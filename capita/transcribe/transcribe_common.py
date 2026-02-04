import datetime
import logging
import os
import json
import textwrap

from google.api_core.client_options import ClientOptions
from google.api_core import exceptions
from google.cloud import speech_v2 as cs
from dotenv import load_dotenv

# --- Global Configuration ---
# Standardizes logging across all demo scripts
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables (Project ID, Location, Model IDs)
load_dotenv()
GCP_PROJECT_ID = os.getenv("PROJECT_ID")
GCP_LOCATION = os.getenv("LOCATION", "us-central1")
GCP_RECOGNIZER_ID = os.getenv("GCP_RECOGNIZER_ID")
GCP_TRANSCRIPTION_MODEL = os.environ.get("GCP_TRANSCRIPTION_MODEL", "telephony")
LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "en-US")
OUTPUT_FILENAME = "output.json"

# Safety check for required credentials
assert GCP_PROJECT_ID, "PROJECT_ID missing in .env"
assert GCP_RECOGNIZER_ID, "GCP_RECOGNIZER_ID missing in .env"

class BaseTranscriptionService:
    """
    Core service containing shared state and UI logic.
    Handles the complexities of real-time terminal display and buffer management.
    """

    def __init__(self, sample_rate: int, channels: int):
        self.sample_rate = sample_rate
        self.channels = channels
        self.transcript_chunks = []
        self.start_time = None
        
        # Audio Session Tracking
        self.restart_offset = 0.0      # Used to maintain timeline continuity after reconnection
        self.current_stream_offset = 0.0 # Tracks playback position within the current stream
        self.current_audio_time = 0.0    # Absolute session playhead position
        
        # UI Styling (ANSI Colors)
        self.COLOR_SPEAKER_1 = "\033[92m" # Green (Caller)
        self.COLOR_SPEAKER_2 = "\033[93m" # Yellow (Agent)
        self.COLOR_DRAFT = "\033[90m"    # Grey (Interim results)
        self.COLOR_RESET = "\033[0m"
        
        # Dynamic Display State
        self.last_printed_channel = None # Tracks which column was last touched
        self.last_was_final = True       # Tracks if the previous line was a draft or permanent
        self.last_line_count = 0         # Number of lines used by the previous print (for clearing)
        self.previous_ts = None          # Used for out-of-order detection (🚨)
        
        # Logic Thresholds (Defaults are 'Low Latency')
        self.STABILITY_THRESHOLD = 0.0   # Hold time for chronological sorting
        self.GAP_THRESHOLD = 0.0         # Threshold for auto-splitting paragraphs
        self.ACTIVE_BLOCKING = False     # Synchronization logic toggle
        
        # Internal Buffers
        self.stability_buffer = []       # Queue for finalized chunks awaiting their timeline slot
        self.active_starts = {1: None, 2: None} # Tracks ongoing speech start times per channel

    def _clear_interim_output(self):
        """Clears the current line. Used primarily by V1 Mono script."""
        print("\r\033[K", end="", flush=True)

    def _print_interim_output(self, text, prefix_label=None):
        """
        Prints interim output on a single line at the bottom.
        Used primarily by V1 Mono script.
        """
        prefix_str = f"{self.COLOR_DRAFT}... {prefix_label + ': ' if prefix_label else ''}"
        full_text = prefix_str + text + self.COLOR_RESET
        
        try:
            term_width = os.get_terminal_size().columns
        except OSError:
            term_width = 80

        # Truncate to avoid wrapping
        if len(full_text) > term_width - 1:
            full_text = full_text[len(full_text) - term_width + 5:] + "..."
            print(f"\r\033[K{full_text}", end= "", flush=True)
        else:
            print(f"\r\033[K{full_text}", end="", flush=True)

    def _split_by_gaps(self, words, channel_tag):
        """
        Sub-segments a long monologue into smaller conversational turns if
        natural pauses (silence) are detected between words.
        """
        if not words or self.GAP_THRESHOLD <= 0:
            return None 
        
        chunks = []
        current_words = [words[0].word]
        current_start = words[0].start_offset.total_seconds()
        
        for i in range(1, len(words)):
            prev_end = words[i-1].end_offset.total_seconds()
            this_start = words[i].start_offset.total_seconds()
            
            # If the silence between words exceeds the threshold, cut the chunk
            if (this_start - prev_end) > self.GAP_THRESHOLD:
                chunks.append({
                    "text": " ".join(current_words), 
                    "start": current_start, 
                    "channel": channel_tag
                })
                current_words, current_start = [words[i].word], this_start
            else:
                current_words.append(words[i].word)
        
        if current_words:
            chunks.append({
                "text": " ".join(current_words), 
                "start": current_start, 
                "channel": channel_tag
            })
        return chunks

    def _process_stability_buffer(self, force_flush=False):
        """
        Core ordering algorithm. Chunks are held until:
        1. The audio playhead has progressed past them (Stability).
        2. No earlier speech is still currently ongoing (Blocking).
        """
        # Determine the earliest possible time we can release (Safety Time)
        active_vals = [v for v in self.active_starts.values() if v is not None]
        min_active_start = min(active_vals) if active_vals else float('inf')
        
        stable, remaining = [], []
        for chunk in self.stability_buffer:
            # Check 1: Has enough time passed to be sure no earlier result will arrive?
            is_stable_time = self.current_audio_time > chunk['start'] + self.STABILITY_THRESHOLD
            
            # Check 2: Synchronization Blocking
            # If this chunk started AFTER some ongoing speech began, we MUST wait for the earlier speech.
            is_blocked = self.ACTIVE_BLOCKING and chunk['start'] > min_active_start + 0.1
            
            if force_flush or (is_stable_time and not is_blocked):
                stable.append(chunk)
            else:
                remaining.append(chunk)
        
        self.stability_buffer = remaining
        
        if stable:
            # Sort the released batch by their absolute start times
            stable.sort(key=lambda x: x['start'])
            for s in stable:
                ts = self.start_time + datetime.timedelta(seconds=s['start'] + self.restart_offset)
                ts_str = ts.strftime("%H:%M:%S.%f")[:-5]
                content = f"[{ts_str}] \"{s['text']}\""
                self._print_in_column(content, s['channel'], is_final=True, ts_only=ts_str)

    def _print_in_column(self, text, channel, is_final, ts_only=None):
        """
        Renders text in a two-column terminal layout with real-time draft overwriting.
        Ensures a smooth, polished UI without duplicate lines.
        """
        # Clear the current interim line before printing
        print("\r\033[K", end="", flush=True)
        
        # SMART OVERWRITE:
        # If the last thing we printed was a draft for THIS specific column,
        # move the cursor up and clear it so the update looks like real-time typing.
        if not self.last_was_final and self.last_printed_channel == channel:
            for _ in range(self.last_line_count):
                print("\033[F\033[K", end="", flush=True)

        # Formatting
        prefix = "" if is_final else "... "
        color = (self.COLOR_SPEAKER_1 if channel == 1 else self.COLOR_SPEAKER_2) if is_final else self.COLOR_DRAFT
        
        # Detection of asynchronous jitter (out-of-order arrival)
        flag = ""
        if is_final and ts_only:
            if self.previous_ts and self.previous_ts > ts_only:
                flag = "\033[91mOut of order: 🚨\033[0m"
            self.previous_ts = ts_only

        full_text = f"{prefix}{flag}{text}"
        colored_content = f"{color}{full_text}{self.COLOR_RESET}"
        
        # Column parameters (Standard terminal width assumption)
        LEFT_COL_WIDTH = 55
        RIGHT_COL_OFFSET = 60
        
        if channel == 1:
            wrapper = textwrap.TextWrapper(width=LEFT_COL_WIDTH, subsequent_indent=" " * 12)
            wrapped = wrapper.fill(colored_content)
        else:
            offset_str = " " * RIGHT_COL_OFFSET
            wrapper = textwrap.TextWrapper(width=115, initial_indent=offset_str, subsequent_indent=offset_str + " " * 12)
            wrapped = wrapper.fill(colored_content)

        print(wrapped, flush=True)
        
        # Store state for the next update
        self.last_was_final = is_final
        self.last_printed_channel = channel
        self.last_line_count = len(wrapped.split("\n"))

    def _get_timestamp(self, result):
        # Use the start offset of the first word to get the beginning of the utterance
        offset = None
        if result.alternatives and result.alternatives[0].words:
            offset = result.alternatives[0].words[0].start_offset
            
        # Fallback to end offset if start offset isn't available
        if not offset:
            offset = getattr(result, "result_end_offset", None)
            
        if not offset and result.alternatives and result.alternatives[0].words:
            offset = result.alternatives[0].words[-1].end_offset
            
        seconds = offset.total_seconds() if offset else 0
        self.current_stream_offset = seconds
        ts = self.start_time + datetime.timedelta(seconds=seconds + self.restart_offset)
        return ts.strftime("%H:%M:%S.%f")[:-5]

