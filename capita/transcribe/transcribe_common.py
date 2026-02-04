import asyncio
import datetime
import logging
import os
import json
import time
import difflib

from google.api_core.client_options import ClientOptions
from google.api_core import exceptions
from google.cloud import speech_v2 as cs
from dotenv import load_dotenv

# --- Configuration & Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
GCP_PROJECT_ID = os.getenv("PROJECT_ID")
GCP_LOCATION = os.getenv("LOCATION", "us-central1")
GCP_RECOGNIZER_ID = os.getenv("GCP_RECOGNIZER_ID")
GCP_TRANSCRIPTION_MODEL = os.environ.get("GCP_TRANSCRIPTION_MODEL", "telephony")
GCP_MODEL_STEREO = os.environ.get("GCP_MODEL_STEREO", "telephony")
GCP_MODEL_MONO = os.environ.get("GCP_MODEL_MONO", "latest_long")
LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "en-US")
OUTPUT_FILENAME = "output.json"

assert GCP_PROJECT_ID, "Missing PROJECT_ID"
assert GCP_RECOGNIZER_ID, "Missing GCP_RECOGNIZER_ID"

class BaseTranscriptionService:
    """Base Service containing common UI logic and state."""

    def __init__(self, sample_rate: int, channels: int, buffer_timeout: float = 0.5):
        self.sample_rate = sample_rate
        self.channels = channels
        self.buffer_timeout = buffer_timeout
        self.transcript_chunks = []
        self.full_text = ""
        self.start_time = None
        self.stream_finished_flag = False
        self.last_was_heartbeat = False
        
        # Audio properties
        self.restart_offset = 0.0
        
        # UI / Display State
        self.COLOR_SPEAKER_1 = "\033[92m" # Green
        self.COLOR_SPEAKER_2 = "\033[93m" # Yellow/Orange
        self.COLOR_RESET = "\033[0m"
        self.last_interim_text = ""
        self.last_interim_prefix = None
        
        # Deduplication state (V1 legacy)
        self.speaker_history = {} 

    def _clear_interim_output(self):
        """Clears the current line."""
        print("\r\033[K", end="", flush=True)

    def _print_interim_output(self, text, prefix_label=None):
        """Prints interim output on a single line."""
        prefix_str = "... "
        full_text = prefix_str + text
        try:
            term_width = os.get_terminal_size().columns
        except OSError:
            term_width = 80
        if len(full_text) > term_width - 1:
            full_text = full_text[:term_width - 4] + "..."
        print(f"\r{full_text}", end="", flush=True)

    def _should_print_chunk(self, chunk):
        """Deduplicates chunks based on history."""
        speaker = chunk.get('speaker', 'Unknown')
        ts = chunk.get('timestamp_float', 0.0)
        text = chunk.get('text', '').strip()
        
        if speaker not in self.speaker_history:
            self.speaker_history[speaker] = []
        history = self.speaker_history[speaker]
        
        for i in range(len(history) - 1, max(-1, len(history) - 11), -1):
            prev_ts, prev_text = history[i]
            if abs(ts - prev_ts) < 0.5:
                if prev_text.startswith(text): return False, None, "IGNORE"
                if text.startswith(prev_text):
                    new_part = text[len(prev_text):].strip()
                    if not new_part: return False, None, "IGNORE"
                    history[i] = (ts, text) 
                    chunk['text'] = new_part
                    return True, chunk, "EXTENSION"
                history[i] = (ts, text)
                return True, chunk, "CORRECTION"

        for other_tag, other_hist in self.speaker_history.items():
            if other_tag == speaker: continue
            for p_ts, p_text in other_hist[-10:]:
                matcher = difflib.SequenceMatcher(None, text.lower(), p_text.lower())
                match = matcher.find_longest_match(0, len(text), 0, len(p_text))
                if match.size > 10:
                    history.append((ts, text))
                    return True, chunk, "RE-ATTRIBUTION"

        history.append((ts, text))
        return True, chunk, "NEW"

    def _get_timestamp(self, result):
        offset = getattr(result, "result_end_offset", None)
        if not offset and result.alternatives and result.alternatives[0].words:
            offset = result.alternatives[0].words[-1].end_offset
        seconds = offset.total_seconds() if offset else 0
        ts = self.start_time + datetime.timedelta(seconds=seconds + self.restart_offset)
        return ts.strftime("%H:%M:%S.%f")[:-5]

