import asyncio
import io
import os
import json
import re
import sys
import wave

# Disable mutual TLS (mTLS) to prevent OpenSSL Context mutation bugs
# on Google corp machines.
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
os.environ["GOOGLE_API_USE_MTLS"] = "never"

from pydub import AudioSegment
from google.cloud import texttospeech
from google.cloud import storage

# Standardized Voice Mappings
VOICE_MAPPING = {
    "german": {
        "caller": {
            "language_code": "de-DE",
            "voice_name": "de-DE-Wavenet-B",
            "gender": texttospeech.SsmlVoiceGender.MALE,
            "fallback_voice": "de-DE-Neural2-F"
        },
        "nurse": {
            "language_code": "en-AU",
            "voice_name": "en-AU-Wavenet-C",
            "gender": texttospeech.SsmlVoiceGender.FEMALE,
            "fallback_voice": "en-AU-Neural2-F"
        }
    },
    "spanish": {
        "caller": {
            "language_code": "es-ES",
            "voice_name": "es-ES-Wavenet-B",
            "gender": texttospeech.SsmlVoiceGender.MALE,
            "fallback_voice": "es-ES-Neural2-F"
        },
        "nurse": {
            "language_code": "en-AU",
            "voice_name": "en-AU-Wavenet-C",
            "gender": texttospeech.SsmlVoiceGender.FEMALE,
            "fallback_voice": "en-AU-Neural2-F"
        }
    },
    "vietnamese": {
        "caller": {
            "language_code": "vi-VN",
            "voice_name": "vi-VN-Wavenet-A",
            "gender": texttospeech.SsmlVoiceGender.FEMALE,
            "fallback_voice": "vi-VN-Neural2-A"
        },
        "nurse": {
            "language_code": "en-AU",
            "voice_name": "en-AU-Wavenet-C",
            "gender": texttospeech.SsmlVoiceGender.FEMALE,
            "fallback_voice": "en-AU-Neural2-F"
        }
    },
    "arabic": {
        "caller": {
            "language_code": "ar-XA",
            "voice_name": "ar-XA-Wavenet-B",
            "gender": texttospeech.SsmlVoiceGender.MALE,
            "fallback_voice": "ar-XA-Wavenet-C"
        },
        "nurse": {
            "language_code": "en-AU",
            "voice_name": "en-AU-Wavenet-C",
            "gender": texttospeech.SsmlVoiceGender.FEMALE,
            "fallback_voice": "en-AU-Neural2-F"
        }
    },
    "hindi_cough": {
        "caller": {
            "language_code": "hi-IN",
            "voice_name": "hi-IN-Wavenet-B",
            "gender": texttospeech.SsmlVoiceGender.MALE,
            "fallback_voice": "hi-IN-Neural2-B"
        },
        "nurse": {
            "language_code": "en-AU",
            "voice_name": "en-AU-Wavenet-C",
            "gender": texttospeech.SsmlVoiceGender.FEMALE,
            "fallback_voice": "en-AU-Neural2-F"
        }
    }
}

# Key medical terms to programmatically emphasize
SYMPTOM_KEYWORDS = [
    "kopfschmerzen", "fieber", "schmerzen",
    "dolor de oído", "dolor", "fiebre",
    "sốt cao", "thở rất khò khè", "lồng ngực cứ phập phồng", "mệt",
    "जकड़न", "तकलीफ", "सूखी खांसी", "बुखार", "भारीपन"
]


def format_ssml_text(text: str) -> str:
    """Wraps text in emotional SSML tags with prosody, pitch, and emphasis.

    Args:
        text: The raw input transcription text to wrap with SSML.

    Returns:
        The formatted SSML speak block string.
    """
    # Inject breathing break tags around clause punctuation
    processed = text.replace(", ", ", <break time=\"500ms\"/> ")
    processed = processed.replace(". ", ". <break time=\"500ms\"/> ")
    
    # Sort symptom keywords by length descending to match larger phrases first
    sorted_keywords = sorted(SYMPTOM_KEYWORDS, key=len, reverse=True)
    
    for kw in sorted_keywords:
        # Match whole words/phrases case-insensitively using unicode bounds.
        pattern = re.compile(
            rf'(?<![a-zA-Z0-9à-üÀ-ÜáéíóúÁÉÍÓÚñÑ])'
            rf'({re.escape(kw)})'
            rf'(?![a-zA-Z0-9à-üÀ-ÜáéíóúÁÉÍÓÚñÑ])',
            re.IGNORECASE
        )
        processed = pattern.sub(
            r'<emphasis level="moderate">\1</emphasis>',
            processed
        )
        
    return (
        f'<speak><prosody rate="85%" pitch="-2st">'
        f'{processed}'
        f'</prosody></speak>'
    )


