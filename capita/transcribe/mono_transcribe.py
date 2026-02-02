import argparse
import asyncio
from transcribe_common import TranscriptionService, OUTPUT_FILENAME

class MonoTranscriptionService(TranscriptionService):
    def __init__(self, gcs_uri: str, buffer_timeout: float):
        super().__init__(gcs_uri, buffer_timeout, enable_multi_channel=False)

    def _create_transcript_chunk(self, result):
        """Creates a chunk with a default speaker label."""
        return {
            "speaker": "Speaker",
            "text": result.alternatives[0].transcript,
            "timestamp": self._get_timestamp(result),
        }

async def main():
    parser = argparse.ArgumentParser(description="Transcribe a mono audio file from GCS.")
    parser.add_argument("gcs_uri", help="The GCS URI (gs://...)")
    parser.add_argument('--use-buffered', action='store_true', help='Enable buffered transcription.')
    parser.add_argument('--buffer-timeout', type=float, default=0.5)
    
    args = parser.parse_args()

    service = MonoTranscriptionService(args.gcs_uri, args.buffer_timeout)
    await service.run(args.use_buffered)

if __name__ == "__main__":
    asyncio.run(main())
