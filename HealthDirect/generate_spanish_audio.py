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
    # Dialogue turns for Spanish caller & English nurse
    # Padded with silence to form a single conversation
    caller_turns = [
        {"start_ms": 0, "text": "Hola, buenas tardes. Estoy llamando porque mi hijo pequeño tiene dolor de oído muy fuerte y está llorando mucho.", "voice": "es-ES-Wavenet-B", "gender": texttospeech.SsmlVoiceGender.MALE},
        {"start_ms": 16000, "text": "Sí, tiene fiebre de treinta y ocho punto cinco grados. También tiene un resfriado y congestión. ¿El paracetamol es seguro para un niño de dos años?", "voice": "es-ES-Wavenet-B", "gender": texttospeech.SsmlVoiceGender.MALE},
        {"start_ms": 38000, "text": "De acuerdo, muchas gracias. Llevaré a mi hijo al médico de cabecera de inmediato.", "voice": "es-ES-Wavenet-B", "gender": texttospeech.SsmlVoiceGender.MALE}
    ]
    
    nurse_turns = [
        {"start_ms": 8000, "text": "Hello, thank you for calling HealthDirect. My name is Nurse Sarah. I am sorry to hear about your son. Have you noticed any other symptoms, like fluid draining from the ear, or a fever?", "voice": "en-AU-Wavenet-C", "gender": texttospeech.SsmlVoiceGender.FEMALE},
        {"start_ms": 26000, "text": "Yes, paracetamol is safe and recommended for managing pain and fever in a two-year-old child. I recommend visiting your local general practitioner or GP to have his ears checked. If his condition worsens or you see discharge, take him to the Emergency Department.", "voice": "en-AU-Wavenet-C", "gender": texttospeech.SsmlVoiceGender.FEMALE},
        {"start_ms": 44000, "text": "You are very welcome. Take care, and please call us back if your son's symptoms worsen.", "voice": "en-AU-Wavenet-C", "gender": texttospeech.SsmlVoiceGender.FEMALE}
    ]
    
    total_duration_ms = 50000
    left_channel = AudioSegment.silent(duration=total_duration_ms, frame_rate=16000)
    right_channel = AudioSegment.silent(duration=total_duration_ms, frame_rate=16000)
    
    for turn in caller_turns:
        audio = await synthesize_text(turn["text"], "es-ES", turn["voice"], turn["gender"])
        left_channel = left_channel.overlay(audio, position=turn["start_ms"])
        
    for turn in nurse_turns:
        audio = await synthesize_text(turn["text"], "en-AU", turn["voice"], turn["gender"])
        right_channel = right_channel.overlay(audio, position=turn["start_ms"])
        
    print("Combining channels into stereo track...")
    stereo_audio = AudioSegment.from_mono_audiosegments(left_channel, right_channel)
    
    os.makedirs("samples", exist_ok=True)
    out_path = "samples/es_ear_session.wav"
    stereo_audio.export(out_path, format="wav")
    print(f"Bilingual Spanish-English stereo audio file successfully generated at: {out_path}")

if __name__ == "__main__":
    asyncio.run(main())
