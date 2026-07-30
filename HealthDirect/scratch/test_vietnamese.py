import os
import asyncio
import base64
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydub import AudioSegment

load_dotenv()

async def run_direction_test(direction, audio_channel, target_lang, sys_inst):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not configured in env.")
        return

    client = genai.Client(api_key=api_key)
    model_name = "gemini-3.5-live-translate-preview"
    
    # Load and process Vietnamese audio
    audio_path = "samples/paediatric_vietnamese_demo.wav"
    if not os.path.exists(audio_path):
        print(f"❌ Error: {audio_path} not found.")
        return
        
    seg = AudioSegment.from_file(audio_path)
    seg = seg.set_frame_rate(16000).set_sample_width(2)
    
    # Split to get specified channel
    if seg.channels == 2:
        left, right = seg.split_to_mono()
        mono_seg = left if audio_channel == "left" else right
    else:
        mono_seg = seg
        
    audio_bytes = mono_seg.raw_data
    # Use first 10 seconds for a quick test
    stream_bytes = audio_bytes[:10 * 32000]

    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        system_instruction=types.Content(
            parts=[types.Part.from_text(text=sys_inst)]
        ),
        translation_config=types.TranslationConfig(
            target_language_code=target_lang,
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

    print(f"\n🚀 Testing {direction}: target_lang={target_lang}...")
    try:
        async with client.aio.live.connect(model=model_name, config=config) as session:
            print(f"✅ Connection successful for {direction}")

            async def receive_loop():
                try:
                    async for response in session.receive():
                        server_content = response.server_content
                        if server_content:
                            if server_content.model_turn:
                                for part in server_content.model_turn.parts:
                                    if part.text:
                                        print(f"💬 [{direction} MODEL TEXT]: {part.text}")
                                    if part.inline_data:
                                        print(f"🔊 [{direction} AUDIO DATA]: {len(part.inline_data.data)} bytes")
                            if server_content.input_transcription and server_content.input_transcription.text:
                                print(f"📝 [{direction} INPUT]: {server_content.input_transcription.text}")
                            if server_content.output_transcription and server_content.output_transcription.text:
                                print(f"📝 [{direction} OUTPUT]: {server_content.output_transcription.text}")
                except Exception as e:
                    print(f"❌ [{direction} RECEIVE ERROR]: {e}")

            async def send_loop():
                try:
                    chunk_size = int(32000 * 0.2)
                    for i in range(0, len(stream_bytes), chunk_size):
                        chunk = stream_bytes[i : i + chunk_size]
                        await session.send_realtime_input(
                            audio=types.Blob(data=chunk, mime_type="audio/pcm;rate=16000")
                        )
                        await asyncio.sleep(0.2)
                    print(f"🏁 [{direction} SENDING COMPLETE] Waiting for responses...")
                    await asyncio.sleep(6.0)
                except Exception as e:
                    print(f"❌ [{direction} SEND ERROR]: {e}")

            await asyncio.gather(receive_loop(), send_loop())
    except Exception as e:
        print(f"❌ [{direction} CONNECTION CRASHED]: {e}")

async def main():
    # 1. Test Patient -> Nurse (Vietnamese -> English)
    await run_direction_test(
        direction="Patient->Nurse (vi->en)",
        audio_channel="left",
        target_lang="en",
        sys_inst="You are a professional interpreter. Translate Vietnamese to English."
    )
    
    # 2. Test Nurse -> Patient (English -> Vietnamese)
    await run_direction_test(
        direction="Nurse->Patient (en->vi)",
        audio_channel="right",
        target_lang="vi",
        sys_inst="You are a professional interpreter. Translate English to Vietnamese."
    )

if __name__ == "__main__":
    asyncio.run(main())
