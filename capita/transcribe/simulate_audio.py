"""
Real-Time Audio Stream Simulator.
Provides the infrastructure to stream static audio files (local or GCS) 
at real-time speeds to simulate a live phone call or broadcast.
"""

import asyncio
import logging
import io
import subprocess
import audioop
from urllib.parse import quote
from pydub import AudioSegment
from google.cloud.storage import Client as StorageClient

# Configure standard logging for the simulator
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

class AudioStreamSimulator:
    """
    Handles audio ingestion, normalization, and throttled streaming.
    """

    def __init__(self, gcs_uri: str, force_mono: bool = False, target_sample_rate: int = None):
        self.gcs_uri = gcs_uri
        self.force_mono = force_mono
        self.target_sample_rate = target_sample_rate
        
        # State
        self.sample_rate = 0
        self.channels = 0 
        self.source_channels = 0
        self.audio_bytes = None
        self.bytes_per_sec = 0
        
        # UI Colors
        self.COLOR_PROMPT = "\033[93m"  # Yellow
        self.COLOR_RESET = "\033[0m"

    def generate_signed_url(self):
        """Generates a link to the GCS file for browser playback during the demo."""
        try:
            bucket_name, blob_name = self.gcs_uri.replace("gs://", "").split("/", 1)
            encoded_blob = quote(blob_name, safe="")
            url = f"https://storage.cloud.google.com/{bucket_name}/{encoded_blob}"

            # Attempt to append the active gcloud account for seamless login
            try:
                account = subprocess.check_output(
                    ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"],
                    text=True
                ).strip()
                if account: 
                    url += f"?authuser={account}"
            except Exception: 
                pass
            
            print(f"\nPlayback URL: {url}\n", flush=True)
            return url
        except Exception as e:
            logger.warning(f"Could not generate console URL: {e}")
            return None

    def wait_for_user_start(self):
        """Pauses the script so the user can start browser audio before transcription kicks in."""
        input(f"{self.COLOR_PROMPT}Press Enter to start streaming...{self.COLOR_RESET}")

    async def prepare(self):
        """Downloads, resamples, and normalizes audio to Linear16 PCM."""
        if self.gcs_uri.startswith("gs://"):
            logger.info(f"Downloading {self.gcs_uri}...")
            storage = StorageClient()
            bucket_name, blob_name = self.gcs_uri.replace("gs://", "").split("/", 1)
            blob = storage.bucket(bucket_name).blob(blob_name)
            raw_audio_data = blob.download_as_bytes()
            storage.close()
        else:
            logger.info(f"Reading local file {self.gcs_uri}...")
            with open(self.gcs_uri, "rb") as f:
                raw_audio_data = f.read()
        
        # Ingest using pydub
        seg = AudioSegment.from_file(io.BytesIO(raw_audio_data))
        
        # Apply resampling if requested (GCP STT usually prefers 16kHz)
        if self.target_sample_rate:
            logger.info(f"Resampling from {seg.frame_rate}Hz to {self.target_sample_rate}Hz...")
            seg = seg.set_frame_rate(self.target_sample_rate)
            
        self.source_channels = seg.channels
        self.sample_rate = seg.frame_rate
        self.channels = 1 if self.force_mono else self.source_channels

        # Convert to raw Linear16 PCM (the wire format for STT)
        self.audio_bytes = seg.set_sample_width(2).raw_data
        
        # 2 bytes per sample * channels * sample_rate
        self.bytes_per_sec = self.sample_rate * self.source_channels * 2

        logger.info(f"Audio Ready: {self.source_channels}ch, {self.sample_rate}Hz -> Streaming as {self.channels}ch")

    async def stream(self, duration: float = None, chunk_duration_sec: float = 0.25):
        """
        Async generator yielding audio chunks at real-time speeds.
        Uses precise sleep timers to enforce chronological data release.
        """
        if not self.audio_bytes: 
            return

        chunk_size = int(self.bytes_per_sec * chunk_duration_sec)
        
        # Align chunk size to frame boundary (sample_width * channels)
        frame_size = 2 * self.source_channels
        chunk_size = (chunk_size // frame_size) * frame_size
        
        # Respect optional duration limit
        max_bytes = int(self.bytes_per_sec * duration) if duration else len(self.audio_bytes)
        audio_to_stream = self.audio_bytes[:max_bytes]

        start_time = asyncio.get_event_loop().time()
        chunks_queued = 0

        for i in range(0, len(audio_to_stream), chunk_size):
            chunk = audio_to_stream[i : i + chunk_size]

            # Mono down-mix if requested
            if self.force_mono and self.source_channels > 1:
                chunk = audioop.tomono(chunk, 2, 0.5, 0.5)

            yield chunk
            chunks_queued += 1

            # ENFORCE REAL-TIME:
            # We calculate when the next chunk 'belongs' on the timeline.
            expected_release_time = start_time + (chunks_queued * chunk_duration_sec)
            current_time = asyncio.get_event_loop().time()
            
            sleep_time = expected_release_time - current_time
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