async def synthesize_voice(
    text: str,
    is_caller: bool,
    preset_key: str,
    use_ssml: bool = True
) -> AudioSegment:
    """Synthesizes speech using Text-to-Speech Async Client.

    Caller (patient) voices are programmatically geared with SSML if
    use_ssml=True. Falls back to stable default Neural2 voices without
    SSML in case of synthesis failures.

    Args:
        text: The source text to synthesize.
        is_caller: True if synthesizing patient/caller voice, False for nurse.
        preset_key: The language preset configuration key.
        use_ssml: Whether to wrap caller text with slow & low SSML tags.

    Returns:
        An AudioSegment of the synthesized audio bytes.
    """
    client = texttospeech.TextToSpeechAsyncClient()
    role = "caller" if is_caller else "nurse"
    
    config = VOICE_MAPPING.get(preset_key, VOICE_MAPPING["german"])[role]
    language_code = config["language_code"]
    voice_name = config["voice_name"]
    gender = config["gender"]
    
    # Configure Synthesis input
    if is_caller and use_ssml:
        ssml_content = format_ssml_text(text)
        print(f"[{role.upper()}] Synthesizing with SSML: "
              f"{ssml_content[:55]}...")
        input_data = texttospeech.SynthesisInput(ssml=ssml_content)
    else:
        print(f"[{role.upper()}] Synthesizing standard text: "
              f"{text[:55]}...")
        input_data = texttospeech.SynthesisInput(text=text)
        
    voice_params = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
        ssml_gender=gender
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000
    )
    
    try:
        response = await client.synthesize_speech(
            input=input_data, voice=voice_params, audio_config=audio_config
        )
        return AudioSegment.from_file(
            io.BytesIO(response.audio_content),
            format="wav"
        )
    except Exception as e:
        print(f"[WARNING] Synthesis failed for voice {voice_name}: {e}. "
              f"Retrying with Neural2 fallback...")
        fallback_params = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=config["fallback_voice"],
            ssml_gender=gender
        )
        # Force text synthesis (no SSML) to guarantee a stable exit
        fallback_input = texttospeech.SynthesisInput(text=text)
        response = await client.synthesize_speech(
            input=fallback_input,
            voice=fallback_params,
            audio_config=audio_config
        )
        return AudioSegment.from_file(
            io.BytesIO(response.audio_content),
            format="wav"
        )


