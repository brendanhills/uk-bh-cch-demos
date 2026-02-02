import asyncio
import os
import logging
import time
from transcribe_common import TranscriptionService
from google.cloud import speech_v1 as speech

# Configure logging
logging.basicConfig(level=logging.ERROR) 
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MODELS_TO_TEST = [
    "long",
    "telephony",
    "chirp",
    "chirp-2",
]

TEST_URI = "gs://uk-bh-experiments-argolis-us/capita/4520.mp3"

async def test_v1_diarization(audio_bytes):
    print("\nTesting V1 API with Diarization...")
    client = speech.SpeechAsyncClient()
    
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=8000,
        language_code="en-US",
        diarization_config=speech.SpeakerDiarizationConfig(
            enable_speaker_diarization=True,
            min_speaker_count=2,
            max_speaker_count=2,
        ),
        model="phone_call",
        use_enhanced=True,
    )
    streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)

    async def request_generator():
        yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)
        # Send approx 5 seconds of real audio
        chunk_size = 1600 
        for i in range(0, min(len(audio_bytes), 80000), chunk_size):
            yield speech.StreamingRecognizeRequest(audio_content=audio_bytes[i:i+chunk_size])
            await asyncio.sleep(0.01) 
        print("DEBUG: V1 request_generator finished sending audio.")

    try:
        responses = await client.streaming_recognize(requests=request_generator())
        print("DEBUG: V1 streaming_recognize called, waiting for responses...")
        async with asyncio.timeout(15.0):
            async for response in responses:
                if response.results:
                    print(f"DEBUG: V1 response received with {len(response.results)} results")
                    print("✅ V1 API STARTED successfully.")
                    return True
        print("❌ V1 API: Loop finished without any response.")
        return False
    except asyncio.TimeoutError:
        print("❌ V1 API FAILED: Timed out waiting for response.")
        return False
    except Exception as e:
        print(f"❌ V1 API FAILED: {e}")
        return False

async def test_v2_model(model_name):
    print(f"\nTesting V2 model: {model_name}...")
    safe_name = model_name.replace("_", "-")
    rec_id = f"test-rec-{safe_name}-{int(time.time())}"
    
    service = TranscriptionService(
        gcs_uri=TEST_URI,
        buffer_timeout=0.1,
        enable_multi_channel=False,
        enable_diarization=True,
        recognizer_id=rec_id,
        model_name=model_name
    )
    
    try:
        recognizer = await service.get_recognizer()
        await service.prepare_audio()
        
        async def short_stream():
            await service.audio_q.put(service.audio_bytes[:16000]) # ~0.5s
            await service.audio_q.put(None)

        asyncio.create_task(short_stream())
        
        responses_stream = await service.client.streaming_recognize(
            requests=service.generate_requests(recognizer.name)
        )
        
        async with asyncio.timeout(10.0):
            async for response in responses_stream:
                print(f"✅ V2 Model '{model_name}' STARTED successfully.")
                return True
    except Exception as e:
        print(f"❌ V2 Model '{model_name}' FAILED: {e}")
        return False

async def main():
    print("Starting Multi-API Compatibility Test...")
    
    # Download audio once
    v2_service = TranscriptionService(gcs_uri=TEST_URI)
    await v2_service.prepare_audio()
    audio_data = v2_service.audio_bytes

    results = {}
    
    # Test V1
    v1_success = await test_v1_diarization(audio_data)
    results["V1 (phone_call)"] = "Pass" if v1_success else "Fail"
    
    # Test V2 Models
    for model in MODELS_TO_TEST:
        success = await test_v2_model(model)
        results[f"V2 ({model})"] = "Pass" if success else "Fail"
    
    print("\n--- Summary ---")
    for test, status in results.items():
        print(f"{test:<30}: {status}")

if __name__ == "__main__":
    asyncio.run(main())