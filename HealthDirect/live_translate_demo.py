#!/usr/bin/env python3
"""
Live Translate Demo - Real-Time Bidirectional Bilingual Medical Interpreter
Specifically utilizes the dedicated Gemini Live Translate API to translate
real-time multi-channel conversation between a Patient and a Clinician.
"""

import asyncio
import os
import sys
import argparse
import logging
from dotenv import load_dotenv
from pydub import AudioSegment

# Force standard TLS/HTTPS to prevent client certificate/mTLS issues
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"

from google import genai
from google.genai import types
from glossary_highlighter import GlossaryHighlighter

# Load environment variables
load_dotenv()

# Initialize global glossary highlighter
highlighter = GlossaryHighlighter()

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("live_translate_demo")
logger.setLevel(logging.INFO)

# Define preset medical call files
PRESETS = {
    "german": {
        "file": "samples/de_fever_session.wav",
        "code": "de",
        "language": "German"
    },
    "spanish": {
        "file": "samples/es_ear_session.wav",
        "code": "es",
        "language": "Spanish"
    },
    "vietnamese": {
        "file": "samples/paediatric_vietnamese_demo.wav",
        "code": "vi",
        "language": "Vietnamese"
    }
}

def print_border():
    print("=" * 114)

def print_row(col1: str, col2: str, language: str = None):
    """
    Renders two strings side-by-side in an aligned double-column grid.
    If language is provided, clinical glossary terms are highlighted:
    - English in col1 (bold green)
    - Target language in col2 (bold magenta)
    """
    import re
    
    c1_width = 54
    c2_width = 54
    
    # Highlight before wrapping if language is specified
    if language:
        col1 = highlighter.highlight_cli(col1, "english")
        col2 = highlighter.highlight_cli(col2, language)

    def len_visible(text: str) -> int:
        return len(re.sub(r'\x1b\[[0-9;]*m', '', text))

    def wrap_text(text, width):
        words = text.split()
        lines = []
        current = []
        for word in words:
            if sum(len_visible(w) + 1 for w in current) + len_visible(word) <= width:
                current.append(word)
            else:
                lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))
        return lines or [""]

    def pad_right(text: str, width: int) -> str:
        vis_len = len_visible(text)
        padding_needed = max(0, width - vis_len)
        return text + (" " * padding_needed)

    c1_lines = wrap_text(col1, c1_width)
    c2_lines = wrap_text(col2, c2_width)
    
    max_lines = max(len(c1_lines), len(c2_lines))
    for i in range(max_lines):
        l1 = c1_lines[i] if i < len(c1_lines) else ""
        l2 = c2_lines[i] if i < len(c2_lines) else ""
        p1 = pad_right(l1, c1_width)
        p2 = pad_right(l2, c2_width)
        print(f"║ {p1} ║ {p2} ║")

