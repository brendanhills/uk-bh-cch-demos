import argparse
import asyncio
import os
from google.cloud import speech_v1 as cs
from core.utils import parse_common_args, setup_pipeline, run_broadcaster, q_gen
from core.providers import V1Provider

async def main():
    args = parse_common_args("Mono Diarization Demo", is_mono=True)
    simulator, engine, terminal, json_log, output_path = await setup_pipeline(args, "mono_v1", force_mono=True)

    # 1. Setup API Provider
    client = cs.SpeechAsyncClient()
    provider = V1Provider(client)

    # 2. Worker
    audio_q = asyncio.Queue()

    async def worker():
        async for event in provider.stream(q_gen(audio_q)):
            engine.process_raw_event(event)

    print(f"\nREFACTORED MONO V1 DEMO: {os.path.basename(args.gcs_uri)}")
    print(f"Output File: {output_path}")
    print("-" * 100)

    try:
        await asyncio.gather(
            run_broadcaster(simulator, engine, audio_q, args.duration, args.chunk_size),
            worker()
        )
    finally:
        engine.shutdown()
        json_log.close()

if __name__ == "__main__":
    asyncio.run(main())
