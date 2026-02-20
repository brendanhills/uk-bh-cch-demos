import datetime
import logging
import os
import json
import textwrap
import asyncio

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
        self.last_vad_start = None       # Fallback for untagged VAD events
        self.vad_queue = []              # Queue of untagged VAD start times

        # File Logging
        self.log_file = None

    def set_log_file(self, file_path):
        """Sets a file to mirror the columnar output (without ANSI colors)."""
        self.log_file = open(file_path, "w")

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
                    "end": prev_end,
                    "channel": channel_tag
                })
                current_words, current_start = [words[i].word], this_start
            else:
                current_words.append(words[i].word)
        
        if current_words:
            chunks.append({
                "text": " ".join(current_words), 
                "start": current_start, 
                "end": words[-1].end_offset.total_seconds(),
                "channel": channel_tag
            })
        return chunks

    def _split_by_punctuation(self, text, channel_tag, start_sec, end_sec):
        """
        Fallback for models without word timestamps. Splits a block of text
        by sentence boundaries to improve readability.
        """
        import re
        # Split by . ! ? followed by space or end of string
        parts = re.split(r'(?<=[.!?]) +', text.strip())
        if len(parts) <= 1:
            return None
            
        chunks = []
        # Ensure at least 0.5s duration for the estimation to work visually
        duration = max(0.5, end_sec - start_sec)
        
        for i, p in enumerate(parts):
            # Sequenced timing: [0.0, 0.1, 0.2] etc if duration is near zero
            p_start = start_sec + (i * (duration / len(parts)))
            p_end = start_sec + ((i + 0.9) * (duration / len(parts))) # Small gap
            chunks.append({
                "text": p,
                "start": p_start,
                "end": p_end,
                "channel": channel_tag
            })
        return chunks

    def _process_stability_buffer(self, force_flush=False):
        """
        Core ordering algorithm. Chunks are held until:
        1. The audio playhead has progressed past them (Stability).
        2. No earlier speech is still currently ongoing (Blocking).
        """
        stable, remaining = [], []
        for chunk in self.stability_buffer:
            # Check 1: Has enough time passed to be sure no earlier result will arrive?
            is_stable_time = self.current_audio_time > chunk['start'] + self.STABILITY_THRESHOLD
            
            # Check 2: Synchronization Blocking
            is_blocked = False
            if self.ACTIVE_BLOCKING:
                for ch, start in self.active_starts.items():
                    if ch != chunk['channel'] and start is not None:
                        # Only block if the OTHER person started significantly BEFORE this chunk
                        # We use 0.5s as a 'near-simultaneous' window.
                        if start < chunk['start'] - 0.5:
                            # SAFETY: If we've been holding this chunk for a while, release it anyway
                            # to avoid the 'Channel 1 blocks Channel 2 for 20 seconds' effect.
                            wait_time = self.current_audio_time - chunk['start']
                            if wait_time < 2.0: # 2s max hold
                                is_blocked = True
                                break
            
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
                
                # SAVE DATA FOR PERMANENCE
                s['timestamp'] = ts_str
                self.transcript_chunks.append(s)
                
                rel_start = f"{s['start']:05.1f}s"
                rel_end = f"{s.get('end', s['start']):05.1f}s"
                
                if rel_start != rel_end:
                    content = f"[{rel_start}] \"{s['text']}\" [{rel_end}]"
                else:
                    content = f"[{rel_start}] \"{s['text']}\""
                    
                self._print_in_column(content, s['channel'], is_final=True, ts_only=ts_str)

    def _print_in_column(self, text, channel, is_final, ts_only=None):
        """
        Renders text in a multi-column terminal layout with real-time draft overwriting.
        Supports up to 4 columns for comparative demos.
        """
        # SMART OVERWRITE:
        # If the last thing we printed was a draft for THIS specific column,
        # move the cursor up and clear it so the update looks like real-time typing.
        if not self.last_was_final and self.last_printed_channel == channel:
            for _ in range(self.last_line_count):
                print("\033[F\033[K", end="", flush=True)

        # Formatting
        prefix = "" if is_final else "... "
        # Cycle colors for 4 channels
        colors = [self.COLOR_SPEAKER_1, self.COLOR_SPEAKER_2, self.COLOR_SPEAKER_1, self.COLOR_SPEAKER_2]
        color = colors[channel-1] if is_final else self.COLOR_DRAFT
        
        # Detection of asynchronous jitter (out-of-order arrival)
        flag = ""
        if is_final and ts_only:
            if self.previous_ts and self.previous_ts > ts_only:
                flag = "\033[91mOut of order: 🚨\033[0m"
            self.previous_ts = ts_only

        full_text = f"{prefix}{flag}{text}"
        colored_content = f"{color}{full_text}{self.COLOR_RESET}"
        
        # Column parameters (Assumes a wide terminal for 4-column layout)
        COL_WIDTH = 38
        COL_SPACING = 2
        
        offset_str = " " * ((channel - 1) * (COL_WIDTH + COL_SPACING))
        # Total width for wrapping logic
        TOTAL_WIDTH = offset_str.__len__() + COL_WIDTH
        
        wrapper = textwrap.TextWrapper(
            width=TOTAL_WIDTH, 
            initial_indent=offset_str, 
            subsequent_indent=offset_str + " " * 4
        )
        wrapped = wrapper.fill(colored_content)

        print(wrapped, flush=True)

        # Mirror to log file (plain text)
        if is_final and self.log_file:
            # We strip the flag and colors for the log file
            plain_text = f"{prefix}{text}"
            wrapped_plain = textwrap.TextWrapper(
                width=TOTAL_WIDTH, 
                initial_indent=offset_str, 
                subsequent_indent=offset_str + " " * 4
            ).fill(plain_text)
            self.log_file.write(wrapped_plain + "\n")
            self.log_file.flush()
        
        # Store state for the next update
        self.last_was_final = is_final
        self.last_printed_channel = channel
        self.last_line_count = len(wrapped.split("\n"))

    def _print_event(self, text, channel=None):
        """Prints a non-transcript event marker (e.g. VAD) in the columns."""
        # Dimmed grey for events
        color = "\033[90m"
        reset = "\033[0m"
        content = f"{color}<{text}>{reset}"
        
        COL_WIDTH = 38
        COL_SPACING = 2
        
        if channel:
            offset_str = " " * ((channel - 1) * (COL_WIDTH + COL_SPACING))
            print(f"{offset_str}{content}", flush=True)
        else:
            # Center the event between the columns
            offset_str = " " * ((COL_WIDTH + COL_SPACING) // 2)
            print(f"{offset_str}{content}", flush=True)
        
        self.last_was_final = True # Reset draft state
        self.last_line_count = 1

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

class ComparisonManager:
    """
    Coordinates multiple TranscriptionService instances.
    Distributes a single audio stream to all registered services.
    """
    def __init__(self, services: list["TranscriptionService"]):
        self.services = services

    async def run(self, audio_stream):
        """Distributes the audio stream to all registered services in parallel."""
        # Create a queue for each service to receive audio chunks
        queues = [asyncio.Queue() for _ in self.services]

        # Generator for each service that reads from its dedicated queue
        async def queue_to_stream(queue):
            while True:
                chunk = await queue.get()
                if chunk is None:
                    break
                yield chunk

        # Start all services in parallel
        tasks = []
        for i, service in enumerate(self.services):
            tasks.append(asyncio.create_task(service.run(queue_to_stream(queues[i]))))

        # Distribute chunks from the main audio_stream to all queues
        try:
            async for chunk in audio_stream:
                for q in queues:
                    await q.put(chunk)
        finally:
            # Signal all services to shut down
            for q in queues:
                await q.put(None)
            
            # Wait for all transcription tasks to complete
            await asyncio.gather(*tasks)

class TranscriptionService(BaseTranscriptionService):
    """
    Specialized implementation for Google Cloud Speech-to-Text V2.
    Handles streaming request generation and response consumption.
    """

    def __init__(self, sample_rate: int, channels: int, enable_multi_channel: bool = True, enable_diarization: bool = False, recognizer_id: str = None, model_name: str = None, duration: float = None):
        super().__init__(sample_rate, channels)
        self.enable_multi_channel = enable_multi_channel
        self.enable_diarization = enable_diarization
        self.recognizer_id = recognizer_id or GCP_RECOGNIZER_ID
        self.model_name = model_name or GCP_TRANSCRIPTION_MODEL
        self.duration = duration
        
        # Determine API endpoint based on model (Chirp requires global/us/eu)
        location = GCP_LOCATION
        endpoint = f"{location}-speech.googleapis.com"
        if "chirp" in self.model_name.lower():
            location = "us" # Default to 'us' for Chirp
            endpoint = "us-speech.googleapis.com"
            self.CHIRP_MODE = True
        else:
            self.CHIRP_MODE = False

        self.client = cs.SpeechAsyncClient(
            client_options=ClientOptions(api_endpoint=endpoint)
        )
        self.api_location = location

    async def get_recognizer(self):
        """Fetches an existing V2 Recognizer or creates one with optimal demo features."""
        parent = f"projects/{GCP_PROJECT_ID}/locations/{self.api_location}"
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
        # Chirp 3 does not support word timestamps in streaming mode
        enable_word_offsets = not self.CHIRP_MODE

        # Chirp 3 does not support diarization in streaming mode
        enable_diarization = self.enable_diarization and not self.CHIRP_MODE
        
        if self.channels > 1 and self.enable_multi_channel and not enable_diarization:
             mc_mode = cs.RecognitionFeatures.MultiChannelMode.SEPARATE_RECOGNITION_PER_CHANNEL
             audio_channel_count = self.channels
        else:
             # Diarization (if supported) requires single channel mode
             mc_mode = cs.RecognitionFeatures.MultiChannelMode.MULTI_CHANNEL_MODE_UNSPECIFIED
             audio_channel_count = 1 if enable_diarization else self.channels
        
        features = cs.RecognitionFeatures(
            multi_channel_mode=mc_mode,
            enable_word_time_offsets=enable_word_offsets,
            enable_automatic_punctuation=True,
        )
        
        if enable_diarization:
            features.diarization_config = cs.SpeakerDiarizationConfig(min_speaker_count=2, max_speaker_count=2)

        # 1. Send the Initial Configuration Request
        yield cs.StreamingRecognizeRequest(
            recognizer=recognizer_name,
            streaming_config=cs.StreamingRecognitionConfig(
                config=cs.RecognitionConfig(
                    explicit_decoding_config=cs.ExplicitDecodingConfig(
                        encoding=cs.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
                        sample_rate_hertz=self.sample_rate,
                        audio_channel_count=audio_channel_count,
                    ),
                    features=features,
                    language_codes=[LANGUAGE_CODE],
                    model=self.model_name,
                ),
                streaming_features=cs.StreamingRecognitionFeatures(
                    interim_results=True,
                    enable_voice_activity_events=True
                    )
            ),
        )

        # 2. Yield the actual binary audio data
        async for chunk in audio_stream:
            # Chirp models have a smaller max chunk size (approx 25KB)
            if self.CHIRP_MODE and len(chunk) > 25000:
                for i in range(0, len(chunk), 25000):
                    yield cs.StreamingRecognizeRequest(audio=chunk[i:i+25000])
            else:
                yield cs.StreamingRecognizeRequest(audio=chunk)

    async def process_responses(self, stream):
        """Iterates over API results and routes them through the stability logic."""
        try:
            async for response in stream:
                # Handle Voice Activity Events
                if response.speech_event_type:
                    event_type = cs.StreamingRecognizeResponse.SpeechEventType(response.speech_event_type)
                    event_name = event_type.name
                    
                    event_offset = response.speech_event_offset.total_seconds() if response.speech_event_offset else self.current_audio_time

                    # Suppress 'end of test' artifact storms
                    if self.duration and event_offset >= self.duration - 0.5:
                        continue

                    if event_type in [cs.StreamingRecognizeResponse.SpeechEventType.SPEECH_ACTIVITY_BEGIN, 
                                      cs.StreamingRecognizeResponse.SpeechEventType.SPEECH_ACTIVITY_END]:
                        
                        # Attribution: Check metadata first, then results
                        event_channel = None
                        if hasattr(response, "metadata") and getattr(response.metadata, "channel_tag", 0) > 0:
                            event_channel = response.metadata.channel_tag
                        elif response.results:
                            event_channel = getattr(response.results[0], "channel_tag", 1)
                        
                        rel_ts = f"{event_offset:05.1f}s"
                        self._print_event(f"{event_name} @ {rel_ts}", channel=event_channel)
                        
                        if event_type == cs.StreamingRecognizeResponse.SpeechEventType.SPEECH_ACTIVITY_BEGIN:
                             self.last_vad_start = event_offset
                             self.vad_queue.append(event_offset)
                             if event_channel:
                                 self.active_starts[event_channel] = event_offset
                        elif event_type == cs.StreamingRecognizeResponse.SpeechEventType.SPEECH_ACTIVITY_END:
                             if event_channel:
                                 self.active_starts[event_channel] = None
                             else:
                                 # Clear both if unknown to be safe
                                 self.active_starts[1] = self.active_starts[2] = None

                for result in response.results:
                    if not result.alternatives: continue
                    alt = result.alternatives[0]
                    
                    # Attribution: Use speaker_tag if diarization is on, otherwise channel_tag
                    speaker_tag = getattr(result, "channel_tag", 1) or 1
                    if self.enable_diarization and alt.words:
                        speaker_tag = alt.words[0].speaker_tag
                    
                    # Calculate chunk start/end times
                    if alt.words:
                        start_sec = alt.words[0].start_offset.total_seconds()
                        end_sec = alt.words[-1].end_offset.total_seconds()
                    else:
                        # Fallback for models without word offsets (Chirp 3)
                        end_offset = getattr(result, "result_end_offset", None)
                        end_sec = end_offset.total_seconds() if end_offset else self.current_audio_time
                        
                        # Try to find the matching VAD start
                        start_sec = self.active_starts.get(speaker_tag)
                        if start_sec is None:
                             # Pop from queue if available
                             start_sec = self.vad_queue.pop(0) if self.vad_queue else self.last_vad_start
                        
                        start_sec = start_sec or end_sec
                        # Clear the global fallback once consumed
                        self.last_vad_start = None
                    
                    ts = self.start_time + datetime.timedelta(seconds=start_sec + self.restart_offset)
                    ts_str = ts.strftime("%H:%M:%S.%f")[:-5]

                    if not result.is_final:
                        # INTERIM: Current active speech
                        if self.active_starts.get(speaker_tag) is None:
                            self.active_starts[speaker_tag] = start_sec
                        
                        # Anti-Jump logic: Don't show a 'future' draft if a 'past' final is waiting
                        if self.STABILITY_THRESHOLD > 0 and self.stability_buffer:
                            if start_sec > min(c['start'] for c in self.stability_buffer) + 0.5:
                                continue

                        rel_ts = f"{start_sec:05.1f}s"
                        self._print_in_column(f"[{rel_ts}] \"{alt.transcript}\"", speaker_tag, is_final=False)
                        continue
                    
                    # FINAL: Result is fixed
                    self.active_starts[speaker_tag] = None
                    
                    # Split monologue turns based on silence gaps (requires word offsets)
                    sub_chunks = self._split_by_gaps(alt.words, speaker_tag)
                    
                    # FALLBACK: If no word offsets (Chirp 3), split by sentence punctuation
                    if not sub_chunks and not alt.words:
                        sub_chunks = self._split_by_punctuation(alt.transcript, speaker_tag, start_sec, end_sec)

                    if sub_chunks:
                        for sc in sub_chunks: self.stability_buffer.append(sc)
                    else:
                        self.stability_buffer.append({
                            "text": alt.transcript,
                            "start": start_sec,
                            "end": end_sec,
                            "channel": speaker_tag
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
        
        # Reset relative stream timer
        self.current_audio_time = 0.0

        async def stream_with_timer():
            chunks_sent = 0
            async for chunk in audio_stream:
                chunks_sent += 1
                # Each chunk is approx 250ms
                self.current_audio_time = chunks_sent * 0.25 
                yield chunk

        while True:
            try:
                responses_stream = await self.client.streaming_recognize(
                    requests=self.generate_requests(recognizer.name, stream_with_timer())
                )
                await self.process_responses(responses_stream)
                break
            except Exception as e:
                logger.warning(f"Connection lost ({e}). Resuming timeline...")
                self.restart_offset += self.current_stream_offset
                self.current_stream_offset = 0.0

        # Save standardized JSON results
        # We ensure chunks are sorted by start_sec for consistency
        self.transcript_chunks.sort(key=lambda x: x.get('start_sec', x.get('start', 0)))
        
        output_data = []
        for c in self.transcript_chunks:
            output_data.append({
                "timestamp": c.get('timestamp'),
                "start_sec": c.get('start_sec', c.get('start', 0)),
                "speaker": c.get('speaker', c.get('channel', 1)),
                "text": c.get('text')
            })

        with open(OUTPUT_FILENAME, "w") as f:
            json.dump(output_data, f, indent=2)
        logger.info(f"Transcription complete. Results saved to {OUTPUT_FILENAME}")
        
        if self.log_file:
            self.log_file.close()
    