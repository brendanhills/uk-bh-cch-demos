"""
Legacy Baseline Transcription (STT V2)

This script is maintained as a 'clean' baseline that stays close to the 
original code logic provided by the customer. It has been enhanced with 
essential fixes for real-time ordering and two-column display.
"""

import argparse
import asyncio
import datetime
import json
import logging
import os
import io
import textwrap

from pydub import AudioSegment
from google.api_core.client_options import ClientOptions
from google.api_core import exceptions
from google.cloud import speech_v2 as cs
from google.cloud.storage import Client as StorageClient
from dotenv import load_dotenv

# --- Configuration & Environment ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
GCP_PROJECT_ID = os.getenv("PROJECT_ID")
GCP_LOCATION = os.getenv("LOCATION", "us-central1")
GCP_RECOGNIZER_ID = os.getenv("GCP_RECOGNIZER_ID")
GCP_TRANSCRIPTION_MODEL = os.environ.get("GCP_TRANSCRIPTION_MODEL", "telephony")
LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "en-US")
CUSTOMER_CHANNEL = os.environ.get("CUSTOMER_CHANNEL", "channel_1")
OUTPUT_FILENAME = "output.json"

# Logic tuning (Global Constants)
STABILITY_THRESHOLD = 3.0 # Wait 3 seconds for out-of-order results
CHUNK_DURATION_SEC = 0.25  # Simulator chunk size

# Validation
assert GCP_PROJECT_ID, "PROJECT_ID missing"
assert GCP_RECOGNIZER_ID, "GCP_RECOGNIZER_ID missing"

class AudioStream:
    """Session timing container."""
    def __init__(self):
        self.start_time = datetime.datetime.now(datetime.timezone.utc)

