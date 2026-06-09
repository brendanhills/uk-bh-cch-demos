"""
Parallel Multi-Worker Transcription Demo (STT V2)

This script demonstrates an advanced architecture where a stereo file is split 
into two independent mono streams, each handled by its own API worker.

Architecture:
[Simulator] -> [Broadcaster] -> [Queue L, Queue R] -> [RawChannelWorker L, RawChannelWorker R]
                                                   -> [Centralized Engine] -> [Unified UI]
"""

import asyncio
import os
from google.cloud import speech_v2 as cs
from google.api_core.client_options import ClientOptions
from core.utils import parse_common_args, setup_pipeline, run_broadcaster, q_gen
from core.providers import V2Provider
from core.workers import RawChannelWorker

async def main():
    # 1. Pipeline Setup
    args = parse_common_args("Parallel Producer-Consumer Demo")
    simulator, engine, terminal, json_log, output_path = await setup_pipeline(args, "parallel")

    # 2. Configure Google STT Client
    project = os.getenv("PROJECT_ID")
    recognizer_id = os.getenv("GCP_RECOGNIZER_ID")
    location = "us" if ("chirp" in args.model.lower() or "medical" in args.model.lower()) else os.getenv("LOCATION", "us-central1")
    api_endpoint = f"{location}-speech.googleapis.com"

    client = cs.SpeechAsyncClient(client_options=ClientOptions(api_endpoint=api_endpoint))
    recognizer_name = f"projects/{project}/locations/{location}/recognizers/{recognizer_id}"
    
    # 3. Initialize Workers & Queues
    q1, q2 = asyncio.Queue(), asyncio.Queue()
    
    provider = V2Provider(client, recognizer_name, args.model, endpoint_sensitivity=args.sensitivity)
    provider.speech_start_timeout_sec = args.start_timeout
    
    w1 = RawChannelWorker(provider, 1)
    w2 = RawChannelWorker(provider, 2)

    async def run_worker(worker, queue, channel_id):
        """Worker loop that captures events and feeds the Engine."""
        out_q = asyncio.Queue()
        
        async def forward_to_engine():
            while True:
                event = await out_q.get()
                if event is None: break
                
                # Sync VAD state for engine-side blocking
                if event.event_type == "speech_activity_begin":
                    engine.update_active_status(channel_id, event.start_sec)
                elif event.event_type == "speech_activity_end":
                    engine.update_active_status(channel_id, None)
                
                engine.process_raw_event(event)

        await asyncio.gather(
            worker.run(q_gen(queue), out_q, args.chunk_size),
            forward_to_engine()
        )

    # 4. Orchestration
    print(f"\nPARALLEL DEMO ({args.mode.upper()}): {os.path.basename(args.gcs_uri)}")
    print(f"Config: model={args.model}, chunk={args.chunk_size}s, stability={engine.STABILITY_THRESHOLD}s, gap={engine.GAP_THRESHOLD}s")
    print(f"Output: {output_path}")
    print("-" * 100)

    try:
        await asyncio.gather(
            run_broadcaster(simulator, engine, [q1, q2], args.duration, args.chunk_size),
            run_worker(w1, q1, 1),
            run_worker(w2, q2, 2)
        )
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        engine.shutdown()
        json_log.close()

if __name__ == "__main__":
    asyncio.run(main())
