"""
Mono Diarization Demo (Chirp-3)
This script demonstrates Chirp-3's native speaker diarization on a single-channel mix.
"""

import asyncio
import os
import argparse
from google.cloud import speech_v2 as cs
from google.api_core.client_options import ClientOptions
from core.utils import parse_common_args, setup_pipeline, run_broadcaster, q_gen
from core.providers import V2Provider
from core.models import TranscriptionEvent

async def main():
    # 1. Pipeline Setup (Force mono simulator)
    args = parse_common_args("Mono Diarization Demo")
    args.model = "chirp_3"
    
    # Initialize shared components
    # setup_pipeline creates the simulator, engine, terminal sink etc.
    # We pass is_mono=True to ensure the simulator mixes the audio down.
    simulator, engine, terminal, json_log, output_path = await setup_pipeline(args, "mono_diarization")

    # 2. Setup V2 Provider with Diarization Enabled
    project = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION", "us-central1")
    recognizer_id = os.getenv("RECOGNIZER_ID", "default-recognizer")
    
    # For Chirp, we always use the 'us' endpoint/location for V2
    api_endpoint, loc = "us-speech.googleapis.com", "us"
    client = cs.SpeechAsyncClient(client_options=ClientOptions(api_endpoint=api_endpoint))
    recognizer_name = f"projects/{project}/locations/{loc}/recognizers/{recognizer_id}-chirp3-mono"
    
    provider = V2Provider(client, recognizer_name, "chirp_3")

    # 3. Define the Worker Loop
    audio_q = asyncio.Queue()

    async def api_worker():
        """Standard worker loop that feeds the Engine."""
        # Note: we pass diarization=True here
        async for event in provider.stream(q_gen(audio_q), multi_channel=False, diarization=True, chunk_duration_sec=args.chunk_size):
            engine.process_raw_event(event)

    # 4. Orchestration
    print(f"\nMONO DIARIZATION DEMO (CHIRP-3): {os.path.basename(args.gcs_uri)}")
    print(f"Config: chunk={args.chunk_size}s, stability={engine.STABILITY_THRESHOLD}s")
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
