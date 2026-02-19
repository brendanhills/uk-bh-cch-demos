"""
Model Comparison Framework (STT V2)

This script allows side-by-side comparison of two STT models 
(e.g., telephony vs chirp_3) in real-time. It uses multi-channel 
recognition for 100% reliable speaker attribution.
"""

import argparse
import asyncio
import os
import logging
import textwrap
from transcribe_common import TranscriptionService, ComparisonManager
from simulate_audio import AudioStreamSimulator

# Configure professional logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class ComparisonTranscriptionService(TranscriptionService):
    """
    Subclass of TranscriptionService with specialized UI for comparison.
    Prepends the model name to results and uses distinct colors.
    """
    def __init__(self, sample_rate: int, channels: int, model_name: str, 
                 customer_channel: str, color_p1: str, color_p2: str):
        super().__init__(sample_rate, channels, model_name=model_name)
        self.model_label = model_name.upper()
        self.customer_channel = customer_channel
        self.COLOR_SPEAKER_1 = color_p1
        self.COLOR_SPEAKER_2 = color_p2
        self.recognizer_id = f"{os.getenv('GCP_RECOGNIZER_ID', 'default').lower()}-{model_name.lower().replace('_', '-')}"

    def _print_in_column(self, text, channel, is_final, ts_only=None):
        """Standardizes the output for side-by-side comparison with speaker ID."""
        # Prepend the model label and speaker to finalized chunks
        if is_final:
            text = f"[{self.model_label}] S{channel}: {text}"
            
        super()._print_in_column(text, channel, is_final, ts_only)

async def main():
    parser = argparse.ArgumentParser(description="Model Comparison Demo")
    parser.add_argument("gcs_uri", help="The GCS URI of the stereo audio file")
    parser.add_argument("--model1", default="telephony", help="First model to compare")
    parser.add_argument("--model2", default="chirp_3", help="Second model to compare")
    parser.add_argument("--customer-channel", default="channel_1")
    parser.add_argument('--wait-for-play', action='store_true', help='Pauses for user to start audio.')
    parser.add_argument("--duration", type=float, default=60, help="Stop test after X seconds.")

    args = parser.parse_args()

    # 1. Prepare Audio Simulator
    simulator = AudioStreamSimulator(args.gcs_uri, force_mono=False)
    await simulator.prepare()
    if args.gcs_uri.startswith("gs://"):
        simulator.generate_signed_url()
    
    if args.wait_for_play:
        simulator.wait_for_user_start()

    # 2. Initialize Two Services
    # Service 1: Model 1 (Colors: Green/Yellow)
    service1 = ComparisonTranscriptionService(
        simulator.sample_rate, simulator.channels, args.model1, 
        args.customer_channel, "\033[92m", "\033[93m"
    )
    
    # Service 2: Model 2 (Colors: Cyan/Magenta)
    service2 = ComparisonTranscriptionService(
        simulator.sample_rate, simulator.channels, args.model2, 
        args.customer_channel, "\033[96m", "\033[95m"
    )

    print(f"\nCOMPARING: {args.model1.upper()} vs {args.model2.upper()}")
    print(f"{'Channel 1 (Caller)':<60} {'Channel 2 (Agent)'}")
    print("-" * 120)

    # 3. Coordinate both through the ComparisonManager
    manager = ComparisonManager([service1, service2])
    await manager.run(simulator.stream(duration=args.duration))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nComparison stopped by user.")
