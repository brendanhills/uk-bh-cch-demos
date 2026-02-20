"""
Batch Transcription Service (STT V2) via GCS

This script processes an entire audio file stored in GCS using the 
BatchRecognize API. It provides a full, non-streaming transcription 
suitable for ground-truth comparison with real-time streaming results.
"""

import argparse
import asyncio
import os
import logging
import datetime
import json
from google.cloud import speech_v2 as cs
from google.api_core.client_options import ClientOptions
from transcribe_common import BaseTranscriptionService, GCP_PROJECT_ID, GCP_LOCATION, GCP_TRANSCRIPTION_MODEL, LANGUAGE_CODE

# Configure professional logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class BatchTranscriptionService(BaseTranscriptionService):
    """
    Subclass of BaseTranscriptionService for offline batch processing.
    Uses BatchRecognize for long GCS files and provides columnar UI.
    """
    def __init__(self, channels: int, customer_channel: str, 
                 model_name: str = None, enable_diarization: bool = False):
        # Sample rate is not strictly required for V2 batch with auto-decoding
        super().__init__(16000, channels)
        self.customer_channel = customer_channel
        self.enable_diarization = enable_diarization
        self.model_name = model_name or GCP_TRANSCRIPTION_MODEL
        
        # We set a gap threshold to break long monologues into turns for interlacing
        self.GAP_THRESHOLD = 0.5 
        
        # Determine API endpoint (Chirp requires global/us)
        location = GCP_LOCATION
        endpoint = f"{location}-speech.googleapis.com"
        if "chirp" in self.model_name.lower():
            location = "us"
            endpoint = "us-speech.googleapis.com"
        
        self.client = cs.SpeechAsyncClient(
            client_options=ClientOptions(api_endpoint=endpoint)
        )
        self.api_location = location

    def _print_in_column(self, text, channel, is_final, ts_only=None):
        if self.enable_diarization:
            speaker = f"Speaker {channel}"
        else:
            speaker = "Caller" if (self.customer_channel == f"channel_{channel}") else "Agent"
        
        if is_final:
            text = f"{speaker}: {text}"
            
        super()._print_in_column(text, channel, is_final, ts_only)

    async def run_batch(self, gcs_uri: str):
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        parent = f"projects/{GCP_PROJECT_ID}/locations/{self.api_location}"
        
        # 1. Configure Recognition Features
        mc_mode = cs.RecognitionFeatures.MultiChannelMode.SEPARATE_RECOGNITION_PER_CHANNEL if (self.channels > 1 and not self.enable_diarization) else cs.RecognitionFeatures.MultiChannelMode.MULTI_CHANNEL_MODE_UNSPECIFIED
        
        features = cs.RecognitionFeatures(
            multi_channel_mode=mc_mode,
            enable_word_time_offsets=True, # High-fidelity timestamps
            enable_automatic_punctuation=True,
        )
        
        if self.enable_diarization:
            features.diarization_config = cs.SpeakerDiarizationConfig(min_speaker_count=2, max_speaker_count=2)

        # 2. Prepare Batch Request
        config = cs.RecognitionConfig(
            features=features,
            auto_decoding_config=cs.AutoDetectDecodingConfig(),
            model=self.model_name,
            language_codes=[LANGUAGE_CODE],
        )

        request = cs.BatchRecognizeRequest(
            recognizer=f"{parent}/recognizers/_",
            config=config,
            files=[cs.BatchRecognizeFileMetadata(uri=gcs_uri)],
            # Result set is small enough for inline processing
            recognition_output_config=cs.RecognitionOutputConfig(inline_response_config=cs.InlineOutputConfig())
        )

        logger.info(f"Submitting BatchRecognize request for {gcs_uri}...")
        try:
            operation = await self.client.batch_recognize(request=request)
            logger.info(f"Operation started: {operation.operation.name}. Waiting for results...")
            
            response = await operation.result()
            
            # Extract results from the inline response
            # results[gcs_uri] because we only sent one file
            file_results = response.results[gcs_uri]
            self._process_results(file_results.transcript.results)
        except Exception as e:
            logger.error(f"Batch transcription failed: {e}")

    def _process_results(self, results):
        """Processes and displays the batch results with strict interlacing."""
        all_chunks = []
        for result in results:
            if not result.alternatives: continue
            alt = result.alternatives[0]
            
            # Attribution check
            channel = alt.words[0].speaker_tag if (self.enable_diarization and alt.words) else getattr(result, "channel_tag", 1)
            
            # Split the long transcript into smaller chunks based on silence gaps
            sub_chunks = self._split_by_gaps(alt.words, channel)
            
            if sub_chunks:
                for sc in sub_chunks:
                    # Calculate high-precision timestamp for each sub-chunk
                    ts = self.start_time + datetime.timedelta(seconds=sc['start'])
                    sc['timestamp'] = ts.strftime("%H:%M:%S.%f")[:-5]
                    all_chunks.append(sc)
            else:
                # Fallback if words are missing (unlikely for V2 Batch)
                start_sec = alt.words[0].start_offset.total_seconds() if alt.words else 0
                end_sec = alt.words[-1].end_offset.total_seconds() if alt.words else 0
                ts = self.start_time + datetime.timedelta(seconds=start_sec)
                all_chunks.append({
                    "text": alt.transcript,
                    "start": start_sec,
                    "end": end_sec,
                    "channel": channel,
                    "timestamp": ts.strftime("%H:%M:%S.%f")[:-5]
                })

        # CRITICAL: Final Chronological Sort to interlace Speaker 1 and Speaker 2
        all_chunks.sort(key=lambda x: x['start'])
        
        final_output = []
        for chunk in all_chunks:
            # Format text to match streaming output: [start] "Transcript" [end]
            rel_start = f"{chunk['start']:05.1f}s"
            rel_end = f"{chunk['end']:05.1f}s"
            
            if rel_start != rel_end:
                display_text = f"[{rel_start}] \"{chunk['text']}\" [{rel_end}]"
            else:
                display_text = f"[{rel_start}] \"{chunk['text']}\""
                
            self._print_in_column(display_text, chunk['channel'], is_final=True, ts_only=chunk['timestamp'])
            
            final_output.append({
                "timestamp": chunk['timestamp'],
                "start_sec": chunk['start'],
                "end_sec": chunk['end'],
                "speaker": chunk['channel'],
                "text": chunk['text']
            })

        with open("batch_output.json", "w") as f:
            json.dump(final_output, f, indent=2)
        logger.info("Batch transcription complete. Results saved to batch_output.json")

async def main():
    parser = argparse.ArgumentParser(description="GCS Batch Transcription (STT V2)")
    parser.add_argument("gcs_uri", help="The GCS URI of the audio file")
    parser.add_argument("--customer-channel", default="channel_1")
    parser.add_argument("--diarization", action="store_true")
    parser.add_argument("--model", help="STT model override")

    args = parser.parse_args()

    # Note: We assume 2 channels for comparison demo purposes
    service = BatchTranscriptionService(2, args.customer_channel, 
                                        model_name=args.model, 
                                        enable_diarization=args.diarization)
    
    print(f"\nBATCH MODE: {args.model or 'default'}")
    await service.run_batch(args.gcs_uri)

if __name__ == "__main__":
    asyncio.run(main())
