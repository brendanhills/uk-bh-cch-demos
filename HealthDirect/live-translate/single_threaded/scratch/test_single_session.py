import asyncio
import os
from google import genai
from google.genai import types
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"

async def test_streaming():
    client = genai.Client()
    
    # Load raw audio segment for Patient Turn 3 (23.5s to 30.1s)
    seg = AudioSegment.from_file('samples/paediatric_vietnamese_demo.wav')
    # Convert to mono, 16kHz, 16-bit PCM
    seg = seg.set_frame_rate(16000).set_sample_width(2).split_to_mono()[0]
    
    # Slice Patient Turn 3
    turn_3_seg = seg[23500:30100]
    raw_bytes = turn_3_seg.raw_data
    chunk_size = 3200
    
    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        system_instruction=types.Content(
            parts=[types.Part.from_text(text="You are a medical interpreter. Translate Vietnamese to English.")]
        ),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        realtime_input_config=types.RealtimeInputConfig(
            automatic_activity_detection=types.AutomaticActivityDetection(
                silence_duration_ms=400
            )
        ),
    )
    
    async def run_turn(turn_idx, audio_data):
        print(f"\n--- STARTING TURN {turn_idx} (Fresh Connection) ---")
        config = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            system_instruction=types.Content(
                parts=[types.Part.from_text(text="You are a medical interpreter. Translate Vietnamese to English.")]
            ),
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            realtime_input_config=types.RealtimeInputConfig(
                automatic_activity_detection=types.AutomaticActivityDetection(
                    silence_duration_ms=400
                )
            ),
        )
        
        print(f"Connecting to Gemini Live session for Turn {turn_idx}...")
        async with client.aio.live.connect(model="gemini-3.1-flash-live-preview", config=config) as session:
            print(f"Connected for Turn {turn_idx}!")
            
            translation_complete = asyncio.Event()
            
            async def receive_responses():
                try:
                    async for response in session.receive():
                        server_content = response.server_content
                        if server_content:
                            if server_content.model_turn:
                                for part in server_content.model_turn.parts:
                                    if part.text:
                                        print(f"[TURN {turn_idx} TRANSLATION]: {part.text}")
                            if server_content.input_transcription and server_content.input_transcription.text:
                                print(f"[TURN {turn_idx} ORIGINAL]: {server_content.input_transcription.text}")
                            if server_content.turn_complete:
                                print(f"[TURN {turn_idx} COMPLETE EVENT]")
                                translation_complete.set()
                except Exception as e:
                    print(f"Receiver error on Turn {turn_idx}: {e}")
                    
            receiver_task = asyncio.create_task(receive_responses())
            
            print(f"Streaming Turn {turn_idx} audio chunks...")
            for idx in range(0, len(audio_data), chunk_size):
                chunk = audio_data[idx:idx+chunk_size]
                await session.send_realtime_input(
                    audio=types.Blob(data=chunk, mime_type="audio/pcm;rate=16000")
                )
                await asyncio.sleep(0.1)
                
            print(f"Finished streaming audio chunks for Turn {turn_idx}. Streaming silence to let VAD trigger...")
            silence_chunk = b'\x00' * chunk_size
            for _ in range(50):
                await session.send_realtime_input(
                    audio=types.Blob(data=silence_chunk, mime_type="audio/pcm;rate=16000")
                )
                await asyncio.sleep(0.1)
                
            print(f"Waiting for Turn {turn_idx} translation to complete...")
            try:
                await asyncio.wait_for(translation_complete.wait(), timeout=15)
            except asyncio.TimeoutError:
                print(f"⚠️ Turn {turn_idx} translation wait timed out!")
                
            receiver_task.cancel()
            print(f"Turn {turn_idx} session closed.")

    # Run Turn 1 using Patient Turn 3 audio
    await run_turn(1, raw_bytes)
    
    # Simulate some natural inactive pause
    print("\n--- SIMULATING INACTIVE TURN 2 (5 seconds of pause) ---")
    await asyncio.sleep(5)
    
    # Run Turn 3 (Turn 2 of the Patient) using Patient Turn 3 audio again
    await run_turn(2, raw_bytes)

if __name__ == '__main__':
    asyncio.run(test_streaming())