class TranscriptionService(BaseTranscriptionService):
    """
    Specialized implementation for Google Cloud Speech-to-Text V2.
    Handles streaming request generation and response consumption.
    """

    def __init__(self, sample_rate: int, channels: int, enable_multi_channel: bool = True, enable_diarization: bool = False, recognizer_id: str = None, model_name: str = None):
        super().__init__(sample_rate, channels)
        self.enable_multi_channel = enable_multi_channel
        self.enable_diarization = enable_diarization
        self.recognizer_id = recognizer_id or GCP_RECOGNIZER_ID
        self.model_name = model_name or GCP_TRANSCRIPTION_MODEL
        self.client = cs.SpeechAsyncClient(
            client_options=ClientOptions(api_endpoint=f"{GCP_LOCATION}-speech.googleapis.com")
        )

    async def get_recognizer(self):
        """Fetches an existing V2 Recognizer or creates one with optimal demo features."""
        parent = f"projects/{GCP_PROJECT_ID}/locations/{GCP_LOCATION}"
        name = f"{parent}/recognizers/{self.recognizer_id}"
        try:
            return await self.client.get_recognizer(name=name)
        except exceptions.NotFound:
            features = cs.RecognitionFeatures(
                enable_word_time_offsets=True,
                enable_automatic_punctuation=True,
            )
            # Diarization is used for Mono files where speakers are mixed on one channel
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
        """Generator that yields binary audio chunks wrapped in V2 API requests."""
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

        # 1. Send the Initial Configuration Request
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

        # 2. Yield the actual binary audio data
        async for chunk in audio_stream:
            yield cs.StreamingRecognizeRequest(audio=chunk)

    async def process_responses(self, stream):
        """Iterates over API results and routes them through the stability logic."""
        try:
            async for response in stream:
                for result in response.results:
                    if not result.alternatives: continue
                    alt = result.alternatives[0]
                    channel_tag = getattr(result, "channel_tag", 1) or 1
                    
                    # Calculate chunk start time
                    if alt.words:
                        start_sec = alt.words[0].start_offset.total_seconds()
                    else:
                        # Fallback for interims without word-level offsets
                        offset = getattr(result, "result_end_offset", None)
                        start_sec = offset.total_seconds() if offset else self.current_audio_time
                    
                    ts = self.start_time + datetime.timedelta(seconds=start_sec + self.restart_offset)
                    ts_str = ts.strftime("%H:%M:%S.%f")[:-5]

                    if not result.is_final:
                        # INTERIM: Current active speech
                        if self.active_starts[channel_tag] is None:
                            self.active_starts[channel_tag] = start_sec
                        
                        # Anti-Jump logic: Don't show a 'future' draft if a 'past' final is waiting
                        if self.STABILITY_THRESHOLD > 0 and self.stability_buffer:
                            if start_sec > min(c['start'] for c in self.stability_buffer) + 0.5:
                                continue

                        self._print_in_column(f"[{ts_str}] \"{alt.transcript}\"", channel_tag, is_final=False)
                        continue
                    
                    # FINAL: Result is fixed
                    self.active_starts[channel_tag] = None
                    
                    # Split monologue turns based on silence gaps
                    sub_chunks = self._split_by_gaps(alt.words, channel_tag)
                    if sub_chunks:
                        for sc in sub_chunks: self.stability_buffer.append(sc)
                    else:
                        self.stability_buffer.append({
                            "text": alt.transcript,
                            "start": start_sec,
                            "channel": channel_tag
                        })
                    
                    # Attempt to release chunks from the buffer
                    self._process_stability_buffer()
        except Exception as e:
            logger.error(f"Response loop encountered an error: {e}")
        finally:
            # Ensure all remaining buffered text is printed before closing
            self._process_stability_buffer(force_flush=True)

    async def run(self, audio_stream):
        """Execution entrypoint. Handles API lifecycle and automatic reconnections."""
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        recognizer = await self.get_recognizer()
        
        logger.info("Service initialized. Awaiting audio...")
        
        # Timer wrapper to track absolute playback time during the stream
        async def stream_with_timer():
            async for chunk in audio_stream:
                self.current_audio_time += 0.25 # Assumes 250ms chunk size from simulator
                yield chunk

        while True:
            try:
                responses_stream = await self.client.streaming_recognize(
                    requests=self.generate_requests(recognizer.name, stream_with_timer())
                )
                await self.process_responses(responses_stream)
                break
            except Exception as e:
                # Automatic recovery for transient network disconnects
                logger.warning(f"Connection lost ({e}). Resuming timeline...")
                self.restart_offset += self.current_stream_offset
                self.current_stream_offset = 0.0

        # Save the finalized conversation history to a JSON file
        self.transcript_chunks.sort(key=lambda x: x['timestamp'] if 'timestamp' in x else x.get('start', 0))
        with open(OUTPUT_FILENAME, "w") as f:
            json.dump(self.transcript_chunks, f, indent=2)
        logger.info(f"Transcription complete. Results saved to {OUTPUT_FILENAME}")