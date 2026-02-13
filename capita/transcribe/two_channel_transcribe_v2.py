"""
Unified Two-Channel Transcription Service (STT V2)

This script provides a high-quality, real-time transcription experience for stereo audio files.
It supports two primary modes:
1. LOW_LATENCY: Minimum latency, printing results the moment they are finalized by the API.
2. READABILITY: Prioritizes conversational flow using a stability buffer and active blocking.
"""

import argparse
import asyncio
import os
import logging
from transcribe_common import TranscriptionService, GCP_TRANSCRIPTION_MODEL
from simulate_audio import AudioStreamSimulator

# Configure professional logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class UnifiedTwoChannelService(TranscriptionService):
    """
    Subclass of the common TranscriptionService tailored for 2-channel stereo audio.
    Implements speaker mapping and mode-based logic tuning.
    """
    def __init__(self, sample_rate: int, channels: int, customer_channel: str, 
                 mode: str = "low_latency"):
        # Initialize the base V2 service with multi-channel support enabled
        super().__init__(sample_rate, channels, enable_multi_channel=True)
        self.customer_channel = customer_channel
        self.recognizer_id = f"{os.getenv('GCP_RECOGNIZER_ID')}-unified"
        
        # Configure logic thresholds based on the selected mode
        if mode == "readability":
            # READABILITY MODE: Prefers perfect ordering over speed
            self.STABILITY_THRESHOLD = 1.5  # Seconds to wait for asynchronous results
            self.GAP_THRESHOLD = 0.8        # Seconds of silence to trigger a turn split
            self.ACTIVE_BLOCKING = True     # Hold short utterances if a monologue is ongoing
        else: 
            # LOW LATENCY MODE: Prefers raw speed
            self.STABILITY_THRESHOLD = 0.0
            self.GAP_THRESHOLD = 0.0
            self.ACTIVE_BLOCKING = False

    def _print_in_column(self, text, channel, is_final, ts_only=None):
        """
        Maps numeric channel tags (1, 2) to human-readable labels (Caller, Agent)
        before passing to the standardized columnar display logic.
        """
        speaker = "Caller" if (self.customer_channel == f"channel_{channel}") else "Agent"
        
        # We only prepend the speaker label to finalized chunks to keep drafts clean
        if is_final:
            text = f"{speaker}: {text}"
            
        super()._print_in_column(text, channel, is_final, ts_only)

async def main():
    """CLI Entrypoint for the Unified Stereo Transcription demo."""
    parser = argparse.ArgumentParser(description="Unified Two-Channel Transcription Demo")
    parser.add_argument("gcs_uri", help="The GCS URI of the stereo audio file (gs://...)")
    parser.add_argument("--mode", choices=["low_latency", "readability"], default="low_latency", 
                        help="Toggles between raw speed ('low_latency') and conversational order ('readability').")
    parser.add_argument("--customer-channel", default=os.environ.get("CUSTOMER_CHANNEL", "channel_1"),
                        help="Defines which audio channel (1 or 2) belongs to the customer.")
    parser.add_argument('--wait-for-play', action='store_true', help='Pauses for user to start audio.')

    args = parser.parse_args()

    print(f"\nMode: {args.mode.upper()}")

    
    ch1_label = "Channel 1 (Caller)" if args.customer_channel == "channel_1" else "Channel 1 (Agent)"
    ch2_label = "Channel 2 (Agent)" if args.customer_channel == "channel_1" else "Channel 2 (Caller)"
    print(f"{ch1_label:<60} {ch2_label}")
    print("-" * 120)

    # 2. Audio Simulation: Initialize the real-time audio streamer
    simulator = AudioStreamSimulator(args.gcs_uri, force_mono=False)
    await simulator.prepare()
    simulator.generate_signed_url()
    
    if args.wait_for_play:
        simulator.wait_for_user_start()


    # 3. Service Execution: Instantiate and run the unified service
    service = UnifiedTwoChannelService(simulator.sample_rate, simulator.channels, 
                                       args.customer_channel, mode=args.mode)
    print(f"Settings: Stability={service.STABILITY_THRESHOLD}s, GapSplit={service.GAP_THRESHOLD}s, ActiveBlocking={service.ACTIVE_BLOCKING}")
    # Pipe the simulated real-time stream into the transcription engine
    await service.run(simulator.stream())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo stopped by user.")