def load_and_split_stereo(file_path: str, target_sample_rate: int = 16000) -> tuple[bytes, bytes, int]:
    """
    Loads a stereo audio file, resamples to 16kHz, converts to 16-bit PCM,
    splits into Left (Patient) and Right (Nurse) mono streams, and returns
    (patient_bytes, nurse_bytes, chunk_size_100ms).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found at {file_path}")
        
    logger.info(f"Loading and processing audio file: {file_path}")
    seg = AudioSegment.from_file(file_path)
    
    # Force 16kHz, 16-bit PCM (sample width = 2 bytes)
    seg = seg.set_frame_rate(target_sample_rate)
    seg = seg.set_sample_width(2)
    
    # Ensure it's stereo
    if seg.channels != 2:
        logger.warning("Input audio is not stereo. Simulating mono on both channels.")
        # If mono, both channels get the same audio
        left_mono = seg
        right_mono = seg
    else:
        # Split into left and right mono channels
        left_mono, right_mono = seg.split_to_mono()
        
    patient_bytes = left_mono.raw_data
    nurse_bytes = right_mono.raw_data
    
    # 16-bit mono bytes per second = 16000 * 1 * 2 = 32000
    bytes_per_sec = target_sample_rate * 1 * 2
    # 100ms chunk = 0.1s
    chunk_size = int(bytes_per_sec * 0.1)
    # Align to 2-byte frame boundary
    chunk_size = (chunk_size // 2) * 2
    
    return patient_bytes, nurse_bytes, chunk_size

async def run_live_translation(file_path: str, lang_code: str, language: str, api_key: str, model_name: str):
    if not os.path.exists(file_path):
        print(f"❌ Error: Audio file not found at {file_path}")
        return

    # Print header
    print_border()
    print(f"║ {'GEMINI LIVE REAL-TIME BILINGUAL INTERPRETER DEMO':^110} ║")
    print(f"║ {'Streaming file: ' + os.path.basename(file_path):^110} ║")
    print(f"║ {'Target Language: ' + language + ' (' + lang_code + ') | Model: ' + model_name:^110} ║")
    print_border()
    print(f"║ {'CLINICIAN / NURSE (English)':^54} ║ {'PATIENT / FAMILY (' + language + ')':^54} ║")
    print_border()

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the output audio streams to PCM files
    # Patient -> Nurse outputs English
    p_to_n_pcm_path = os.path.join(output_dir, f"translated_patient_to_nurse_en.pcm")
    # Nurse -> Patient outputs target language (e.g. German)
    n_to_p_pcm_path = os.path.join(output_dir, f"translated_nurse_to_patient_{language.lower()}.pcm")

    # Load and split stereo
    try:
        patient_bytes, nurse_bytes, chunk_size = load_and_split_stereo(file_path)
    except Exception as e:
        print(f"❌ Error preparing audio channels: {e}")
        return

    # Open PCM files for writing
    pcm_p_to_n = open(p_to_n_pcm_path, "wb")
    pcm_n_to_p = open(n_to_p_pcm_path, "wb")

    client = genai.Client(api_key=api_key)

    # 1. Config Patient -> Nurse (Translate patient language -> English)
    config_p_to_n = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        translation_config=types.TranslationConfig(
            target_language_code="en",
            echo_target_language=True
        ),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )

    # 2. Config Nurse -> Patient (Translate English -> Patient language)
    config_n_to_p = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        translation_config=types.TranslationConfig(
            target_language_code=lang_code,
            echo_target_language=True
        ),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )

    logger.info("Connecting parallel Live Translate sessions to Gemini...")
    try:
        async with client.aio.live.connect(model=model_name, config=config_p_to_n) as session_p_to_n, \
                   client.aio.live.connect(model=model_name, config=config_n_to_p) as session_n_to_p:
            print("🟢 Connected parallel live translation sessions!")
            print_border()

            # State for accumulating Patient to Nurse turn
            current_p_original = ""
            current_n_translated = ""
            p_to_n_audio_bytes = 0

            # State for accumulating Nurse to Patient turn
            current_n_original = ""
            current_p_translated = ""
            n_to_p_audio_bytes = 0

            # Background task to send audio chunks in real-time
            async def send_audio_task():
                try:
                    start_time = asyncio.get_event_loop().time()
                    chunks_queued = 0
                    max_len = max(len(patient_bytes), len(nurse_bytes))
                    
                    for i in range(0, max_len, chunk_size):
                        chunk_p = patient_bytes[i : i + chunk_size]
                        chunk_n = nurse_bytes[i : i + chunk_size]
                        
                        # Send patient channel to Patient->Nurse session
                        if chunk_p:
                            await session_p_to_n.send_realtime_input(
                                audio=types.Blob(data=chunk_p, mime_type="audio/pcm;rate=16000")
                            )
                        # Send nurse channel to Nurse->Patient session
                        if chunk_n:
                            await session_n_to_p.send_realtime_input(
                                audio=types.Blob(data=chunk_n, mime_type="audio/pcm;rate=16000")
                            )
                            
                        chunks_queued += 1
                        
                        # Strict real-time throttle (100ms intervals)
                        expected_release_time = start_time + (chunks_queued * 0.1)
                        sleep_time = expected_release_time - asyncio.get_event_loop().time()
                        if sleep_time > 0:
                            await asyncio.sleep(sleep_time)
                            
                    logger.info("Real-time dual-channel audio streaming complete.")
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Error in sending audio: {e}")

            # Background task to listen to Patient-to-Nurse session
            async def receive_p_to_n():
                nonlocal current_p_original, current_n_translated, p_to_n_audio_bytes
                try:
                    async for response in session_p_to_n.receive():
                        server_content = response.server_content
                        if server_content:
                            # Capture translation audio output
                            if server_content.model_turn:
                                for part in server_content.model_turn.parts:
                                    if part.inline_data:
                                        pcm_p_to_n.write(part.inline_data.data)
                                        p_to_n_audio_bytes += len(part.inline_data.data)
                                        
                            # Capture Patient original text
                            if server_content.input_transcription and server_content.input_transcription.text:
                                current_p_original += server_content.input_transcription.text
                                
                            # Capture Nurse translated text
                            if server_content.output_transcription and server_content.output_transcription.text:
                                current_n_translated += server_content.output_transcription.text
                                
                            # Display turn on complete
                            if server_content.turn_complete:
                                if current_p_original.strip() or current_n_translated.strip():
                                    print_row(
                                        f"🔊 Translation (EN):\n\"{current_n_translated.strip()}\"",
                                        f"🎙️ Original ({language}):\n\"{current_p_original.strip()}\"",
                                        language=language
                                    )
                                    print_row("- " * 27, "- " * 26)
                                    sys.stdout.flush()
                                current_p_original = ""
                                current_n_translated = ""
                                
                            if server_content.interrupted:
                                # Patient was interrupted or call was cut
                                if current_p_original.strip() or current_n_translated.strip():
                                    print_row(
                                        f"🔊 Translation [Part] (EN):\n\"{current_n_translated.strip()}\"",
                                        f"🎙️ Original [Part] ({language}):\n\"{current_p_original.strip()}\"",
                                        language=language
                                    )
                                print_row("⚠️ Patient stream interrupted!", "⚠️ Patient stream interrupted!")
                                print_row("- " * 27, "- " * 26)
                                sys.stdout.flush()
                                current_p_original = ""
                                current_n_translated = ""
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Error in Patient-to-Nurse receiver: {e}")

            # Background task to listen to Nurse-to-Patient session
            async def receive_n_to_p():
                nonlocal current_n_original, current_p_translated, n_to_p_audio_bytes
                try:
                    async for response in session_n_to_p.receive():
                        server_content = response.server_content
                        if server_content:
                            # Capture translation audio output
                            if server_content.model_turn:
                                for part in server_content.model_turn.parts:
                                    if part.inline_data:
                                        pcm_n_to_p.write(part.inline_data.data)
                                        n_to_p_audio_bytes += len(part.inline_data.data)
                                        
                            # Capture Nurse original text
                            if server_content.input_transcription and server_content.input_transcription.text:
                                current_n_original += server_content.input_transcription.text
                                
                            # Capture Patient translated text
                            if server_content.output_transcription and server_content.output_transcription.text:
                                current_p_translated += server_content.output_transcription.text
                                
                            # Display turn on complete
                            if server_content.turn_complete:
                                if current_n_original.strip() or current_p_translated.strip():
                                    print_row(
                                        f"🎙️ Original (EN):\n\"{current_n_original.strip()}\"",
                                        f"🔊 Translation ({language}):\n\"{current_p_translated.strip()}\"",
                                        language=language
                                    )
                                    print_row("- " * 27, "- " * 26)
                                    sys.stdout.flush()
                                current_n_original = ""
                                current_p_translated = ""
                                
                            if server_content.interrupted:
                                if current_n_original.strip() or current_p_translated.strip():
                                    print_row(
                                        f"🎙️ Original [Part] (EN):\n\"{current_n_original.strip()}\"",
                                        f"🔊 Translation [Part] ({language}):\n\"{current_p_translated.strip()}\"",
                                        language=language
                                    )
                                print_row("⚠️ Nurse stream interrupted!", "⚠️ Nurse stream interrupted!")
                                print_row("- " * 27, "- " * 26)
                                sys.stdout.flush()
                                current_n_original = ""
                                current_p_translated = ""
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Error in Nurse-to-Patient receiver: {e}")

            # Start all tasks
            send_task = asyncio.create_task(send_audio_task())
            rec_p_to_n_task = asyncio.create_task(receive_p_to_n())
            rec_n_to_p_task = asyncio.create_task(receive_n_to_p())

            # Wait for sending task to complete
            await send_task
            
            print("\n🏁 Audio file streaming finished! Waiting a few seconds for final translation packets...")
            await asyncio.sleep(6)
            
            # Cancel receiver tasks
            rec_p_to_n_task.cancel()
            rec_n_to_p_task.cancel()
            
            pcm_p_to_n.close()
            pcm_n_to_p.close()

            # Print footer
            print_border()
            print(f"║ {'REAL-TIME TRANSLATION FLOW COMPLETED':^110} ║")
            if p_to_n_audio_bytes > 0:
                print(f"║ Patient->Nurse translation saved to: {os.path.basename(p_to_n_pcm_path):<56} ║")
            if n_to_p_audio_bytes > 0:
                print(f"║ Nurse->Patient translation saved to: {os.path.basename(n_to_p_pcm_path):<56} ║")
            print_border()

    except Exception as e:
        print(f"❌ Gemini Live connection error: {e}")
        print("Please check your GEMINI_API_KEY environment variable and internet connection.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standalone Gemini Live Real-Time Bidirectional Medical Interpreter Demo")
    parser.add_argument(
        "--preset", "-p",
        choices=list(PRESETS.keys()),
        default="german",
        help="Use a preset call sample (german, spanish, vietnamese)"
    )
    parser.add_argument(
        "--file", "-f",
        help="Custom path to a local audio file to stream"
    )
    parser.add_argument(
        "--language", "-l",
        help="Custom target language (e.g., German, Spanish, Vietnamese)"
    )
    parser.add_argument(
        "--code", "-c",
        help="Custom language BCP-47 code (e.g., de, es, vi)"
    )
    parser.add_argument(
        "--model", "-m",
        default="gemini-3.5-live-translate-preview",
        help="Gemini Live model name (default: gemini-3.5-live-translate-preview)"
    )

    args = parser.parse_args()

    # Get API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable is not set.")
        print("Please set it in your environment or create a `.env` file.")
        sys.exit(1)

    # Determine file, language, and code
    if args.file:
        file_path = args.file
        language = args.language or "German"
        lang_code = args.code or "de"
    else:
        preset_info = PRESETS[args.preset]
        file_path = preset_info["file"]
        language = args.language or preset_info["language"]
        lang_code = args.code or preset_info["code"]

    # Run direct async interpreter loop
    asyncio.run(run_live_translation(file_path, lang_code, language, api_key, args.model))