class TranscriptionService(BaseTranscriptionService):
    """Service for streaming audio transcription with Google Cloud Speech-to-Text V2."""

    def __init__(self, sample_rate: int, channels: int, buffer_timeout: float = 0.5, enable_multi_channel: bool = True, enable_diarization: bool = False, recognizer_id: str = None, model_name: str = None):
        super().__init__(sample_rate, channels, buffer_timeout)
        self.enable_multi_channel = enable_multi_channel
        self.enable_diarization = enable_diarization
        self.recognizer_id = recognizer_id or GCP_RECOGNIZER_ID
        self.model_name = model_name or GCP_TRANSCRIPTION_MODEL
        self.client = cs.SpeechAsyncClient(
            client_options=ClientOptions(api_endpoint=f"{GCP_LOCATION}-speech.googleapis.com")
        )

    async def get_recognizer(self):
        """Gets or creates the Speech V2 Recognizer."""
        parent = f"projects/{GCP_PROJECT_ID}/locations/{GCP_LOCATION}"
        name = f"{parent}/recognizers/{self.recognizer_id}"
        try:
            return await self.client.get_recognizer(name=name)
        except exceptions.NotFound:
            features = cs.RecognitionFeatures(
                enable_word_time_offsets=True,
                enable_automatic_punctuation=True,
            )
            if self.enable_diarization:
                features.diarization_config = cs.SpeakerDiarizationConfig(min_speaker_count=2, max_speaker_count=2)

            request = cs.CreateRecognizerRequest(
                parent=parent,
                recognizer_id=self.recognizer_id,
                recognizer=cs.Recognizer(
                    default_recognition_config=cs.RecognitionConfig(
                        language_codes=[LANGUAGE_CODE], 
                        model=self.model_name,
                        features=features,
                    ),
                ),
            )
            op = await self.client.create_recognizer(request=request)
            return await op.result()

    async def generate_requests(self, recognizer_name, audio_stream):
        """Yields streaming requests for the API."""
        if self.channels > 1 and self.enable_multi_channel:
             mc_mode = cs.RecognitionFeatures.MultiChannelMode.SEPARATE_RECOGNITION_PER_CHANNEL
        else:
             mc_mode = cs.RecognitionFeatures.MultiChannelMode.MULTI_CHANNEL_MODE_UNSPECIFIED
        
        features = cs.RecognitionFeatures(
            multi_channel_mode=mc_mode,
            enable_word_time_offsets=True,
            enable_automatic_punctuation=True,
        )
        
        if self.enable_diarization:
            features.diarization_config = cs.SpeakerDiarizationConfig(min_speaker_count=2, max_speaker_count=2)

        yield cs.StreamingRecognizeRequest(
            recognizer=recognizer_name,
            streaming_config=cs.StreamingRecognitionConfig(
                config=cs.RecognitionConfig(
                    explicit_decoding_config=cs.ExplicitDecodingConfig(
                        encoding=cs.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
                        sample_rate_hertz=self.sample_rate,
                        audio_channel_count=self.channels,
                    ),
                    features=features,
                    language_codes=[LANGUAGE_CODE],
                    model=self.model_name,
                ),
                streaming_features=cs.StreamingRecognitionFeatures(interim_results=True)
            ),
        )

        async for chunk in audio_stream:
            yield cs.StreamingRecognizeRequest(audio=chunk)

    async def process_responses(self, stream, use_buffered=False):
        """Consumes responses from the API."""
        buffer = []
        async def flush_buffer_loop():
            while True:
                await asyncio.sleep(self.buffer_timeout)
                if buffer:
                    if self.last_was_heartbeat:
                        print("", flush=True)
                        self.last_was_heartbeat = False
                    self._process_buffer(buffer)
                    buffer.clear()

        flusher = asyncio.create_task(flush_buffer_loop()) if use_buffered else None

        try:
            async for response in stream:
                for result in response.results:
                    if not result.alternatives: continue
                    if not result.is_final:
                        text = result.alternatives[0].transcript
                        tag = getattr(result, "channel_tag", "?")
                        label = f"Ch{tag}"
                        self._print_interim_output(text, label)
                        self.last_was_heartbeat = True
                        continue
                    
                    self._clear_interim_output()
                    if not use_buffered:
                        if self.last_was_heartbeat: self.last_was_heartbeat = False
                        self._process_single_result(result)
                    else:
                        buffer.append(result)
        finally:
            if flusher: flusher.cancel()
            self._clear_interim_output()
            if buffer:
                if self.last_was_heartbeat: self.last_was_heartbeat = False
                self._process_buffer(buffer)

    def _process_single_result(self, result):
        if not result.alternatives: return 
        transcript = result.alternatives[0].transcript
        self.full_text += f"\n{transcript}"
        chunk = self._create_transcript_chunk(result)
        self.transcript_chunks.append(chunk)
        self._print_chunk(chunk)

    def _process_buffer(self, buffer):
        temp_chunks = []
        for result in buffer:
            if not result.alternatives: continue
            self.full_text += f"\n{result.alternatives[0].transcript}"
            temp_chunks.append(self._create_transcript_chunk(result))
        temp_chunks.sort(key=lambda x: x['timestamp'])
        for chunk in temp_chunks:
            self._print_chunk(chunk)
        self.transcript_chunks.extend(temp_chunks)

    def _create_transcript_chunk(self, result):
        raise NotImplementedError

    def _should_print_chunk(self, chunk):
        return True, chunk, "NEW"

    def _print_chunk(self, chunk):
        speaker = chunk.get("speaker", "Speaker")
        text = chunk.get("text", "")
        timestamp = chunk.get("timestamp", "")
        print(f"[{timestamp}] {speaker: <10}: {text}", flush=True)

    async def run(self, audio_stream, use_buffered=False):
        """Main execution flow."""
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        recognizer = await self.get_recognizer()
        
        logger.info(f"Starting {'buffered' if use_buffered else 'live'} transcription...")
        
        try:
            responses_stream = await self.client.streaming_recognize(
                requests=self.generate_requests(recognizer.name, audio_stream)
            )
            await self.process_responses(responses_stream, use_buffered)
        except Exception as e:
            logger.error(f"Error during streaming_recognize: {e}")

        self.transcript_chunks.sort(key=lambda x: x['timestamp'])
        with open(OUTPUT_FILENAME, "w") as f:
            json.dump(self.transcript_chunks, f, indent=2)
        logger.info(f"Done. Saved to {OUTPUT_FILENAME}")
