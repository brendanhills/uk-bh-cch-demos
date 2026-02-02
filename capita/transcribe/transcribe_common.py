import asyncio
import datetime
import logging
import os
import io
import json
import time

from pydub import AudioSegment
from google.api_core.client_options import ClientOptions
from google.api_core import exceptions
from google.cloud import speech_v2 as cs
from google.cloud.storage import Client as StorageClient
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

class TranscriptionService:
    """Base Service for streaming audio transcription with Google Cloud Speech-to-Text V2."""

    def __init__(self, gcs_uri: str, buffer_timeout: float = 0.5, enable_multi_channel: bool = True, enable_diarization: bool = False, recognizer_id: str = None, model_name: str = None):
        self.gcs_uri = gcs_uri
        self.buffer_timeout = buffer_timeout
        self.enable_multi_channel = enable_multi_channel
        self.enable_diarization = enable_diarization
        self.recognizer_id = recognizer_id or GCP_RECOGNIZER_ID
        self.model_name = model_name or GCP_TRANSCRIPTION_MODEL
        self.client = cs.SpeechAsyncClient(
            client_options=ClientOptions(api_endpoint=f"{GCP_LOCATION}-speech.googleapis.com")
        )
        self.audio_q = asyncio.Queue()
        self.transcript_chunks = []
        self.full_text = ""
        self.start_time = None
        self.stream_finished_flag = False
        self.last_was_heartbeat = False
        
        # Audio properties
        self.sample_rate = 0
        self.channels = 0
        self.audio_bytes = None
        self.bytes_per_sec = 0
        self.restart_offset = 0.0
        self.current_stream_bytes_sent = 0

    async def prepare_audio(self):
        """Downloads audio and determines properties (Rate, Channels)."""
        logger.info(f"Downloading audio from {self.gcs_uri}...")
        storage = StorageClient()
        bucket_name, blob_name = self.gcs_uri.replace("gs://", "").split("/", 1)
        bucket = storage.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        raw_audio = blob.download_as_bytes()
        storage.close()

        seg = AudioSegment.from_file(io.BytesIO(raw_audio))
        if seg.channels == 2:
            left, right = seg.split_to_mono()
            if left.raw_data == right.raw_data:
                logger.info("Stereo file detected with identical channels. Treating as mono.")
                seg = seg.set_channels(1)

        self.channels = seg.channels
        self.sample_rate = seg.frame_rate
        self.audio_bytes = seg.set_sample_width(2).raw_data
        
        # Calculate bytes per second
        self.bytes_per_sec = self.sample_rate * self.channels * 2
        
        logger.info(f"Audio Ready: {self.channels} channel(s), {self.sample_rate} Hz")

    async def get_recognizer(self):
        """Gets or creates the Speech V2 Recognizer."""
        parent = f"projects/{GCP_PROJECT_ID}/locations/{GCP_LOCATION}"
        name = f"{parent}/recognizers/{self.recognizer_id}"
        
        try:
            logger.info(f"Checking for recognizer: {self.recognizer_id}")
            return await self.client.get_recognizer(name=name)
        except exceptions.NotFound:
            logger.info(f"Recognizer '{self.recognizer_id}' not found. Creating new one...")
            
            # Build default features
            features = cs.RecognitionFeatures(
                enable_word_time_offsets=True,
                enable_automatic_punctuation=True,
            )
            if self.enable_diarization:
                features.diarization_config = cs.SpeakerDiarizationConfig(
                    min_speaker_count=2,
                    max_speaker_count=2
                )

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

    async def stream_audio_chunks(self):
        """Simulates streaming by feeding the queue."""
        chunk_size = 8000 # Bytes per chunk
        chunk_duration = chunk_size / self.bytes_per_sec

        # Pre-load 1 second of audio to prime the stream
        preload_chunks = int(1.0 / chunk_duration)
        chunks_queued = 0

        for i in range(0, len(self.audio_bytes), chunk_size): # type: ignore
            await self.audio_q.put(self.audio_bytes[i:i+chunk_size]) # type: ignore
            chunks_queued += 1
            if chunks_queued > preload_chunks:
                await asyncio.sleep(chunk_duration) 
            
        await self.audio_q.put(None) # EOF

    async def generate_requests(self, recognizer_name):
        """Yields streaming requests for the API."""
        # 1. Configuration Request
        if self.channels > 1 and self.enable_multi_channel:
             mc_mode = cs.RecognitionFeatures.MultiChannelMode.SEPARATE_RECOGNITION_PER_CHANNEL
        else:
             mc_mode = cs.RecognitionFeatures.MultiChannelMode.MULTI_CHANNEL_MODE_UNSPECIFIED
        
        print("", flush=True)
        logger.debug(f"Yielding config (mc_mode={mc_mode.name})")
        
        # Configure features
        features = cs.RecognitionFeatures(
            multi_channel_mode=mc_mode,
            enable_word_time_offsets=True,
            enable_automatic_punctuation=True,
        )
        
        if self.enable_diarization:
            features.diarization_config = cs.SpeakerDiarizationConfig(
                min_speaker_count=2,
                max_speaker_count=2
            )

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
                streaming_features=cs.StreamingRecognitionFeatures(
                    interim_results=True
                )
            ),
        )

        # 2. Audio Data Requests
        start_time = time.time()
        while True:
            # Check for stream time limit (restart every 240s)
            if time.time() - start_time > 240:
                print("", flush=True)
                logger.info("Restarting Stream")
                return

            chunk = await self.audio_q.get()
            if chunk is None: 
                self.stream_finished_flag = True
                print("", flush=True)
                logger.info("Stream finished.")
                return
            
            self.current_stream_bytes_sent += len(chunk)
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
                    if not result.is_final:
                        # Print channel-specific heartbeat
                        tag = getattr(result, "channel_tag", None)
                        char = str(tag) if tag in [1, 2] else "."
                        print(char, end="", flush=True) 
                        self.last_was_heartbeat = True
                        continue
                    
                    if not use_buffered:
                        if self.last_was_heartbeat:
                            print("", flush=True)
                            self.last_was_heartbeat = False
                        self._process_single_result(result)
                    else:
                        buffer.append(result)
        finally:
            if flusher: 
                flusher.cancel()
            if buffer: 
                if self.last_was_heartbeat:
                    print("", flush=True)
                    self.last_was_heartbeat = False
                self._process_buffer(buffer)

    def _print_chunk(self, chunk):
        """Prints a single transcript chunk to the console."""
        speaker = chunk.get("speaker", "Speaker")
        text = chunk.get("text", "")
        timestamp = chunk.get("timestamp", "")
        print(f"[{timestamp}] {speaker: <10}: {text}", flush=True)

    def _process_single_result(self, result):
        if not result.alternatives: return  # noqa: E701
        transcript = result.alternatives[0].transcript
        self.full_text += f"\n{transcript}"
        
        chunk = self._create_transcript_chunk(result)
        self.transcript_chunks.append(chunk)
        self._print_chunk(chunk)

    def _process_buffer(self, buffer):
        temp_chunks = []
        for result in buffer:
            if not result.alternatives: continue  # noqa: E701
            self.full_text += f"\n{result.alternatives[0].transcript}"
            temp_chunks.append(self._create_transcript_chunk(result))
        
        temp_chunks.sort(key=lambda x: x['timestamp'])
        for chunk in temp_chunks:
            self._print_chunk(chunk)
        self.transcript_chunks.extend(temp_chunks)

    def _create_transcript_chunk(self, result):
        raise NotImplementedError

    def _get_timestamp(self, result):
        offset = getattr(result, "result_end_offset", None)
        if not offset and result.alternatives and result.alternatives[0].words:
            offset = result.alternatives[0].words[-1].end_offset
            
        seconds = offset.total_seconds() if offset else 0
        ts = self.start_time + datetime.timedelta(seconds=seconds + self.restart_offset)
        return ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-5]

    async def run(self, use_buffered=False):
        """Main execution flow."""
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        self.stream_finished_flag = False
        
        recognizer = await self.get_recognizer()
        await self.prepare_audio()

        if not self.audio_bytes:
            logger.error("No audio data to transcribe!")
            return

        logger.info(f"Starting {'buffered' if use_buffered else 'live'} transcription...")
        
        stream_task = asyncio.create_task(self.stream_audio_chunks())
        await asyncio.sleep(0.5)

        while not self.stream_finished_flag:
            self.current_stream_bytes_sent = 0
            try:
                responses_stream = await self.client.streaming_recognize(
                    requests=self.generate_requests(recognizer.name)
                )
                await self.process_responses(responses_stream, use_buffered)
            except Exception as e:
                logger.error(f"Error during streaming_recognize: {e}")
                await asyncio.sleep(1)
            
            if self.bytes_per_sec > 0:
                self.restart_offset += self.current_stream_bytes_sent / self.bytes_per_sec
        
        await stream_task 

        self.transcript_chunks.sort(key=lambda x: x['timestamp'])
        with open(OUTPUT_FILENAME, "w") as f:
            json.dump(self.transcript_chunks, f, indent=2)
        
        logger.info(f"Done. Saved to {OUTPUT_FILENAME}")
