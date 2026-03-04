"""
Real-Time Model Comparison Demo (STT V2)

This script demonstrates side-by-side comparison of two different STT models
(e.g., 'telephony' vs 'chirp_3') processing the same audio stream.

Architecture:
[Simulator] -> [Broadcaster] -> [audio_q] -> [Worker A (Model 1), Worker B (Model 2)] 
                                             -> [Shared Engine] -> [Unified UI]
"""

import asyncio
import os
from google.cloud import speech_v2 as cs
from google.api_core.client_options import ClientOptions
from core.utils import parse_common_args, setup_pipeline, run_broadcaster, q_gen
from core.providers import V2Provider

async def main(args):
    # 1. Pipeline Setup
    # Add a virtual 'model' name for setup_pipeline naming
    args.model = f"{args.model1}_vs_{args.model2}"
    
    # Initialize shared components
    simulator, engine, terminal, json_log, output_path = await setup_pipeline(args, "comparison")

    # 2. Setup API Providers for both models
    project = os.getenv("PROJECT_ID")
    recognizer_id = os.getenv("GCP_RECOGNIZER_ID")
    location = os.getenv("LOCATION", "us-central1")
    
    def create_provider(model_name):
        # Chirp often requires different endpoints/locations
        if "chirp" in model_name.lower():
            api_endpoint, loc = "us-speech.googleapis.com", "us"
        else:
            loc = location
            api_endpoint = f"{loc}-speech.googleapis.com"
            
        client = cs.SpeechAsyncClient(client_options=ClientOptions(api_endpoint=api_endpoint))
        recognizer_name = f"projects/{project}/locations/{loc}/recognizers/{recognizer_id}-{model_name.replace('_', '-')}"
        
        return V2Provider(client, recognizer_name, model_name)

    provider1 = create_provider(args.model1 if hasattr(args, 'model1') else "telephony")
    provider2 = create_provider(args.model2 if hasattr(args, 'model2') else "chirp_2")

    # 3. Define the Dual Workers
    q1 = asyncio.Queue()
    q2 = asyncio.Queue()

    async def api_worker(provider, queue, model_label):
        """Standard worker that injects a model label into every event."""
        async for event in provider.stream(q_gen(queue), multi_channel=True, chunk_duration_sec=args.chunk_size):
            event.metadata["model"] = model_label.upper()
            
            # Note: We now allow VAD events through because the engine 
            # uses them to 'pin' wordless transcripts (Chirp-3 timing fix).
            engine.process_raw_event(event)

    # 4. Orchestration
    m1_label = args.model1.upper()
    m2_label = args.model2.upper()
    
    print(f"\nREAL-TIME COMPARISON: {m1_label} vs {m2_label}")
    print(f"Output File: {output_path}")
    print("-" * 115)

    try:
        await asyncio.gather(
            run_broadcaster(simulator, engine, [q1, q2], args.duration, args.chunk_size, broadcast_stereo=True),
            api_worker(provider1, q1, m1_label),
            api_worker(provider2, q2, m2_label)
        )
    except KeyboardInterrupt:
        print("\nStopping comparison...")
    finally:
        engine.shutdown()
        json_log.close()

if __name__ == "__main__":
    # Add comparison-specific arguments
    import argparse
    from core.utils import parse_common_args
    
    # We need to monkey-patch or manually extend the parser for this specific demo
    parser = argparse.ArgumentParser(description="Real-Time Model Comparison")
    parser.add_argument("gcs_uri", help="Path to audio file")
    parser.add_argument("--model1", default="telephony")
    parser.add_argument("--model2", default="chirp_2")
    parser.add_argument("--stability", type=float, default=1.0)
    parser.add_argument("--gap", type=float, default=0.5)
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--chunk-size", type=float, default=0.1)
    parser.add_argument("--wait-for-play", action="store_true")
    parser.add_argument("--duration", type=float, default=60)
    parser.add_argument("--mode", choices=["low_latency", "readability"], default="readability")
    parser.add_argument("--use-chirp3", action="store_true", help="Use specialized Chirp3Provider for Chirp-3 models")
    
    # Override standard args with our extended set
    args = parser.parse_args()
    
    asyncio.run(main(args))
