"""
Two-Channel Transcription Demo (STT V2)

This script demonstrates the 'standard' approach for transcribing 2-channel 
stereo audio using a single bi-directional GRPC stream.

Architecture: 
[Simulator] --> [Broadcaster] --> [Queue] --> [V2Provider] --> [Engine] --> [Sinks]
"""

import asyncio
import os
from google.cloud import speech_v2 as cs
from google.api_core.client_options import ClientOptions
from core.utils import parse_common_args, setup_pipeline, run_broadcaster, q_gen
from core.providers import V2Provider
from core.chirp3_provider import Chirp3Provider

async def main():
    # 1. Pipeline Setup (Arg parsing, Engine/Simulator initialization)
    args = parse_common_args("Two-Channel Demo")
    simulator, engine, terminal, json_log, output_path = await setup_pipeline(args, "two_channel")

    # 2. Configure Google STT Client
    project = os.getenv("PROJECT_ID")
    recognizer_id = os.getenv("GCP_RECOGNIZER_ID")
    location = "us" if "chirp" in args.model.lower() else os.getenv("LOCATION", "us-central1")
    api_endpoint = f"{location}-speech.googleapis.com"

    client = cs.SpeechAsyncClient(client_options=ClientOptions(api_endpoint=api_endpoint))
    recognizer_name = f"projects/{project}/locations/{location}/recognizers/{recognizer_id}"
    
    # Initialize the high-level API wrapper
    if args.use_chirp3:
        provider = Chirp3Provider(client, recognizer_name, args.model)
    else:
        provider = V2Provider(client, recognizer_name, args.model)

    # 3. Define the Worker (API Consumer)
    audio_q = asyncio.Queue()

    async def api_worker():
        """Consumes audio from the queue, streams to STT, and pushes events to the engine."""
        async for event in provider.stream(q_gen(audio_q), multi_channel=True, chunk_duration_sec=args.chunk_size):
            # Update Voice Activity status for Active Blocking logic
            if event.event_type == "speech_activity_begin":
                engine.update_active_status(event.speaker_id, event.start_sec)
            elif event.event_type == "speech_activity_end":
                engine.update_active_status(event.speaker_id, None)
            
            # Pass raw transcript/VAD events to the engine for processing
            engine.process_raw_event(event)

    # 4. Orchestration
    print(f"\nTWO-CHANNEL DEMO ({args.mode.upper()}): {os.path.basename(args.gcs_uri)}")
    print(f"Config: model={args.model}, chunk={args.chunk_size}s, stability={engine.STABILITY_THRESHOLD}s, gap={engine.GAP_THRESHOLD}s")
    print(f"Output File: {output_path}")
    print("-" * 100)

    try:
        # Run the Broadcaster (Producer) and the API Worker (Consumer) concurrently
        await asyncio.gather(
            run_broadcaster(simulator, engine, audio_q, args.duration, args.chunk_size),
            api_worker()
        )
    except KeyboardInterrupt:
        print("\nStopping demo...")
    finally:
        # Ensure all buffered results are emitted and files are closed
        engine.shutdown()
        json_log.close()

if __name__ == "__main__":
    asyncio.run(main())
