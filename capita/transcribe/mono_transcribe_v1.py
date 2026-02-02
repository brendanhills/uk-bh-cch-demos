import asyncio
import argparse
import datetime
import logging
import os
import io
import textwrap
import time
import difflib

from pydub import AudioSegment
from google.api_core.client_options import ClientOptions
from google.cloud import speech_v1 as speech
from google.cloud.storage import Client as StorageClient
from dotenv import load_dotenv

# --- Configuration & Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
GCP_PROJECT_ID = os.getenv("PROJECT_ID")
GCP_LOCATION = os.getenv("LOCATION", "us") # V1 is global

assert GCP_PROJECT_ID, "Missing PROJECT_ID"

class MonoTranscriptionServiceV1:
    """Service for streaming audio transcription with Google Cloud Speech-to-Text V1."""

    def __init__(self, gcs_uri: str, buffer_timeout: float = 0.5):
        self.gcs_uri = gcs_uri
        self.buffer_timeout = buffer_timeout
        self.client = speech.SpeechAsyncClient()
        self.audio_q = asyncio.Queue()
        self.transcript_chunks = []
        self.start_time = None
        self.stream_finished_flag = False
        self.last_was_heartbeat = False
        
        # Deduplication state
        # Key: speaker_tag, Value: list of (timestamp_float, text) tuples
        self.speaker_history = {} 
        
        # Audio properties
        self.sample_rate = 0
        self.channels = 0
        self.audio_bytes = None
        self.bytes_per_sec = 0

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
        if seg.channels > 1:
            logger.info("Converting to mono for V1 Diarization...")
            seg = seg.set_channels(1)

        self.channels = seg.channels
        self.sample_rate = seg.frame_rate
        self.audio_bytes = seg.set_sample_width(2).raw_data
        self.bytes_per_sec = self.sample_rate * self.channels * 2
        
        logger.info(f"Audio Ready: {self.channels} channel(s), {self.sample_rate} Hz")

    async def stream_audio_chunks(self):
        """Simulates streaming by feeding the queue."""
        chunk_size = 8000 
        chunk_duration = chunk_size / self.bytes_per_sec

        preload_chunks = int(1.0 / chunk_duration)
        chunks_queued = 0

        for i in range(0, len(self.audio_bytes), chunk_size):
            await self.audio_q.put(self.audio_bytes[i:i+chunk_size])
            chunks_queued += 1
            if chunks_queued > preload_chunks:
                await asyncio.sleep(chunk_duration) 
            
        await self.audio_q.put(None) # EOF

    async def generate_requests(self):
        """Yields streaming requests for the V1 API."""
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.sample_rate,
            language_code="en-US",
            diarization_config=speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                min_speaker_count=2,
                max_speaker_count=2,
            ),
            model="phone_call",
            use_enhanced=True,
        )
        
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True
        )

        yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)

        start_time = time.time()
        while True:
            if time.time() - start_time > 240:
                return

            chunk = await self.audio_q.get()
            if chunk is None: 
                self.stream_finished_flag = True
                return
            
            yield speech.StreamingRecognizeRequest(audio_content=chunk)

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
                if not response.results:
                    continue
                
                result = response.results[0]
                if not result.alternatives:
                    continue

                if not result.is_final:
                    print(".", end="", flush=True) 
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
            if flusher: flusher.cancel()
            if buffer: 
                if self.last_was_heartbeat:
                    print("", flush=True)
                    self.last_was_heartbeat = False
                self._process_buffer(buffer)

    def _should_print_chunk(self, chunk):
        """Deduplicates chunks based on history."""
        speaker = chunk['speaker_tag']
        ts = chunk['sort_key'] # Float seconds
        text = chunk['text'].strip()
        
        if speaker not in self.speaker_history:
            self.speaker_history[speaker] = []
            
        history = self.speaker_history[speaker]
        
        # 1. Check current speaker history (last 10 entries) to filter duplicates/regressions
        for i in range(len(history) - 1, max(-1, len(history) - 11), -1):
            prev_ts, prev_text = history[i]
            
            # If timestamp is close (within 0.5s)
            if abs(ts - prev_ts) < 0.5:
                # Case 0: Regression / Exact Match
                if prev_text.startswith(text):
                    return False, None, "IGNORE"

                # Case 1: Extension (new text starts with old text)
                if text.startswith(prev_text):
                    new_part = text[len(prev_text):].strip()
                    if not new_part:
                        return False, None, "IGNORE"
                    
                    history[i] = (ts, text) 
                    chunk['text'] = new_part
                    return True, chunk, "EXTENSION"
                
                # Case 2: Correction / Variant
                history[i] = (ts, text)
                return True, chunk, "CORRECTION"

        # 2. Check other speakers for re-attribution (same text, different speaker)
        # Only check this if it wasn't caught as a duplicate/extension above
        for other_tag, other_hist in self.speaker_history.items():
            if other_tag == speaker: continue
            for p_ts, p_text in other_hist[-10:]:
                # Check for significant overlap using difflib
                matcher = difflib.SequenceMatcher(None, text.lower(), p_text.lower())
                match = matcher.find_longest_match(0, len(text), 0, len(p_text))
                
                # If overlap is significant (e.g., > 20 chars)
                if match.size > 20:
                    # This text (or part of it) was already printed for another speaker!
                    history.append((ts, text))
                    return True, chunk, "RE-ATTRIBUTION"

        # New entry
        history.append((ts, text))
        return True, chunk, "NEW"

    def _print_chunk(self, chunk):
        should_print, mod_chunk, chunk_type = self._should_print_chunk(chunk)
        if not should_print or chunk_type == "IGNORE":
            return

        speaker_tag = mod_chunk.get("speaker_tag", 1)
        text = mod_chunk.get("text", "")
        timestamp = mod_chunk.get("timestamp", "")
        speaker_label = f"Speaker {speaker_tag}"
        
        # Determine prefix based on type
        prefix = ""
        if chunk_type == "CORRECTION":
            prefix = "[CORRECTION] "
        elif chunk_type == "EXTENSION":
            prefix = "... "
        elif chunk_type == "RE-ATTRIBUTION":
            prefix = "[ATTRIBUTION FIX] "
            
        full_content = f'{timestamp} [{speaker_label}] {prefix}"{text}"'
        
        LEFT_COL_WIDTH = 45 
        RIGHT_COL_OFFSET = 60 
        
        if speaker_tag == 1:
            indent_str = " " * 12 
            wrapper = textwrap.TextWrapper(width=LEFT_COL_WIDTH, subsequent_indent=indent_str)
            print(wrapper.fill(full_content), flush=True)
        else:
            offset_str = " " * RIGHT_COL_OFFSET
            wrapper = textwrap.TextWrapper(width=RIGHT_COL_OFFSET + LEFT_COL_WIDTH, 
                                         initial_indent=offset_str, 
                                         subsequent_indent=offset_str + " " * 12)
            print(wrapper.fill(full_content), flush=True)

    def _extract_chunks_from_result(self, result):
        chunks = []
        if not result.alternatives or not result.alternatives[0].words:
            return chunks

        words = result.alternatives[0].words
        current_speaker = words[0].speaker_tag
        current_transcript = []
        current_start_time = words[0].start_time.total_seconds()

        for word in words:
            if word.speaker_tag != current_speaker:
                chunks.append(self._create_chunk_dict(current_speaker, " ".join(current_transcript), current_start_time))
                
                current_speaker = word.speaker_tag
                current_transcript = [word.word]
                current_start_time = word.start_time.total_seconds()
            else:
                current_transcript.append(word.word)
        
        if current_transcript:
            chunks.append(self._create_chunk_dict(current_speaker, " ".join(current_transcript), current_start_time))
            
        return chunks

    def _create_chunk_dict(self, speaker_tag, text, seconds):
        ts = self.start_time + datetime.timedelta(seconds=seconds)
        timestamp = ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-5]
        return {
            "speaker_tag": speaker_tag,
            "text": text,
            "timestamp": timestamp,
            "sort_key": seconds 
        }

    def _process_single_result(self, result):
        chunks = self._extract_chunks_from_result(result)
        for chunk in chunks:
            self.transcript_chunks.append(chunk)
            self._print_chunk(chunk)

    def _process_buffer(self, buffer):
        all_chunks = []
        for result in buffer:
            all_chunks.extend(self._extract_chunks_from_result(result))
        
        all_chunks.sort(key=lambda x: x['sort_key'])
        
        for chunk in all_chunks:
            self._print_chunk(chunk)
            self.transcript_chunks.append(chunk)

    async def run(self, use_buffered=False):
        """Main execution flow."""
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        self.stream_finished_flag = False
        
        await self.prepare_audio()

        if not self.audio_bytes:
            logger.error("No audio data to transcribe!")
            return

        logger.info(f"Starting V1 {'buffered' if use_buffered else 'live'} transcription...")
        
        stream_task = asyncio.create_task(self.stream_audio_chunks())
        await asyncio.sleep(0.5)

        while not self.stream_finished_flag:
            try:
                responses_stream = await self.client.streaming_recognize(
                    requests=self.generate_requests()
                )
                await self.process_responses(responses_stream, use_buffered)
            except Exception as e:
                logger.error(f"Error during streaming_recognize: {e}")
                await asyncio.sleep(1)
        
        await stream_task 

async def main():
    parser = argparse.ArgumentParser(description="Transcribe mono audio with V1 Diarization.")
    parser.add_argument("gcs_uri", help="The GCS URI")
    parser.add_argument('--use-buffered', action='store_true', help='Enable buffered.')
    parser.add_argument('--buffer-timeout', type=float, default=5.0)
    args = parser.parse_args()

    print(f"{'Speaker 1':<60} {'Speaker 2'}")
    print("-" * 100)

    service = MonoTranscriptionServiceV1(args.gcs_uri, args.buffer_timeout)
    await service.run(args.use_buffered)

if __name__ == "__main__":
    asyncio.run(main())
