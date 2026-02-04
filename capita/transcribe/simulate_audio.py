import asyncio
import logging
import io
import subprocess
import audioop
from urllib.parse import quote

from pydub import AudioSegment
from google.cloud.storage import Client as StorageClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

class AudioStreamSimulator:
    """
    Simulates a real-time audio stream from a GCS file.
    Handles downloading, property inspection, and chunked streaming.
    """

    def __init__(self, gcs_uri: str, force_mono: bool = False):
        self.gcs_uri = gcs_uri
        self.force_mono = force_mono
        self.sample_rate = 0
        self.channels = 0  # Target channels for API
        self.source_channels = 0  # Actual channels in file
        self.audio_bytes = None
        self.bytes_per_sec = 0
        self.COLOR_SPEAKER_2 = "\033[93m"  # Yellow/Orange
        self.COLOR_RESET = "\033[0m"

    def generate_signed_url(self):
        """Generates a direct link to the file in Google Cloud Console."""

        try:
            bucket_name, blob_name = self.gcs_uri.replace("gs://", "").split("/", 1)
            encoded_blob = quote(blob_name, safe="")
            url = f"https://storage.cloud.google.com/{bucket_name}/{encoded_blob}"

            try:
                account = subprocess.check_output(
                    [
                        "gcloud",
                        "auth",
                        "list",
                        "--filter=status:ACTIVE",
                        "--format=value(account)",
                    ],
                    text=True,
                ).strip()
                if account:
                    url += f"?authuser={account}"
            except Exception:
                pass
            print(f"\nOpen Audio in Console: {url}\n", flush=True)
            return url

        except Exception as e:
            logger.warning(f"Could not generate console URL: {e}")

            return None

    def wait_for_user_start(self):
        """Pauses execution until the user presses Enter."""
        input(
            f"{self.COLOR_SPEAKER_2}Press Enter to start transcription...{self.COLOR_RESET}"
        )

    async def prepare(self):
        """
        Downloads audio and determines properties.
        """

        logger.info(f"Downloading audio from {self.gcs_uri}...")
        storage = StorageClient()
        bucket_name, blob_name = self.gcs_uri.replace("gs://", "").split("/", 1)
        bucket = storage.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        raw_audio = blob.download_as_bytes()
        storage.close()
        
        seg = AudioSegment.from_file(io.BytesIO(raw_audio))
        self.source_channels = seg.channels
        self.sample_rate = seg.frame_rate

        if self.force_mono:
            self.channels = 1
        else:
            self.channels = self.source_channels

        self.audio_bytes = seg.set_sample_width(2).rw_data
        self.bytes_per_sec = self.sample_rate * self.source_channels * 2

        logger.info(
            f"Audio Ready: Source {self.source_channels}ch -> Target {self.channels}ch, {self.sample_rate} Hz"
        )

    async def stream(self):
        """
        Async generator that yields audio chunks.
        In normal mode, it throttles to real-time.
        """
        if not self.audio_bytes:
            return

        chunk_duration_sec = 0.25
        chunk_size = int(self.bytes_per_sec * chunk_duration_sec)
        frame_size = 2 * self.source_channels
        chunk_size = (chunk_size // frame_size) * frame_size
        chunks_queued = 0

        for i in range(0, len(self.audio_bytes), chunk_size):
            chunk = self.audio_bytes[i : i + chunk_size]

            if self.force_mono and self.source_channels > 1:
                try:
                    chunk = audioop.tomono(chunk, 2, 0.5, 0.5)
                except Exception as e:
                    logger.error(f"Error converting chunk to mono: {e}")

            yield chunk
            chunks_queued += 1

            # Simulate real-time delay
            if chunks_queued > (1.0 / chunk_duration_sec):
                await asyncio.sleep(chunk_duration_sec)
