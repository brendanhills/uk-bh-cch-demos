import os
import asyncio
import base64
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydub import AudioSegment

load_dotenv()

async def run_test():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not configured in env.")
        return

    client = genai.Client(api_key=api_key)
    model_name = "gemini-3.5-live-translate-preview"
    
    # Load and process English audio (Nurse speaking)
    audio_path = "samples/es_ear_session.wav"
    if not os.path.exists(audio_path):
        print(f"❌ Error: {audio_path} not found.")
        return
        
    print(f"Loading {audio_path}...")
    seg = AudioSegment.from_file(audio_path)
    seg = seg.set_frame_rate(16000).set_sample_width(2)
    # Split to get Right channel (Nurse speaking English)
    if seg.channels == 2:
        _, right_mono = seg.split_to_mono()
    else:
        right_mono = seg
        
    audio_bytes = right_mono.raw_data
    print(f"Audio loaded: {len(audio_bytes)} bytes ({len(audio_bytes)/32000:.2f} seconds).")

    # Connect with TranslationConfig and system instruction
    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        system_instruction=types.Content(
            parts=[types.Part.from_text(text="You are a professional medical interpreter. Translate English to Spanish accurately.")]
        ),
        translation_config=types.TranslationConfig(
            target_language_code="es",
            echo_target_language=True
        ),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        realtime_input_config=types.RealtimeInputConfig(
            automatic_activity_detection=types.AutomaticActivityDetection(
                silence_duration_ms=400
            )
        )
    )

    print("Connecting to Gemini Live...")
    async with client.aio.live.connect(model=model_name, config=config) as session:
        print("✅ Session established!")

        async def receive_loop():
            try:
                async for response in session.receive():
                    server_content = response.server_content
                    if server_content:
                        if server_content.model_turn:
                            for part in server_content.model_turn.parts:
                                if part.text:
                                    print(f"💬 [MODEL PART TEXT]: {part.text}")
                                if part.inline_data:
                                    print(f"🔊 [AUDIO DATA]: {len(part.inline_data.data)} bytes")
                        if server_content.input_transcription and server_content.input_transcription.text:
                            print(f"📝 [INPUT TRANSCRIPTION]: {server_content.input_transcription.text} (finished={server_content.input_transcription.finished})")
                        if server_content.output_transcription and server_content.output_transcription.text:
                            print(f"📝 [OUTPUT TRANSCRIPTION]: {server_content.output_transcription.text}")
                        if server_content.turn_complete:
                            print("🏁 [TURN COMPLETE] Received!")
                        if server_content.interrupted:
                            print("⚠️ [INTERRUPTED] Received!")
            except Exception as e:
                print(f"❌ Error in receive loop: {e}")

        async def send_loop():
            try:
                # Stream first 12 seconds of Spanish speech
                # 32000 bytes per second for 16kHz 16-bit mono
                stream_bytes = audio_bytes[:12 * 32000]
                chunk_size = int(32000 * 0.2) # 200ms chunks = 6400 bytes
                
                print("Streaming audio chunks...")
                for i in range(0, len(stream_bytes), chunk_size):
                    chunk = stream_bytes[i : i + chunk_size]
                    await session.send_realtime_input(
                        audio=types.Blob(data=chunk, mime_type="audio/pcm;rate=16000")
                    )
                    await asyncio.sleep(0.2)
                
                print("Finished streaming audio. Entering hold/silence state...")
                # Hold and do nothing for 10 seconds to see if translation is produced or if it crashes
                await asyncio.sleep(10.0)
                print("Finished hold state.")
            except Exception as e:
                print(f"❌ Error in send loop: {e}")

        # Run send and receive in parallel
        await asyncio.gather(receive_loop(), send_loop())

if __name__ == "__main__":
    asyncio.run(run_test())
