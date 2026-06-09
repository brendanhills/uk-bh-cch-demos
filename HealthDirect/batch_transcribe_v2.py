"""
Batch Transcription Demo (STT V2)

This script processes an entire audio file stored in GCS using the 
BatchRecognize API. It provides a full, non-streaming transcription 
suitable for ground-truth comparison.

Even though this is an 'offline' process, it uses the same Engine and 
Models as the streaming demos to ensure consistent output formatting.
"""

import argparse
import asyncio
import os
import json
import datetime
from google.cloud import speech_v2 as cs
from google.api_core.client_options import ClientOptions
from core.models import TranscriptionEvent
from core.engine import TranscriptionEngine
from core.sinks import TerminalSink, RealTimeJsonSink

async def run_batch(args):
    # 1. Pipeline Setup
    engine = TranscriptionEngine()
    terminal = TerminalSink()
    
    # Standardized output path
    audio_base = os.path.basename(args.gcs_uri)
    output_path = f"output/{audio_base}_batch_v2.json"
    json_log = RealTimeJsonSink(output_path)
    json_log.open()
    
    engine.add_sink(terminal.emit)
    engine.add_sink(json_log.emit)

    # 2. Configure Client
    project = os.getenv("PROJECT_ID")
    location = os.getenv("LOCATION", "us-central1")
    model = args.model or "telephony"
    
    if "chirp" in model.lower() or "medical" in model.lower():
        api_endpoint, location = "us-speech.googleapis.com", "us"
    else:
        api_endpoint = f"{location}-speech.googleapis.com"

    client = cs.SpeechAsyncClient(client_options=ClientOptions(api_endpoint=api_endpoint))
    parent = f"projects/{project}/locations/{location}"

    # 3. Build Request
    # Determine multi-channel mode
    mc_mode = cs.RecognitionFeatures.MultiChannelMode.SEPARATE_RECOGNITION_PER_CHANNEL if not args.diarization else None
    
    features = cs.RecognitionFeatures(
        multi_channel_mode=mc_mode,
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,
    )
    if args.diarization:
        features.diarization_config = cs.SpeakerDiarizationConfig(min_speaker_count=2, max_speaker_count=2)

    config = cs.RecognitionConfig(
        features=features,
        auto_decoding_config=cs.AutoDetectDecodingConfig(),
        model=model,
        language_codes=["en-US"],
    )

    request = cs.BatchRecognizeRequest(
        recognizer=f"{parent}/recognizers/_",
        config=config,
        files=[cs.BatchRecognizeFileMetadata(uri=args.gcs_uri)],
        recognition_output_config=cs.RecognitionOutputConfig(inline_response_config=cs.InlineOutputConfig())
    )

    # 4. Execute
    print(f"\nSUBMITTING BATCH REQUEST: {args.gcs_uri}")
    try:
        operation = await client.batch_recognize(request=request)
        print(f"Operation started: {operation.operation.name}. Waiting for results...")
        response = await operation.result()
        
        # results[uri] contains the transcript
        file_results = response.results[args.gcs_uri]
        
        # 5. Process results through the Engine
        # This ensures they are gap-split and sorted identically to the streaming demo
        for result in file_results.transcript.results:
            if not result.alternatives: continue
            alt = result.alternatives[0]
            
            speaker = alt.words[0].speaker_tag if (args.diarization and alt.words) else getattr(result, "channel_tag", 1)
            start = alt.words[0].start_offset.total_seconds() if alt.words else 0
            end = alt.words[-1].end_offset.total_seconds() if alt.words else 0

            event = TranscriptionEvent(
                speaker_id=speaker,
                text=alt.transcript,
                start_sec=start,
                end_sec=end,
                is_final=True,
                words=[{
                    "word": w.word, 
                    "start": w.start_offset.total_seconds(),
                    "end": w.end_offset.total_seconds()
                } for w in alt.words]
            )
            engine.process_raw_event(event)
            
    except Exception as e:
        print(f"Batch transcription failed: {e}")
    finally:
        engine.shutdown()
        json_log.close()
        print(f"\nBatch transcription complete. Results: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GCS Batch Transcription (STT V2)")
    parser.add_argument("gcs_uri", help="The GCS URI of the audio file (must be gs://...)")
    parser.add_argument("--diarization", action="store_true")
    parser.add_argument("--model", help="STT model override")
    
    args = parser.parse_args()
    if not args.gcs_uri.startswith("gs://"):
        print("Error: Batch transcription requires a GCS URI (gs://...)")
    else:
        asyncio.run(run_batch(args))
