"""
Real-Time Audio Stream Simulator

This module provides the 'live' audio infrastructure for all demo scripts.
It handles downloading from GCS, inspecting audio metadata, and streaming 
binary chunks at real-time speeds to simulate a live phone call or broadcast.
"""

import asyncio
import logging
import io
import subprocess
import audioop
from urllib.parse import quote

from pydub import AudioSegment
from google.cloud.storage import Client as StorageClient

# Shared logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

class AudioStreamSimulator:
    """
    Simulates a real-time audio feed from a static GCS file.
    Includes on-the-fly mono down-mixing and playback throttling.
    """

    def __init__(self, gcs_uri: str, force_mono: bool = False):
        self.gcs_uri = gcs_uri
        self.force_mono = force_mono
        self.sample_rate = 0
        self.channels = 0  # Desired channels for the output stream
        self.source_channels = 0 # Actual channels detected in the file
        self.audio_bytes = None
        self.bytes_per_sec = 0
        self.COLOR_SPEAKER_2 = "\033[93m"  # Yellow (for prompts)
        self.COLOR_RESET = "\033[0m"

    def generate_signed_url(self):
        """
        Generates a direct web link to the audio file in the Google Cloud Console.
        Uses the local gcloud identity to ensure the link works immediately.
        """
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
                if account: url += f"?authuser={account}"
            except Exception: pass
            
            print(f"\nPlayback URL: {url}\n", flush=True)
            return url
        except Exception as e:
            logger.warning(f"Could not generate console URL: {e}")
            return None

    def wait_for_user_start(self):
        """
        Pauses execution to allow the user to start audio playback in their browser
        before the transcription begins.
        """
        input(f"{self.COLOR_SPEAKER_2}Press Enter to start streaming...{self.COLOR_RESET}")

    async def prepare(self):
        """
        Initializes the simulator by downloading the audio and preparing the buffer.
        Normalizes all audio to Linear16 PCM (the expected API format).
        """
        if self.gcs_uri.startswith("gs://"):
            logger.info(f"Downloading {self.gcs_uri}...")
            storage = StorageClient()
            bucket_name, blob_name = self.gcs_uri.replace("gs://", "").split("/", 1)
            bucket = storage.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            raw_audio_data = blob.download_as_bytes()
            storage.close()
        else:
            logger.info(f"Reading local file {self.gcs_uri}...")
            with open(self.gcs_uri, "rb") as f:
                raw_audio_data = f.read()
        
        # Load and inspect audio using pydub
        seg = AudioSegment.from_file(io.BytesIO(raw_audio_data))
        self.source_channels = seg.channels
        self.sample_rate = seg.frame_rate

        # Determine target channel count
        self.channels = 1 if self.force_mono else self.source_channels

        # Convert to raw Linear16 PCM data
        self.audio_bytes = seg.set_sample_width(2).raw_data
        
        # Calculate timing parameters (2 bytes per sample)
        self.bytes_per_sec = self.sample_rate * self.source_channels * 2

        logger.info(f"Audio Ready: {self.source_channels}ch, {self.sample_rate}Hz -> Streaming as {self.channels}ch")

    async def stream(self, duration: float = None):
        """
        Async generator that yields audio chunks at real-time speeds.
        Enforces chronological data release using precise sleep timers.
        """
        if not self.audio_bytes: return

        # Configuration: 250ms chunks provide a good balance of latency and overhead
        chunk_duration_sec = 0.25
        chunk_size = int(self.bytes_per_sec * chunk_duration_sec)
        
        # Alignment: chunk size must be a multiple of the frame size
        frame_size = 2 * self.source_channels
        chunk_size = (chunk_size // frame_size) * frame_size
        chunks_queued = 0

        # Calculate max bytes if duration is set
        max_bytes = int(self.bytes_per_sec * duration) if duration else len(self.audio_bytes)
        audio_to_stream = self.audio_bytes[:max_bytes]

        # High-precision timer start
        start_time = asyncio.get_event_loop().time()

        for i in range(0, len(audio_to_stream), chunk_size):
            chunk = audio_to_stream[i : i + chunk_size]

            # Real-time Mono down-mixing if requested
            if self.force_mono and self.source_channels > 1:
                try:
                    chunk = audioop.tomono(chunk, 2, 0.5, 0.5)
                except Exception as e:
                    logger.error(f"Mono conversion error: {e}")

            yield chunk
            chunks_queued += 1

            # REAL-TIME THROTTLING:
            # We calculate when this chunk 'should' be sent based on its position.
            expected_release_time = start_time + (chunks_queued * chunk_duration_sec)
            current_time = asyncio.get_event_loop().time()
            
            sleep_time = expected_release_time - current_time
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)