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
LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "en-US")
OUTPUT_FILENAME = "output.json"

assert GCP_PROJECT_ID, "Missing PROJECT_ID"
assert GCP_RECOGNIZER_ID, "Missing GCP_RECOGNIZER_ID"

class TranscriptionService:
    """Base Service for streaming audio transcription with Google Cloud Speech-to-Text V2."""

    def __init__(self, gcs_uri: str, buffer_timeout: float = 0.5, enable_multi_channel: bool = True):
        self.gcs_uri = gcs_uri
        self.buffer_timeout = buffer_timeout
        self.enable_multi_channel = enable_multi_channel
        self.client = cs.SpeechAsyncClient(
            client_options=ClientOptions(api_endpoint=f"{GCP_LOCATION}-speech.googleapis.com")
        )
        self.audio_q = asyncio.Queue()
        self.transcript_chunks = []
        self.full_text = ""
        self.start_time = None
        self.stream_finished_flag = False
        
        # Audio properties
        self.sample_rate = 0
        self.channels = 0
        self.audio_bytes = None
        self.bytes_per_sec = 0
        
        # Streaming state for restarts
        self.total_bytes_sent = 0
        self.stream_base_offset = 0.0

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
        
        # Calculate bytes per second for timestamp offset logic (16-bit = 2 bytes)
        self.bytes_per_sec = self.sample_rate * self.channels * 2
        
        logger.info(f"Audio Ready: {self.channels} channel(s), {self.sample_rate} Hz, {self.bytes_per_sec} bytes/sec")

    async def get_recognizer(self):
        """Gets or creates the Speech V2 Recognizer."""
        parent = f"projects/{GCP_PROJECT_ID}/locations/{GCP_LOCATION}"
        name = f"{parent}/recognizers/{GCP_RECOGNIZER_ID}"
        
        try:
            logger.info(f"Checking for recognizer: {GCP_RECOGNIZER_ID}")
            return await self.client.get_recognizer(name=name)
        except exceptions.NotFound:
            logger.info(f"Recognizer '{GCP_RECOGNIZER_ID}' not found. Creating new one...")
            request = cs.CreateRecognizerRequest(
                parent=parent,
                recognizer_id=GCP_RECOGNIZER_ID,
                recognizer=cs.Recognizer(
                    default_recognition_config=cs.RecognitionConfig(
                        language_codes=[LANGUAGE_CODE], 
                        model=GCP_TRANSCRIPTION_MODEL
                    ),
                ),
            )
            op = await self.client.create_recognizer(request=request)
            return await op.result()

    async def stream_audio_chunks(self):
        """Simulates streaming by feeding the queue."""
        print("DEBUG: Streamer task started", flush=True)
        chunk_size = 8000 # Bytes per chunk
        chunk_duration = chunk_size / self.bytes_per_sec
        print(f"DEBUG: Chunk duration: {chunk_duration:.4f}s", flush=True)

        # Pre-load 1 second of audio to prime the stream
        preload_chunks = int(1.0 / chunk_duration)
        chunks_queued = 0

        for i in range(0, len(self.audio_bytes), chunk_size):
            chunk = self.audio_bytes[i:i+chunk_size]
            await self.audio_q.put(chunk)
            chunks_queued += 1
            if chunks_queued > preload_chunks:
                await asyncio.sleep(chunk_duration) 
            
        await self.audio_q.put(None) # EOF
        print("DEBUG: Streamer finished", flush=True)

    async def generate_requests(self, recognizer_name):
        """Yields streaming requests for the API."""
        print("DEBUG: Generator started", flush=True)
        
        # 1. Configuration Request
        if self.channels > 1 and self.enable_multi_channel:
             mc_mode = cs.RecognitionFeatures.MultiChannelMode.SEPARATE_RECOGNITION_PER_CHANNEL
        else:
             mc_mode = cs.RecognitionFeatures.MultiChannelMode.MULTI_CHANNEL_MODE_UNSPECIFIED
        
        print(f"DEBUG: Yielding config (mc_mode={mc_mode.name})", flush=True)
        yield cs.StreamingRecognizeRequest(
            recognizer=recognizer_name,
            streaming_config=cs.StreamingRecognitionConfig(
                config=cs.RecognitionConfig(
                    explicit_decoding_config=cs.ExplicitDecodingConfig(
                        encoding=cs.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
                        sample_rate_hertz=self.sample_rate,
                        audio_channel_count=self.channels,
                    ),
                    features=cs.RecognitionFeatures(
                        multi_channel_mode=mc_mode,
                        enable_word_time_offsets=True,
                        enable_automatic_punctuation=True,
                    ),
                    language_codes=[LANGUAGE_CODE],
                    model=GCP_TRANSCRIPTION_MODEL,
                ),
                streaming_features=cs.StreamingRecognitionFeatures(
                    interim_results=True
                )
            ),
        )

        # 2. Audio Data Requests
        start_time = time.time()
        chunk_count = 0
        while True:
            # Check for stream time limit (restart every 240s / 4 minutes)
            if time.time() - start_time > 240:
                print("DEBUG: Stream time limit reached. Restarting stream...", flush=True)
                return

            chunk = await self.audio_q.get()
            if chunk is None: 
                print("DEBUG: Generator received EOF", flush=True)
                self.stream_finished_flag = True
                return
            
            chunk_count += 1
            # Track bytes sent for timestamp calculation
            self.total_bytes_sent += len(chunk)
            
            yield cs.StreamingRecognizeRequest(audio=chunk)

    async def process_responses(self, stream, use_buffered=False):
        """Consumes responses from the API."""
        print("DEBUG: Starting response processing loop", flush=True)
        buffer = []

        async def flush_buffer_loop():
            while True:
                await asyncio.sleep(self.buffer_timeout)
                if buffer:
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
                        continue
                    
                    print("", flush=True) # Newline after heartbeats
                    if use_buffered:
                        buffer.append(result)
                    else:
                        self._process_single_result(result)
        finally:
            if flusher: flusher.cancel()
            if buffer: self._process_buffer(buffer)

    def _print_chunk(self, chunk):
        """Prints a single transcript chunk to the console."""
        speaker = chunk.get("speaker", "Speaker")
        text = chunk.get("text", "")
        timestamp = chunk.get("timestamp", "")
        print(f"[{timestamp}] {speaker: <10}: {text}", flush=True)

    def _process_single_result(self, result):
        if not result.alternatives: return
        if not self.transcript_chunks:
            logger.info("First transcript result received.")

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

    def _get_timestamp(self, result):
        offset = getattr(result, "result_end_offset", None)
        if not offset and result.alternatives and result.alternatives[0].words:
            offset = result.alternatives[0].words[-1].end_offset
            
        seconds = offset.total_seconds() if offset else 0
        
        # Add offset from previous streams
        total_seconds = self.stream_base_offset + seconds
        
        ts = self.start_time + datetime.timedelta(seconds=total_seconds)
        return ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-5]

    async def run(self, use_buffered=False):
        """Main execution flow."""
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        self.stream_finished_flag = False
        self.total_bytes_sent = 0
        self.stream_base_offset = 0.0
        
        recognizer = await self.get_recognizer()
        await self.prepare_audio()

        if not self.audio_bytes:
            logger.error("No audio data to transcribe!")
            return

        logger.info(f"Starting {'buffered' if use_buffered else 'live'} transcription...")
        
        stream_task = asyncio.create_task(self.stream_audio_chunks())
        await asyncio.sleep(0.5)

        while not self.stream_finished_flag:
            # Update the base offset for timestamps for THIS stream
            if self.bytes_per_sec > 0:
                self.stream_base_offset = self.total_bytes_sent / self.bytes_per_sec
            
            print(f"DEBUG: Calling streaming_recognize for {recognizer.name}", flush=True)
            print(f"DEBUG: Current stream offset: {self.stream_base_offset:.2f}s", flush=True)
            
            try:
                responses_stream = await self.client.streaming_recognize(
                    requests=self.generate_requests(recognizer.name)
                )
                print("DEBUG: streaming_recognize call returned stream iterator", flush=True)
                await self.process_responses(responses_stream, use_buffered)
            except Exception as e:
                logger.error(f"Error during streaming_recognize: {e}")
                await asyncio.sleep(1)
        
        await stream_task 

        self.transcript_chunks.sort(key=lambda x: x['timestamp'])
        with open(OUTPUT_FILENAME, "w") as f:
            json.dump(self.transcript_chunks, f, indent=2)
        
        logger.info(f"Done. Saved to {OUTPUT_FILENAME}")