class TranscriptionService:
    """
    Self-contained transcription service. 
    Implements the core 'Radical' logic: sequential ordering via a stability window.
    """

    def __init__(self, gcs_uri: str, customer_channel: str, buffer_timeout: float):
        self.gcs_uri = gcs_uri
        self.customer_channel = customer_channel
        self.buffer_timeout = buffer_timeout
        self.transcribe_client = cs.SpeechAsyncClient(
            client_options=ClientOptions(api_endpoint=f"{GCP_LOCATION}-speech.googleapis.com")
        )
        self.gcp_transcription_model = GCP_TRANSCRIPTION_MODEL
        self.language_code = LANGUAGE_CODE
        self.enable_channel_identification = True
        self.media_sample_rate_hz = 0
        self.number_of_channels = 0
        self.audio_q = asyncio.Queue()
        self.full_transcript = ""
        self.accumulated_transcript_chunks = []
        self.accumulated_length = 0
        self.stream = AudioStream()
        self.audio_data = None 
        
        # Internal Display & Stability State
        self.previous_ts = None
        self.current_audio_time = 0.0
        self.stability_buffer = []
        self.COLOR_SPEAKER_1 = "\033[92m" 
        self.COLOR_SPEAKER_2 = "\033[93m" 
        self.COLOR_RESET = "\033[0m"

    async def _get_audio_properties(self):
        """Downloads audio and inspects properties using pydub."""
        try:
            storage_client = StorageClient()
            bucket_name, blob_name = self.gcs_uri.replace("gs://", "").split("/", 1)
            blob = storage_client.bucket(bucket_name).blob(blob_name)
            self.audio_data = blob.download_as_bytes()
            
            audio_segment = AudioSegment.from_file(io.BytesIO(self.audio_data))
            if audio_segment.channels == 2:
                # Reliability check: detect and handle identical tracks
                left, right = audio_segment.split_to_mono()
                if left.raw_data == right.raw_data:
                    logger.error("Error: Stereo input required for speaker separation.")
                    exit(1)
                else:
                    self.number_of_channels = 2
            else:
                self.number_of_channels = audio_segment.channels
                self.enable_channel_identification = False

            self.media_sample_rate_hz = audio_segment.frame_rate
            logger.info(f"Audio properties: {self.number_of_channels} ch, {self.media_sample_rate_hz} Hz")
        except Exception as e:
            logger.error(f"Failed to read audio from GCS: {e}")
            raise
        finally:
            storage_client.close()

    async def _stream_audio_from_gcs(self):
        """Simulates real-time audio playback by throttling data upload to the API."""
        try:
            audio_segment = AudioSegment.from_file(io.BytesIO(self.audio_data)) 
            audio_segment = audio_segment.set_sample_width(2)
            pcm_data = audio_segment.set_frame_rate(self.media_sample_rate_hz).set_channels(self.number_of_channels).raw_data

            bytes_per_sec = self.media_sample_rate_hz * self.number_of_channels * 2
            chunk_size = int(bytes_per_sec * CHUNK_DURATION_SEC)
            frame_size = self.number_of_channels * 2
            chunk_size = (chunk_size // frame_size) * frame_size

            start_send_time = asyncio.get_event_loop().time()
            chunks_sent = 0

            for i in range(0, len(pcm_data), chunk_size):
                chunk = pcm_data[i:i+chunk_size]
                if not chunk: break
                await self.audio_q.put(chunk)
                chunks_sent += 1
                self.current_audio_time = chunks_sent * CHUNK_DURATION_SEC

                # Real-time throttling delay
                expected_time = start_send_time + (chunks_sent * CHUNK_DURATION_SEC)
                sleep_time = expected_time - asyncio.get_event_loop().time()
                if sleep_time > 0: await asyncio.sleep(sleep_time)

            await self.audio_q.put(None) # EOF
            logger.info("Audio stream finished.")
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            await self.audio_q.put(None)

    async def request_generator(self):
        """Generates V2 streaming requests."""
        multi_channel_config = (
            cs.RecognitionFeatures.MultiChannelMode.SEPARATE_RECOGNITION_PER_CHANNEL
            if self.enable_channel_identification else cs.RecognitionFeatures.MultiChannelMode.MULTI_CHANNEL_MODE_UNSPECIFIED
        )
        yield cs.StreamingRecognizeRequest(
            recognizer=self.recognizer,
            streaming_config=cs.StreamingRecognitionConfig(
                config=cs.RecognitionConfig(
                    explicit_decoding_config=cs.ExplicitDecodingConfig(
                        encoding=cs.ExplicitDecodingConfig.AudioEncoding.LINEAR16,
                        sample_rate_hertz=self.media_sample_rate_hz,
                        audio_channel_count=self.number_of_channels,
                    ),
                    features=cs.RecognitionFeatures(
                        multi_channel_mode=multi_channel_config,
                        enable_word_time_offsets=True,
                        enable_automatic_punctuation=True,
                    ),
                    language_codes=[self.language_code],
                    model=self.gcp_transcription_model,
                ),
                streaming_features=cs.StreamingRecognitionFeatures(interim_results=True),
            ),
        )

        while True:
            chunk = await self.audio_q.get()
            if chunk is None: return
            yield cs.StreamingRecognizeRequest(audio=chunk)

    def _create_transcript_chunk(self, result):
        """Creates a standardized data chunk from an API result."""
        alt = result.alternatives[0]
        channel_tag = getattr(result, 'channel_tag', 1) or 1
        
        # Use START offset for better conversational order
        start_time = None
        if alt.words:
            start_time = alt.words[0].start_offset
        if not start_time:
            start_time = getattr(result, "result_end_offset", None)
            
        seconds = start_time.total_seconds() if start_time else 0 
        ts = self.stream.start_time + datetime.timedelta(seconds=seconds)
        
        speaker = "customer" if (self.customer_channel.lower() == "channel_1" and channel_tag == 1) or \
                               (self.customer_channel.lower() == "channel_2" and channel_tag == 2) else "agent"
            
        return {
            "speaker": speaker,
            "channel_tag": channel_tag,
            "text": alt.transcript,
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "start": seconds
        }

    def _process_stability_buffer(self, force_flush=False):
        """Sorts and releases finalized chunks once they are stable."""
        stable, remaining = [], []
        for chunk in self.stability_buffer:
            if force_flush or (self.current_audio_time > chunk['start'] + STABILITY_THRESHOLD):
                stable.append(chunk)
            else:
                remaining.append(chunk)
        
        self.stability_buffer = remaining
        if stable:
            stable.sort(key=lambda x: x['timestamp'])
            for s in stable:
                self.accumulated_transcript_chunks.append(s)
                self._print_chunk(s)

    def _print_chunk(self, chunk):
        """Renders chunks in two columns."""
        print("\r\033[K", end="", flush=True) # Clear draft
        
        ts = chunk['timestamp'].split(" ")[-1]
        speaker, text, channel = chunk['speaker'], chunk['text'], chunk['channel_tag']
        
        flag = "\033[91mOut of order: 🚨\033[0m" if self.previous_ts and self.previous_ts > ts else ""
        self.previous_ts = ts
            
        color = self.COLOR_SPEAKER_1 if channel == 1 else self.COLOR_SPEAKER_2
        content = f'{speaker}: {flag}{ts} {color}"{text}"{self.COLOR_RESET}'
        
        if channel == 1:
            wrapper = textwrap.TextWrapper(width=55, subsequent_indent=" " * 12)
            print(wrapper.fill(content), flush=True)
        else:
            offset = " " * 60
            wrapper = textwrap.TextWrapper(width=115, initial_indent=offset, subsequent_indent=offset + " " * 12)
            print(wrapper.fill(content), flush=True)

    def _print_interim(self, text, channel):
        """Draft line at bottom."""
        try: term_width = os.get_terminal_size().columns
        except OSError: term_width = 80
        color, reset = "\033[90m", "\033[0m"
        prefix = f"... Ch{channel} Draft: "
        max_len = term_width - len(prefix) - 5
        if len(text) > max_len: text = "..." + text[-max_len:]
        print(f"\r\033[K{color}{prefix}{text}{reset}", end="", flush=True)

    async def _handle_transcription(self):
        """Consumes results from the API stream."""
        try:
            responses = await self.transcribe_client.streaming_recognize(requests=self.request_generator())
            async for response in responses:
                for result in response.results:
                    if not result.alternatives: continue
                    alt = result.alternatives[0]

                    if not result.is_final:
                        self._print_interim(alt.transcript, getattr(result, "channel_tag", 1))
                        continue

                    # Final
                    self.full_transcript += "\n" + alt.transcript
                    chunk = self._create_transcript_chunk(result)
                    self.stability_buffer.append(chunk)
                    self._process_stability_buffer()
        except Exception as e:
            logger.error(f"API Error: {e}")
        finally:
            self._process_stability_buffer(force_flush=True)

    async def run(self):
        """Demo lifecycle."""
        # Find or Create Recognizer
        parent = f"projects/{GCP_PROJECT_ID}/locations/{GCP_LOCATION}"
        name = f"{parent}/recognizers/{GCP_RECOGNIZER_ID}"
        try:
            self.recognizer = (await self.transcribe_client.get_recognizer(name=name)).name
        except exceptions.NotFound:
            req = cs.CreateRecognizerRequest(parent=parent, recognizer_id=GCP_RECOGNIZER_ID,
                recognizer=cs.Recognizer(default_recognition_config=cs.RecognitionConfig(
                    language_codes=["en-US"], model=self.gcp_transcription_model)))
            self.recognizer = (await (await self.transcribe_client.create_recognizer(request=req)).result()).name

        await self._get_audio_properties()
        logger.info(f"Starting Legacy Baseline demo...")
        
        await asyncio.gather(self._stream_audio_from_gcs(), self._handle_transcription())
        
        with open(OUTPUT_FILENAME, "w") as f:
            json.dump(self.accumulated_transcript_chunks, f, indent=2)
        logger.info(f"Results saved to {OUTPUT_FILENAME}")

async def main():
    parser = argparse.ArgumentParser(description="Legacy Baseline Demo")
    parser.add_argument("gcs_uri", help="The GCS URI (gs://...)")
    args = parser.parse_args()

    # Header
    print(f"\n{'Channel 1':<60} {'Channel 2'}")
    print("-" * 120)

    service = TranscriptionService(gcs_uri=args.gcs_uri, 
                                   customer_channel=os.getenv("CUSTOMER_CHANNEL", "channel_1"), 
                                   buffer_timeout=0.5)
    await service.run()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass