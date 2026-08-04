import asyncio
import io
import os

# Disable mutual TLS (mTLS) to prevent OpenSSL Context mutation bugs in Python 3.13 / urllib3 on Google corp/cloudtop systems
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
os.environ["GOOGLE_API_USE_MTLS"] = "never"

from pydub import AudioSegment
from google.cloud import texttospeech

async def synthesize_text(text: str, language_code: str, voice_name: str, gender: int) -> AudioSegment:
    """Synthesizes text using Google Cloud Text-to-Speech and returns an AudioSegment."""
    client = texttospeech.TextToSpeechAsyncClient()
    
    input_text = texttospeech.SynthesisInput(text=text)
    
    # Configure the voice request
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
        ssml_gender=gender
    )
    
    # Configure the audio encoding (Linear16 PCM)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000
    )
    
    print(f"Synthesizing: '{text}' ({language_code})...")
    response = await client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )
    
    # Ingest the synthesized bytes into pydub
    return AudioSegment.from_file(io.BytesIO(response.audio_content), format="wav")

async def main():
    # Define dialogue turns with natural 3-second gaps (accounting for translation lag)
    # Caller is Channel 1 (Left Channel), Nurse is Channel 2 (Right Channel)
    
    # Left channel parts (German caller)
    caller_turns = [
        {"start_ms": 0, "text": "Guten Tag. Ich rufe an, weil ich seit heute Morgen sehr starke Kopfschmerzen und etwas Fieber habe.", "voice": "de-DE-Wavenet-B", "gender": texttospeech.SsmlVoiceGender.MALE},
        {"start_ms": 22000, "text": "Nein, mein Nacken fühlt sich normal an, aber das helle Licht schmerzt tatsächlich ein wenig in meinen Augen.", "voice": "de-DE-Wavenet-B", "gender": texttospeech.SsmlVoiceGender.MALE},
        {"start_ms": 49000, "text": "Vielen Dank für den Rat. Ich werde sofort meine Temperatur messen und mich in ein dunkles Zimmer legen.", "voice": "de-DE-Wavenet-B", "gender": texttospeech.SsmlVoiceGender.MALE}
    ]
    
    # Right channel parts (English nurse)
    nurse_turns = [
        {"start_ms": 10000, "text": "Hello, thank you for calling HealthDirect. I am sorry to hear you are feeling unwell. Do you have any neck stiffness or sensitivity to bright light?", "voice": "en-AU-Wavenet-C", "gender": texttospeech.SsmlVoiceGender.FEMALE},
        {"start_ms": 34000, "text": "I understand. Light sensitivity can sometimes indicate a more serious condition. I recommend resting in a dark room and checking your temperature. If your fever goes above thirty-nine degrees, please visit the nearest clinic.", "voice": "en-AU-Wavenet-C", "gender": texttospeech.SsmlVoiceGender.FEMALE},
        {"start_ms": 60000, "text": "You are very welcome. Take care, and please call us back if your symptoms worsen.", "voice": "en-AU-Wavenet-C", "gender": texttospeech.SsmlVoiceGender.FEMALE}
    ]
    
    # Initialize silent tracks of sufficient length (66 seconds)
    total_duration_ms = 66000
    left_channel = AudioSegment.silent(duration=total_duration_ms, frame_rate=16000)
    right_channel = AudioSegment.silent(duration=total_duration_ms, frame_rate=16000)
    
    # Synthesize and overlay left channel (German caller)
    for turn in caller_turns:
        audio = await synthesize_text(turn["text"], "de-DE", turn["voice"], turn["gender"])
        # Overlay at the specific timestamp
        left_channel = left_channel.overlay(audio, position=turn["start_ms"])
        
    # Synthesize and overlay right channel (English nurse)
    for turn in nurse_turns:
        audio = await synthesize_text(turn["text"], "en-AU", turn["voice"], turn["gender"])
        # Overlay at the specific timestamp
        right_channel = right_channel.overlay(audio, position=turn["start_ms"])
        
    # Combine mono channels into a single stereo track
    print("Combining channels into stereo track...")
    stereo_audio = AudioSegment.from_mono_audiosegments(left_channel, right_channel)
    
    # Export locally
    os.makedirs("samples", exist_ok=True)
    out_path = "samples/de_fever_session.wav"
    stereo_audio.export(out_path, format="wav")
    print(f"Bilingual stereo audio file successfully generated locally at: {out_path}")
    
    # Save the output to GCS (optional)
    try:
        from google.cloud import storage
        
        # Export to a bytes buffer
        wav_buffer = io.BytesIO()
        stereo_audio.export(wav_buffer, format="wav")
        wav_buffer.seek(0)
        
        # Upload to GCS
        bucket_name = "uk-bh-experiments-argolis-us"
        gcs_path = "HealthDirect/call_samples/de_fever_session.wav"
        
        print(f"Uploading generated bilingual audio to gs://{bucket_name}/{gcs_path}...")
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(gcs_path)
        blob.upload_from_file(wav_buffer, content_type="audio/wav")
        print(f"Bilingual stereo audio file successfully uploaded to: gs://{bucket_name}/{gcs_path}")
    except Exception as e:
        print(f"Skipping GCS upload (GCS credentials or storage client not configured): {e}")

if __name__ == "__main__":
    asyncio.run(main())
