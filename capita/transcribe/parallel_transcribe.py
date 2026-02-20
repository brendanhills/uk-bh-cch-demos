import argparse
import asyncio
import os
from google.cloud import speech_v2 as cs
from core.utils import parse_common_args, setup_pipeline, run_broadcaster, q_gen
from core.providers import V2Provider

async def main():
    args = parse_common_args("Parallel Producer-Consumer Demo")
    simulator, engine, terminal, json_log, output_path = await setup_pipeline(args, "parallel")

    # 1. Setup API Provider
    from google.api_core.client_options import ClientOptions
    project = os.getenv("PROJECT_ID")
    recognizer_id = os.getenv("GCP_RECOGNIZER_ID")
    
    if "chirp" in args.model.lower():
        api_endpoint, location = "us-speech.googleapis.com", "us"
    else:
        location = os.getenv("LOCATION", "us-central1")
        api_endpoint = f"{location}-speech.googleapis.com"

    client = cs.SpeechAsyncClient(client_options=ClientOptions(api_endpoint=api_endpoint))
    recognizer_name = f"projects/{project}/locations/{location}/recognizers/{recognizer_id}"
    provider = V2Provider(client, recognizer_name, args.model)

    # 2. Parallel Workers
    q1, q2 = asyncio.Queue(), asyncio.Queue()
    
    async def worker(audio_gen, channel_id):
        async for event in provider.stream(audio_gen, channel_id=channel_id, chunk_duration_sec=args.chunk_size):
            if event.event_type == "speech_activity_begin":
                engine.update_active_status(channel_id, event.start_sec)
            elif event.event_type == "speech_activity_end":
                engine.update_active_status(channel_id, None)
            engine.process_raw_event(event)

    print(f"\nREFACTORED PARALLEL DEMO: {os.path.basename(args.gcs_uri)}")
    print(f"Output File: {output_path}")
    print("-" * 100)

    try:
        await asyncio.gather(
            run_broadcaster(simulator, engine, [q1, q2], args.duration, args.chunk_size),
            worker(q_gen(q1), 1),
            worker(q_gen(q2), 2)
        )
    finally:
        engine.shutdown()
        json_log.close()

if __name__ == "__main__":
    asyncio.run(main())
