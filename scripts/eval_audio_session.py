"""Live API BIDI Audio Streaming Evaluator for Cymbal Children's Hospital.

Establishes an active WebSocket connection to the Gemini Live API, streams 16kHz PCM mono audio input,
captures real-time streaming audio response chunks, measures exact audio TTFT latency (ms),
and saves the output WAV audio file to app/logs/eval_output_audio.wav.
"""

import asyncio
import os
import subprocess
import sys
import time
import wave
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Ensure app directory is on PYTHONPATH
project_root = Path(__file__).parent.parent
app_dir = project_root / "app"
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

from google import genai
from google.genai import types


def get_default_gcp_project() -> str:
    """Detect default GCP project ID from environment or gcloud config."""
    project = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("PROJECT_ID")
    if project:
        return project
    try:
        res = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        detected = res.stdout.strip().split()[-1] if res.stdout.strip() else ""
        if detected and not detected.startswith("WARNING"):
            return detected
    except Exception:
        pass
    return "uk-bh-experiments-argolis"


def generate_test_pcm_audio(duration_sec: float = 1.5, sample_rate: int = 16000) -> bytes:
    """Generate a 1.5-second 16kHz PCM 16-bit mono sine wave audio chunk for testing live audio input streaming."""
    import math
    import struct

    frequency = 440.0  # A4 tone
    num_samples = int(duration_sec * sample_rate)
    pcm_bytes = bytearray()

    for i in range(num_samples):
        sample = int(32767.0 * 0.3 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
        pcm_bytes.extend(struct.pack("<h", sample))

    return bytes(pcm_bytes)


def save_pcm_as_wav(pcm_data: bytes, output_wav_path: Path, sample_rate: int = 24000):
    """Save raw 16-bit mono PCM audio data into a standard playable WAV file."""
    output_wav_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output_wav_path), "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit PCM (2 bytes)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)


async def run_live_audio_evaluation():
    print("=" * 75)
    print("🎙️ LIVE API REAL-TIME AUDIO STREAMING & TTFT LATENCY EVALUATOR")
    print("=" * 75)

    api_key = os.getenv("GEMINI_API_KEY")
    gcp_project = get_default_gcp_project()
    location = os.getenv("LOCATION", "us-central1")

    print(f"🔑 Authentication: {'Gemini API Key' if api_key else f'Vertex AI Project ({gcp_project})'}")

    try:
        if api_key:
            client = genai.Client(api_key=api_key)
        else:
            client = genai.Client(vertexai=True, project=gcp_project, location=location)

        model_id = os.getenv("LIVE_MODEL_ID", "gemini-live-2.5-flash-native-audio")
        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
                )
            ),
        )

        print(f"📡 Connecting to Live API WebSocket endpoint ({model_id})...")
        start_time = time.time()

        async with client.aio.live.connect(model=model_id, config=config) as session:
            connection_time = (time.time() - start_time) * 1000
            print(f"✅ WebSocket Connected in {connection_time:.1f}ms")

            # Generate and stream 16kHz PCM audio chunk
            pcm_input = generate_test_pcm_audio(duration_sec=1.5)
            print(f"📤 Streaming {len(pcm_input)} bytes of 16kHz PCM audio input...")
            send_time = time.time()

            await session.send(
                input={
                    "data": pcm_input,
                    "mime_type": "audio/pcm",
                },
                end_of_turn=True,
            )

            received_audio_bytes = bytearray()
            first_audio_chunk_time = None

            async for response in session.receive():
                server_content = response.server_content
                if server_content is not None and server_content.model_turn is not None:
                    for part in server_content.model_turn.parts:
                        if part.inline_data and part.inline_data.data:
                            if first_audio_chunk_time is None:
                                first_audio_chunk_time = time.time()
                            received_audio_bytes.extend(part.inline_data.data)

                if server_content and server_content.turn_complete:
                    break

            total_latency = (first_audio_chunk_time - send_time) * 1000 if first_audio_chunk_time else 0
            out_wav = project_root / "app" / "logs" / "eval_output_audio.wav"
            save_pcm_as_wav(bytes(received_audio_bytes), out_wav, sample_rate=24000)

            print("\n" + "=" * 75)
            print("🎉 LIVE AUDIO STREAMING EVALUATION COMPLETE!")
            print(f"   • Audio Time To First Token (TTFT Latency): {total_latency:.1f}ms")
            print(f"   • Received Output Audio Size: {len(received_audio_bytes)} bytes")
            print(f"   • Saved Playable Audio WAV File: {out_wav}")
            print("=" * 75)

    except Exception as e:
        print(f"\n❌ Live Audio Connection Failed: {e}")


if __name__ == "__main__":
    asyncio.run(run_live_audio_evaluation())
