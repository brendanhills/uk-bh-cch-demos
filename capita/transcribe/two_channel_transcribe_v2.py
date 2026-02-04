import argparse
import asyncio
import os
import textwrap
from transcribe_common import TranscriptionService, GCP_TRANSCRIPTION_MODEL
from simulate_audio import AudioStreamSimulator

class TwoChannelTranscriptionService(TranscriptionService):
    def __init__(self, sample_rate: int, channels: int, customer_channel: str):
        # Use a specific recognizer ID for stereo
        rec_id = f"{os.getenv('GCP_RECOGNIZER_ID')}-stereo"
        super().__init__(sample_rate, channels, enable_multi_channel=True, recognizer_id=rec_id, model_name=GCP_TRANSCRIPTION_MODEL)
        self.customer_channel = customer_channel
        self.previous_ts = None

    def _create_transcript_chunk(self, result):
        """Creates a chunk with speaker identification based on channel."""
        timestamp = self._get_timestamp(result)
        
        # Determine channel tag (default to 1)
        channel_tag = getattr(result, 'channel_tag', 1) or 1
        
        # Determine speaker
        if self.customer_channel.lower() == "channel_1":
            speaker = "Caller" if channel_tag == 1 else "Agent"
        else:
            speaker = "Caller" if channel_tag == 2 else "Agent"
        
        return {
            "speaker": speaker,
            "channel_tag": channel_tag,
            "text": result.alternatives[0].transcript,
            "timestamp": timestamp,
        }

    def _print_chunk(self, chunk):
        speaker = chunk.get("speaker", "Speaker")
        channel_tag = chunk.get("channel_tag", 1)
        text = chunk.get("text", "")
        
        # Extract time only (HH:MM:SS.f) from "YYYY-MM-DD HH:MM:SS.f"
        full_ts = chunk.get("timestamp", "")
        time_part = full_ts.split(" ")[1] if " " in full_ts else full_ts
        
        # Determine column parameters
        LEFT_COL_WIDTH = 45 # Width for wrapping text
        RIGHT_COL_OFFSET = 60 # Start position for Channel 2
        
        if self.previous_ts is not None and self.previous_ts > time_part:
            out_of_order_flag = "Out of order: 🚨"
        else:
            out_of_order_flag = ""
        self.previous_ts = time_part
            
        # Determine Color
        color = self.COLOR_SPEAKER_1 if channel_tag == 1 else self.COLOR_SPEAKER_2
        colored_text = f'{color}"{text}"{self.COLOR_RESET}'

        # Prepare the full first line: Timestamp +  "Text"
        full_content = f'{speaker}: {out_of_order_flag}{time_part} {colored_text}' 
        
        if channel_tag == 1:
            # Left Column (Channel 1)
            indent_str = " " * 12 
            wrapper = textwrap.TextWrapper(width=LEFT_COL_WIDTH, subsequent_indent=indent_str)
            print(wrapper.fill(full_content), flush=True)
                
        else:
            # Right Column (Channel 2)
            offset_str = " " * RIGHT_COL_OFFSET
            # Width needs to account for the offset
            wrapper = textwrap.TextWrapper(width=RIGHT_COL_OFFSET + LEFT_COL_WIDTH, 
                                         initial_indent=offset_str, 
                                         subsequent_indent=offset_str + " " * 12)
            print(wrapper.fill(full_content), flush=True)

async def main():
    parser = argparse.ArgumentParser(description="Transcribe a two-channel audio file from GCS.")
    parser.add_argument("gcs_uri", help="The GCS URI (gs://...)")
    parser.add_argument("--customer-channel", default=os.environ.get("CUSTOMER_CHANNEL", "channel_1"))
    parser.add_argument('--wait-for-play', action='store_true', help='Wait for user input before starting stream.')
    
    args = parser.parse_args()

    # Determine headers based on arg
    ch1_label = "Channel 1"
    ch2_label = "Channel 2"
    
    if args.customer_channel == "channel_1":
        ch1_label += " (Caller)"
        ch2_label += " (Agent)"
    else:
        ch1_label += " (Agent)"
        ch2_label += " (Caller)"

    # Print Header
    print(f"{ch1_label:<60} {ch2_label}")
    print("-" * 100)

    # 1. Setup Simulator
    # Force mono is False for V2 Stereo
    simulator = AudioStreamSimulator(args.gcs_uri, force_mono=False)
    await simulator.prepare()
    simulator.generate_signed_url()
    
    if args.wait_for_play:
        simulator.wait_for_user_start()

    # 2. Setup Service
    service = TwoChannelTranscriptionService(simulator.sample_rate, simulator.channels, args.customer_channel)
    
    # 3. Run
    await service.run(simulator.stream())

if __name__ == "__main__":
    asyncio.run(main())