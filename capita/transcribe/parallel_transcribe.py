"""
Parallel Multi-Worker Transcription Demo (STT V2)

This script demonstrates an advanced architecture where a stereo file is split 
into two independent mono streams, each handled by its own API worker.

Modes:
- Mode A (Default): Centralized Interleaving logic. Workers are 'raw'.
- Mode B: Distributed Stabilization logic. Workers are 'stabilized'.
"""

import asyncio
import os
from google.cloud import speech_v2 as cs
from google.api_core.client_options import ClientOptions
from core.utils import parse_common_args, setup_pipeline, run_broadcaster, q_gen
from core.providers import V2Provider
from core.workers import RawChannelWorker, StabilizedChannelWorker

async def main():
    # 1. Pipeline Setup
    args = parse_common_args("Parallel Producer-Consumer Demo", is_parallel=True)
    simulator, engine, terminal, json_log, output_path = await setup_pipeline(args, "parallel")

    # 2. Configure Google STT Client
    project = os.getenv("PROJECT_ID")
    recognizer_id = os.getenv("GCP_RECOGNIZER_ID")
    location = "us" if "chirp" in args.model.lower() else os.getenv("LOCATION", "us-central1")
    api_endpoint = f"{location}-speech.googleapis.com"

    client = cs.SpeechAsyncClient(client_options=ClientOptions(api_endpoint=api_endpoint))
    recognizer_name = f"projects/{project}/locations/{location}/recognizers/{recognizer_id}"
    
    # 3. Initialize Workers & Queues
    q1, q2 = asyncio.Queue(), asyncio.Queue()
    
    def get_provider(model):
        return V2Provider(client, recognizer_name, model)

    if args.arch == "mode_b":
        # Mode B: Workers handle their own stabilization
        w1 = StabilizedChannelWorker(get_provider(args.model), 1, 
                                     stability_threshold=args.stability or 1.0, 
                                     gap_threshold=args.gap or 0.5)
        w2 = StabilizedChannelWorker(get_provider(args.model), 2,
                                     stability_threshold=args.stability or 1.0, 
                                     gap_threshold=args.gap or 0.5)
    else:
        # Mode A: Centralized engine handles stabilization
        w1 = RawChannelWorker(get_provider(args.model), 1)
        w2 = RawChannelWorker(get_provider(args.model), 2)

    async def run_worker(worker, queue, channel_id):
        """Worker loop that captures events and feeds the Engine."""
        out_q = asyncio.Queue()
        
        async def forward_to_engine():
            while True:
                event = await out_q.get()
                if event is None: break
                
                # Sync VAD state for engine-side blocking (Mode A)
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
    print(f"\nPARALLEL DEMO ({args.mode.upper()} - {args.arch.upper()}): {os.path.basename(args.gcs_uri)}")
    print(f"Config: model={args.model}, chunk={args.chunk_size}s, stability={engine.STABILITY_THRESHOLD}s, gap={engine.GAP_THRESHOLD}s")
    print(f"Output: {output_path}")
    print("-" * 100)

    try:
        broadcaster_task = asyncio.create_task(run_broadcaster(simulator, engine, [q1, q2], args.duration, args.chunk_size))
        
        # Keep worker clocks in sync with the broadcaster for Mode B
        async def sync_clocks():
            while not broadcaster_task.done():
                if args.arch == "mode_b":
                    w1.update_time(engine.current_audio_time)
                    w2.update_time(engine.current_audio_time)
                await asyncio.sleep(0.1)

        await asyncio.gather(
            broadcaster_task,
            sync_clocks(),
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
