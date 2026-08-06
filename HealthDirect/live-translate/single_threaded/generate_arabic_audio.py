import asyncio
import io
import os
import sys

# Disable mutual TLS (mTLS) to prevent OpenSSL Context mutation bugs
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
os.environ["GOOGLE_API_USE_MTLS"] = "never"

from pydub import AudioSegment
from google.cloud import texttospeech

async def synthesize_text(text: str, language_code: str, voice_name: str, gender: int) -> AudioSegment:
    """Synthesizes text using Google Cloud Text-to-Speech and returns an AudioSegment."""
    client = texttospeech.TextToSpeechAsyncClient()
    
    input_text = texttospeech.SynthesisInput(text=text)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
        ssml_gender=gender
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000
    )
    
    print(f"Synthesizing: '{text}' ({language_code})...")
    response = await client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )
    
    return AudioSegment.from_file(io.BytesIO(response.audio_content), format="wav")

async def main():
    # Dialogue turns for Arabic caller & English nurse
    # Padded with silence to form a single conversation
    caller_turns = [
        {"start_ms": 0, "text": "مرحباً، أرجو المساعدة. طفلي البالغ من العمر خمس سنوات يعاني من ضيق شديد في التنفس وصدره يصدر صوت أزيز.", "voice": "ar-XA-Wavenet-B", "gender": texttospeech.SsmlVoiceGender.MALE},
        {"start_ms": 22000, "text": "نعم، لديه تاريخ مع مرض الربو. لقد أعطيته جرعتين من جهاز الاستنشاق باستخدام المباعد قبل قليل، لكنه لا يزال يعاني من صعوبة بالغة في التنفس.", "voice": "ar-XA-Wavenet-B", "gender": texttospeech.SsmlVoiceGender.MALE},
        {"start_ms": 53000, "text": "حسناً، فهمت. سأأخذه إلى قسم الطوارئ فوراً. شكراً جزيلاً لكِ يا ممرضة.", "voice": "ar-XA-Wavenet-B", "gender": texttospeech.SsmlVoiceGender.MALE}
    ]
    
    nurse_turns = [
        {"start_ms": 9000, "text": "Hello, thank you for calling HealthDirect. My name is Nurse Sarah. I am sorry to hear about your son. Does he have a history of asthma? And do you have a bronchodilator inhaler and a spacer with you?", "voice": "en-AU-Wavenet-C", "gender": texttospeech.SsmlVoiceGender.FEMALE},
        {"start_ms": 36000, "text": "Understood. Please call an ambulance immediately or take him straight to your nearest Emergency Department. While you wait, continue administering puffs from the inhaler through the spacer. We are here to support you.", "voice": "en-AU-Wavenet-C", "gender": texttospeech.SsmlVoiceGender.FEMALE},
        {"start_ms": 62000, "text": "You are very welcome. Please stay calm and act quickly. Goodbye.", "voice": "en-AU-Wavenet-C", "gender": texttospeech.SsmlVoiceGender.FEMALE}
    ]
    
    total_duration_ms = 68000
    left_channel = AudioSegment.silent(duration=total_duration_ms, frame_rate=16000)
    right_channel = AudioSegment.silent(duration=total_duration_ms, frame_rate=16000)
    
    for turn in caller_turns:
        audio = await synthesize_text(turn["text"], "ar-XA", turn["voice"], turn["gender"])
        left_channel = left_channel.overlay(audio, position=turn["start_ms"])
        
    for turn in nurse_turns:
        audio = await synthesize_text(turn["text"], "en-AU", turn["voice"], turn["gender"])
        right_channel = right_channel.overlay(audio, position=turn["start_ms"])
        
    print("Combining channels into stereo track...")
    stereo_audio = AudioSegment.from_mono_audiosegments(left_channel, right_channel)
    
    os.makedirs("samples", exist_ok=True)
    out_path = "samples/ar_asthma_session.wav"
    stereo_audio.export(out_path, format="wav")
    print(f"Bilingual Arabic-English stereo audio file successfully generated at: {out_path}")

if __name__ == "__main__":
    asyncio.run(main())
