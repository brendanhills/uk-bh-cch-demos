import asyncio
import io
import os
from pydub import AudioSegment
from google.cloud.storage import Client as StorageClient

SAMPLES = [
    "gs://uk-bh-experiments-argolis-us/capita/test_test-transcript-connector.wav",
    "gs://uk-bh-experiments-argolis-us/capita/resources_sample-calls.mp3",
    "gs://uk-bh-experiments-argolis-us/capita/speech_medical_conversation_2.wav",
    "gs://uk-bh-experiments-argolis-us/capita/4507.mp3",
    "gs://uk-bh-experiments-argolis-us/capita/4520.mp3"
]

async def analyze_file(uri):
    print(f"Analyzing {uri}...")
    storage_client = StorageClient()
    try:
        if uri.startswith("gs://"):
            bucket_name, blob_name = uri.replace("gs://", "").split("/", 1)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            data = blob.download_as_bytes()
        else:
            with open(uri, "rb") as f:
                data = f.read()
        
        audio = AudioSegment.from_file(io.BytesIO(data))
        
        print(f"  Channels: {audio.channels}")
        print(f"  Sample Rate: {audio.frame_rate} Hz")
        print(f"  Duration: {len(audio)/1000:.2f} s")
        
        status = "Unknown"
        if audio.channels == 1:
            status = "Mono"
        elif audio.channels == 2:
            left, right = audio.split_to_mono()
            if left.raw_data == right.raw_data:
                status = "Stereo (Identical Channels / Fake Stereo)"
            else:
                status = "Stereo (Distinct Channels / True Dual Channel)"
        else:
            status = f"Multi-channel ({audio.channels})"
            
        print(f"  Type: {status}")
        print("-" * 40)
        
    except Exception as e:
        print(f"  Error: {e}")
        print("-" * 40)

async def main():
    import sys
    
    # If a file is passed as an argument, analyze just that one
    if len(sys.argv) > 1:
        target_samples = sys.argv[1:]
    else:
        target_samples = SAMPLES

    print("="*60)
    print("AUDIO SAMPLE ANALYSIS")
    print("="*60)
    for uri in target_samples:
        await analyze_file(uri)

if __name__ == "__main__":
    asyncio.run(main())
