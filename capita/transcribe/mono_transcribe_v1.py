"""
Mono Diarization Transcription Demo (STT V1)

This script demonstrates AI-based speaker diarization on a single mono stream
using the legacy STT V1 API.

Architecture: 
[Simulator] -> [Broadcaster] -> [Queue] -> [V1Provider] -> [Engine] -> [Sinks]
"""

import asyncio
import os
from google.cloud import speech_v1 as cs
from core.utils import parse_common_args, setup_pipeline, run_broadcaster, q_gen
from core.providers import V1Provider

async def main():
    # 1. Pipeline Setup (Force mono ingestion for V1 Diarization)
    args = parse_common_args("Mono Diarization Demo", is_mono=True)
    simulator, engine, terminal, json_log, output_path = await setup_pipeline(args, "mono_v1", force_mono=True)

    # 2. Configure Google STT Client (V1)
    client = cs.SpeechAsyncClient()
    provider = V1Provider(client)

    # 3. Define the Worker
    audio_q = asyncio.Queue()

    async def api_worker():
        """Consumes mono audio and handles AI-driven speaker separation."""
        async for event in provider.stream(q_gen(audio_q)):
            # V1 doesn't support the same VAD events as V2, so we just process raw transcripts
            engine.process_raw_event(event)

    # 4. Orchestration
    print(f"\nMONO DIARIZATION DEMO (V1): {os.path.basename(args.gcs_uri)}")
    print(f"Output File: {output_path}")
    print("-" * 100)

    try:
        await asyncio.gather(
            run_broadcaster(simulator, engine, audio_q, args.duration, args.chunk_size),
            api_worker()
        )
    except KeyboardInterrupt:
        print("\nStopping demo...")
    finally:
        engine.shutdown()
        json_log.close()

if __name__ == "__main__":
    asyncio.run(main())
