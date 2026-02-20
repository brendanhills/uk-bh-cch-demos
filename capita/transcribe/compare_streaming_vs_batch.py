"""
Streaming vs Batch Comparison (Chirp-3)

This script runs a live Chirp-3 streaming transcription alongside a 
pre-calculated Chirp-3 Batch baseline. This allows for direct evaluation 
of streaming latency, stability, and word accuracy against the "ground truth" 
of an offline batch run.
"""

import argparse
import asyncio
import os
import logging
import json
from transcribe_common import TranscriptionService, BaseTranscriptionService, ComparisonManager
from batch_transcribe_v2 import BatchTranscriptionService
from simulate_audio import AudioStreamSimulator

# Configure professional logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class BaselinePlaybackService(BaseTranscriptionService):
    """
    A 'Mock' service that plays back pre-calculated batch results.
    It ignores audio chunks and instead uses the playhead time to 
    release transcript segments at their 'ideal' timestamps.
    """
    def __init__(self, sample_rate: int, channels: int, baseline_data: list):
        super().__init__(sample_rate, channels)
        self.baseline_data = sorted(baseline_data, key=lambda x: x['start_sec'])
        self.released_indices = set()

    def _print_in_column(self, text, channel, is_final, ts_only=None):
        """Labels output as BATCH baseline."""
        # BaselinePlaybackService uses Speaker ID (1 or 2) as channel
        super()._print_in_column(text, channel, is_final, ts_only)

    async def run(self, audio_stream):
        """Monitors playback time and releases baseline chunks."""
        async for _ in audio_stream:
            # The playhead time is updated by the ComparisonManager/Simulator
            # We check which baseline chunks should have appeared by now
            for i, chunk in enumerate(self.baseline_data):
                if i not in self.released_indices and self.current_audio_time >= chunk['start_sec']:
                    rel_start = f"{chunk['start_sec']:05.1f}s"
                    # Note: batch_transcribe_v2.py doesn't yet save end_sec, 
                    # so we fallback to start_sec if missing
                    rel_end = f"{chunk.get('end_sec', chunk['start_sec']):05.1f}s"
                    self._print_in_column(f"[{rel_start}] \"{chunk['text']}\" [{rel_end}]", chunk['speaker'], is_final=True, ts_only=chunk['timestamp'])
                    self.released_indices.add(i)
            
            # Simulated progress (assuming 250ms chunks)
            self.current_audio_time += 0.25
        
        if self.log_file:
            self.log_file.close()

async def main():
    parser = argparse.ArgumentParser(description="Streaming vs Batch Comparison")
    parser.add_argument("gcs_uri", help="The GCS URI of the audio file")
    parser.add_argument("--model", default="chirp_3", help="Model to use for both runs")
    parser.add_argument("--customer-channel", default="channel_1")
    parser.add_argument("--force-rebatch", action="store_true", help="Force a new batch run even if batch_output.json exists")
    parser.add_argument("--output", help="Mirror the 4-column output to this file")
    parser.add_argument("--mode", default="low_latency", choices=["low_latency", "readability"])
    parser.add_argument("--duration", type=float, default=60, help="Stop test after X seconds.")

    args = parser.parse_args()

    # 1. Ensure Batch Baseline Exists
    baseline_file = "batch_output.json"
    if args.force_rebatch or not os.path.exists(baseline_file):
        print(f"\n--- GENERATING BATCH BASELINE ({args.model}) ---")
        batch_service = BatchTranscriptionService(2, args.customer_channel, model_name=args.model)
        await batch_service.run_batch(args.gcs_uri)
    
    with open(baseline_file, "r") as f:
        baseline_data = json.load(f)

    # 2. Prepare Audio Simulator
    simulator = AudioStreamSimulator(args.gcs_uri, force_mono=False)
    await simulator.prepare()

    # 3. Initialize Services
    # Service A: Live Streaming (Columns 3 & 4)
    streaming_service = TranscriptionService(
        simulator.sample_rate, simulator.channels, model_name=args.model
    )
    
    # Mode Configuration
    if args.mode == "readability":
        streaming_service.STABILITY_THRESHOLD = 1.5
        streaming_service.GAP_THRESHOLD = 0.8
        streaming_service.ACTIVE_BLOCKING = True
        
    if args.output:
        streaming_service.set_log_file(args.output)
        
    # UI Override: Map Stream Speaker 1 -> Col 3, Speaker 2 -> Col 4
    original_print_stream = streaming_service._print_in_column
    streaming_service._print_in_column = lambda text, channel, is_final, ts_only=None: original_print_stream(
        text, channel + 2, is_final, ts_only
    )

    # Service B: Baseline Playback (Columns 1 & 2)
    baseline_service = BaselinePlaybackService(
        simulator.sample_rate, simulator.channels, baseline_data
    )
    if args.output:
        # Note: We don't want to open the same file twice for writing from two services
        # We share the log_file handle from the streaming_service
        baseline_service.log_file = streaming_service.log_file

    # UI Override: Map Batch Speaker 1 -> Col 1, Speaker 2 -> Col 2
    # Note: BaselinePlaybackService.run already passes speaker ID as channel
    original_print_batch = baseline_service._print_in_column
    baseline_service._print_in_column = lambda text, channel, is_final, ts_only=None: original_print_batch(
        text, channel, is_final, ts_only
    )

    header = f"\nCOMPARING: {args.model.upper()} Batch vs Streaming"
    col_labels = [
        f"{'BATCH S1':<38}", f"{'BATCH S2':<38}",
        f"{'STREAM S1':<38}", f"{'STREAM S2':<38}"
    ]
    print(header)
    labels_row = "  ".join(col_labels)
    print(labels_row)
    separator = "-" * 160
    print(separator)

    if args.output:
        # Write headers to log file too
        streaming_service.log_file.write(header + "\n")
        streaming_service.log_file.write(labels_row + "\n")
        streaming_service.log_file.write(separator + "\n")

    # 4. Run Side-by-Side
    manager = ComparisonManager([streaming_service, baseline_service])
    await manager.run(simulator.stream(duration=args.duration))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nComparison stopped by user.")