async def compile_simultaneous_stereo_wav(
    metadata_path: str,
    tail_buffer_ms: int = 2500
) -> str:
    """Reads metadata JSON, compiles Left and Right audio segments.

    Ensures precise channel separation and lockstep chronological pacing.

    Args:
        metadata_path: Path to the dialogue session metadata JSON file.
        tail_buffer_ms: Pacing silence buffer appended after each turn in ms.

    Returns:
        The output path of the compiled stereo WAV file.
    """
    with open(metadata_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    preset_key = data["metadata"]["preset_key"]
    turns = data["turns"]
    
    base_meta = os.path.basename(metadata_path)
    print(f"\n--- Compiling Scenario: {preset_key.upper()} "
          f"(Metadata: {base_meta}) ---")
    
    # Phase 1: Synthesize all turns and track their actual durations
    synthesized_turns = []
    total_estimated_duration = 1000 # initial 1.0s lead-in
    
    for turn in turns:
        is_caller = (turn["speaker"] == "caller" or
                     turn["speaker"] == "patient")
        # Synthesize audio segment
        audio_segment = await synthesize_voice(
            turn["text"],
            is_caller,
            preset_key
        )
        duration_ms = len(audio_segment)
        
        synthesized_turns.append({
            "speaker": turn["speaker"],
            "is_caller": is_caller,
            "audio": audio_segment,
            "duration_ms": duration_ms,
            "original_turn": turn
        })
        # Add spacing for playback pacing
        total_estimated_duration += duration_ms + tail_buffer_ms
        
    print(f"[Timeline] Estimated Total Duration: "
          f"{total_estimated_duration / 1000:.2f}s")
    
    # Initialize silent mono channel canvas tracks
    left_channel = AudioSegment.silent(
        duration=total_estimated_duration,
        frame_rate=16000
    )
    right_channel = AudioSegment.silent(
        duration=total_estimated_duration,
        frame_rate=16000
    )
    
    # Compile the lockstep timeline
    current_time_ms = 1000  # Starts with 1.0s lead-in silence
    new_turns_metadata = []
    
    for idx, item in enumerate(synthesized_turns):
        duration = item["duration_ms"]
        original = item["original_turn"]
        
        print(f"  Turn {idx+1}: {item['speaker'].upper()} "
              f"starts at {current_time_ms/1000:.2f}s "
              f"(len={duration/1000:.2f}s)")
        
        # Overlay turn onto correct mono channel
        if item["is_caller"]:
            left_channel = left_channel.overlay(
                item["audio"],
                position=current_time_ms
            )
        else:
            right_channel = right_channel.overlay(
                item["audio"],
                position=current_time_ms
            )
            
        # Record new updated start time for metadata sync
        updated_turn = original.copy()
        updated_turn["start_ms"] = current_time_ms
        new_turns_metadata.append(updated_turn)
        
        # Advance playhead by actual duration + 2.5s tail silence
        current_time_ms += duration + tail_buffer_ms
        
    # Trim excess silence from canvas
    total_conversational_duration = current_time_ms + 500  # add 500ms tail pad
    left_channel = left_channel[:total_conversational_duration]
    right_channel = right_channel[:total_conversational_duration]
    
    # Merge channels into dual-channel stereo output
    print("[Timeline] Blending left and right tracks into stereo...")
    stereo_audio = AudioSegment.from_mono_audiosegments(
        left_channel,
        right_channel
    )
    
    # Save Wav file
    os.makedirs("samples", exist_ok=True)
    base_name = os.path.splitext(os.path.basename(metadata_path))[0]
    out_wav_path = f"samples/{base_name}.wav"
        
    stereo_audio.export(out_wav_path, format="wav")
    print(f"[Timeline] Completed! Saved stereo wav to: {out_wav_path}")
    
    # Rewrite original metadata JSON with perfectly synchronized timeline values
    data["turns"] = new_turns_metadata
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[Timeline] Synchronized JSON metadata saved to: {metadata_path}")
    
    return out_wav_path


def upload_to_gcs(
    local_file_path: str,
    bucket_name: str,
    destination_blob_name: str
):
    """Gracefully uploads compiled WAV file to Google Cloud Storage.

    Args:
        local_file_path: Absolute local path to compiled stereo WAV file.
        bucket_name: Name of target GCS bucket.
        destination_blob_name: Path of target cloud storage object blob.
    """
    base_file = os.path.basename(local_file_path)
    print(f"[GCS] Attempting upload of {base_file} to "
          f"gs://{bucket_name}/{destination_blob_name}...")
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_file_path)
        print(f"[GCS] Upload successful!")
    except Exception as e:
        print(f"[GCS-SKIP] Skipping cloud upload: {e}. "
              f"(This is normal if credentials are not configured locally).")


async def main():
    metadata_files = [
        "samples/scripts/de_fever_session.json",
        "samples/scripts/es_ear_session.json",
        "samples/scripts/vi_paediatric_session.json",
        "samples/scripts/ar_asthma_session.json",
        "samples/scripts/hi_cough_session.json"
    ]
    
    bucket_name = "uk-bh-experiments-argolis-us"
    
    for meta_path in metadata_files:
        if not os.path.exists(meta_path):
            print(f"[ERROR] Metadata file not found at: {meta_path}. Skipping.")
            continue
            
        try:
            # Compile WAV and update timeline JSON
            wav_path = await compile_simultaneous_stereo_wav(meta_path)
            
            # Sync GCS
            wav_name = os.path.basename(wav_path)
            blob_name = f"HealthDirect/call_samples/{wav_name}"
            upload_to_gcs(wav_path, bucket_name, blob_name)
        except Exception as e:
            print(f"[ERROR] Failed to compile scenario for {meta_path}: {e}")
            
    print("\n--- PROGRAMMATIC SIMULTANEOUS AUDIO SYNTHESIS COMPLETE ---")


if __name__ == "__main__":
    asyncio.run(main())
