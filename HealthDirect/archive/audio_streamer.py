import asyncio
import io
import time
import os
import logging
from typing import AsyncGenerator, Optional
from pydub import AudioSegment
from google.cloud.storage import Client as StorageClient
import yt_dlp

logger = logging.getLogger(__name__)

class AudioStreamSimulator:
    """Simulates a real-time audio stream from GCS, local file, or YouTube URL."""

    def __init__(self, source_uri: str, chunk_duration_ms: int = 100):
        self.source_uri = source_uri
        self.chunk_duration_ms = chunk_duration_ms
        self.sample_rate = 0
        self.channels = 0
        self.sample_width = 0
        self._audio_data: Optional[bytes] = None

    async def _load_from_gcs(self) -> bytes:
        logger.info(f"Downloading from GCS: {self.source_uri}")
        storage_client = StorageClient()
        try:
            bucket_name, blob_name = self.source_uri.replace("gs://", "").split("/", 1)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            return blob.download_as_bytes()
        finally:
            storage_client.close()

    async def _load_from_youtube(self) -> bytes:
        logger.info(f"Downloading from YouTube: {self.source_uri}")
        
        # Simplify: just download best audio, let pydub handle conversion
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '-', 
            'quiet': True,
            'logtostderr': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web']
                }
            }
        }

        import tempfile
        # Create a temp file with a suffix, but let yt-dlp determine the extension if possible?
        # No, we need a target. Let's use a safe placeholder extension like .m4a or just no extension
        # and let yt-dlp append it, but we need to know what it is.
        # Actually, simpler: Use 'outtmpl' with a predictable name in a temp dir.
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # We'll tell yt-dlp to save here with a fixed name, allowing it to append ext
            ydl_opts['outtmpl'] = f"{tmp_dir}/download.%(ext)s"
            
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, lambda: self._download_yt(ydl_opts))
            
            # Find the file (yt-dlp might have saved as .m4a, .webm, etc.)
            files = os.listdir(tmp_dir)
            if not files:
                raise FileNotFoundError("YouTube download failed, no file created.")
            
            downloaded_file = os.path.join(tmp_dir, files[0])
            logger.info(f"Downloaded: {downloaded_file}")
            
            # Load with pydub (auto-detects format)
            audio = await loop.run_in_executor(None, lambda: AudioSegment.from_file(downloaded_file))
            
            # Export as WAV bytes for consistency with the rest of the pipeline
            buffer = io.BytesIO()
            audio.export(buffer, format="wav")
            return buffer.getvalue()

    def _download_yt(self, opts):
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([self.source_uri])

    async def _load_from_local(self) -> bytes:
        logger.info(f"Loading local file: {self.source_uri}")
        if not os.path.exists(self.source_uri):
            raise FileNotFoundError(f"File not found: {self.source_uri}")
        
        # Run file I/O in thread pool to avoid blocking async loop
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: open(self.source_uri, "rb").read())

    async def get_audio_data(self) -> bytes:
        """Determines source type and loads audio data."""
        if self._audio_data:
            return self._audio_data

        if self.source_uri.startswith("gs://"):
            data = await self._load_from_gcs()
        elif self.source_uri.startswith("http://") or self.source_uri.startswith("https://"):
             # Assume URL is YouTube or compatible for now, or direct download? 
             # For this specific requirement "YouTube URL", we assume yt-dlp.
             # We could check 'youtube.com' or 'youtu.be' but yt-dlp supports many sites.
             data = await self._load_from_youtube()
        else:
            data = await self._load_from_local()

        self._audio_data = data
        
        # Parse properties
        audio = AudioSegment.from_file(io.BytesIO(data))
        self.sample_rate = audio.frame_rate
        self.channels = audio.channels
        self.sample_width = audio.sample_width
        
        # Calculate bit rate (bits per second)
        bit_rate = self.sample_rate * self.channels * self.sample_width * 8
        duration_secs = len(audio) / 1000.0

        print("\n" + "="*40)
        print("AUDIO STREAM INFO")
        print("-" * 40)
        print(f"Source:         {self.source_uri}")
        print(f"Channels:       {self.channels}")
        print(f"Sample Rate:    {self.sample_rate} Hz")
        print(f"Bit Depth:      {self.sample_width * 8} bit")
        print(f"Bit Rate:       {bit_rate / 1000:.1f} kbps")
        print(f"Duration:       {duration_secs:.2f} seconds")
        print("="*40 + "\n")
        
        return data

    async def stream(self, simulate_realtime: bool = True) -> AsyncGenerator[bytes, None]:
        """Yields audio chunks.
        
        Args:
            simulate_realtime: If True, sleeps between chunks to mimic real-time playback.
                               If False, yields chunks as fast as possible.
        """
        data = await self.get_audio_data()
        audio = AudioSegment.from_file(io.BytesIO(data))
        
        # Ensure it's PCM LINEAR16
        audio = audio.set_sample_width(2)
        self.sample_width = 2
        self.sample_rate = audio.frame_rate
        self.channels = audio.channels

        pcm_data = audio.raw_data
        
        bytes_per_ms = (self.sample_rate * self.channels * self.sample_width) / 1000
        chunk_size = int(bytes_per_ms * self.chunk_duration_ms)
        
        start_time = time.time()
        bytes_sent = 0

        for i in range(0, len(pcm_data), chunk_size):
            chunk = pcm_data[i:i+chunk_size]
            bytes_sent += len(chunk)
            
            if simulate_realtime:
                # Calculate how much time should have elapsed for this many bytes
                expected_elapsed = bytes_sent / (bytes_per_ms * 1000)
                actual_elapsed = time.time() - start_time
                
                sleep_time = expected_elapsed - actual_elapsed
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            
            yield chunk

if __name__ == "__main__":
    # Quick standalone test
    async def test():
        # Example: Replace with a valid local file or YouTube URL to test
        # simulator = AudioStreamSimulator("test.wav")
        # simulator = AudioStreamSimulator("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        pass
    
    # asyncio.run(test())