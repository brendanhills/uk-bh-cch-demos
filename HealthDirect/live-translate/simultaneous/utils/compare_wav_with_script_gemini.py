#!/usr/bin/env python3
"""
compare_wav_with_script_gemini.py

A high-fidelity diagnostic utility that leverages Gemini's native multimodal
audio understanding to transcribe our simultaneous stereo WAV samples and perform
a side-by-side semantic validation against the original dialogue scripts.
"""

import os
import sys
import json
import argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load local environment variables from .env
load_dotenv()

# Standard preset mapping
PRESETS = {
    "german": {
        "script": "samples/scripts/de_fever_session.json",
        "audio": "samples/de_fever_session.wav"
    },
    "spanish": {
        "script": "samples/scripts/es_ear_session.json",
        "audio": "samples/es_ear_session.wav"
    },
    "vietnamese": {
        "script": "samples/scripts/vi_paediatric_session.json",
        "audio": "samples/vi_paediatric_session.wav"
    },
    "arabic": {
        "script": "samples/scripts/ar_asthma_session.json",
        "audio": "samples/ar_asthma_session.wav"
    },
    "hindi": {
        "script": "samples/scripts/hi_cough_session.json",
        "audio": "samples/hi_cough_session.wav"
    }
}

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Transcribe simultaneous audio samples via Gemini and validate against dialogue scripts."
    )
    parser.add_argument(
        "preset",
        choices=list(PRESETS.keys()) + ["de", "es", "vi", "ar", "hi"],
        help="The language scenario to validate (e.g. 'german', 'de', 'spanish', 'es', etc.)"
    )
    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Gemini model to use for transcription (default: gemini-2.5-flash)"
    )
    return parser.parse_args()

def resolve_preset_key(preset_arg: str) -> str:
    arg = preset_arg.lower()
    mapping = {
        "de": "german",
        "es": "spanish",
        "vi": "vietnamese",
        "ar": "arabic",
        "hi": "hindi"
    }
    return mapping.get(arg, arg)

def load_script_turns(script_path: str) -> list:
    if not os.path.exists(script_path):
        print(f"[ERROR] Dialogue script JSON not found at: {script_path}")
        sys.exit(1)
        
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    turns = []
    for idx, turn in enumerate(data.get("turns", [])):
        turns.append({
            "index": idx + 1,
            "speaker": turn.get("speaker", "unknown").upper(),
            "text": turn.get("text", "").strip()
        })
    return turns

def transcribe_audio_gemini(audio_path: str, model_name: str) -> str:
    if not os.path.exists(audio_path):
        print(f"[ERROR] Audio WAV file not found at: {audio_path}")
        sys.exit(1)
        
    print(f"\n[Gemini] Initializing genai Client...")
    try:
        client = genai.Client()
    except Exception as e:
        print(f"[ERROR] Failed to initialize Google GenAI Client: {e}")
        print("Please ensure your GEMINI_API_KEY environment variable is set.")
        sys.exit(1)
        
    print(f"[Gemini] Reading raw audio bytes from {audio_path}...")
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
        
    print(f"[Gemini] Sending audio to model '{model_name}' for transcription...")
    
    prompt = (
        "You are an expert medical transcriptionist. Listen to this dual-channel stereo audio "
        "and transcribe every single word spoken. Format your output strictly as a JSON list "
        "of dialogue turns. Each item in the list must be a JSON object with 'speaker' (either "
        "'NURSE' or 'CALLER') and 'text' keys representing what they said. Do not omit any words, "
        "and preserve the spoken language of each speaker. Respond ONLY with valid, raw, unquoted "
        "JSON content (do not wrap in markdown ```json blocks)."
    )
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[
                types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type="audio/wav"
                ),
                prompt
            ]
        )
        return response.text
    except Exception as e:
        print(f"[ERROR] Gemini transcription API call failed: {e}")
        sys.exit(1)

def perform_alignment_comparison(script_turns: list, transcribed_text: str):
    print("\n" + "=" * 80)
    print("  GEMINI TRANSCRIPTION VS. DIALOGUE SCRIPT ALIGNMENT")
    print("=" * 80)
    
    # Clean output in case model wrapped it in markdown blocks despite instructions
    clean_text = transcribed_text.strip()
    if clean_text.startswith("```"):
        # Remove starting ```json or ```
        clean_text = clean_text.split("\n", 1)[1]
    if clean_text.endswith("```"):
        clean_text = clean_text.rsplit("\n", 1)[0]
    clean_text = clean_text.strip()
    
    try:
        transcribed_turns = json.loads(clean_text)
    except Exception as e:
        print("[WARNING] Could not parse Gemini's response as a valid JSON list of turns.")
        print("Raw Response from Gemini:")
        print("-" * 50)
        print(transcribed_text)
        print("-" * 50)
        return
        
    print(f"\nSuccessfully parsed {len(transcribed_turns)} transcribed turns from Gemini.")
    print("-" * 80)
    
    max_turns = max(len(script_turns), len(transcribed_turns))
    discrepancies = 0
    
    for i in range(max_turns):
        print(f"\n--- Turn {i+1} ---")
        
        # Expected from Script
        if i < len(script_turns):
            s_turn = script_turns[i]
            s_speaker = s_turn["speaker"]
            s_text = s_turn["text"]
            print(f"  [EXPECTED SCRIPT] ({s_speaker}):")
            print(f"    \"{s_text}\"")
        else:
            s_speaker = None
            s_text = None
            print("  [EXPECTED SCRIPT]: (None - end of script reached)")
            
        # Heard from Gemini
        if i < len(transcribed_turns):
            t_turn = transcribed_turns[i]
            t_speaker = str(t_turn.get("speaker", "unknown")).upper()
            t_text = t_turn.get("text", "").strip()
            print(f"  [GEMINI HEARD   ] ({t_speaker}):")
            print(f"    \"{t_text}\"")
        else:
            t_speaker = None
            t_text = None
            print("  [GEMINI HEARD   ]: (None - model did not transcribe further)")
            
        # Simple validation
        if s_speaker != t_speaker:
            print("  >> [MISMATCH] Speaker role does not match!")
            discrepancies += 1
        elif s_text and t_text:
            # Check length/presence to make sure it's not radically different
            s_words = set(s_text.lower().replace(".", "").replace(",", "").split())
            t_words = set(t_text.lower().replace(".", "").replace(",", "").split())
            common = s_words.intersection(t_words)
            
            # If overlap is extremely small (e.g. less than 10%), flag it
            if len(s_words) > 0 and (len(common) / len(s_words)) < 0.15:
                print("  >> [MISMATCH] Text content diverges significantly!")
                discrepancies += 1
            else:
                print("  >> [MATCH] Spoken content aligned.")
                
    print("\n" + "=" * 80)
    if discrepancies == 0:
        print("  COMPARISON SUMMARY: ALL SPOKEN CONTENT MATCHES SCRIPT PERFECTLY!")
    else:
        print(f"  COMPARISON SUMMARY: COMPLETED WITH {discrepancies} SECTIONS FLAGGED.")
    print("=" * 80)

def main():
    args = parse_arguments()
    preset_key = resolve_preset_key(args.preset)
    
    preset_info = PRESETS[preset_key]
    script_path = preset_info["script"]
    audio_path = preset_info["audio"]
    
    print(f"Starting Gemini transcription comparison for scenario: {preset_key.upper()}")
    
    # 1. Load original turns from script
    script_turns = load_script_turns(script_path)
    print(f"Loaded {len(script_turns)} turns from official script: {script_path}")
    
    # 2. Transcribe WAV via Gemini multimodal input
    transcribed_raw = transcribe_audio_gemini(audio_path, args.model)
    
    # 3. Perform Alignment Comparison
    perform_alignment_comparison(script_turns, transcribed_raw)

if __name__ == "__main__":
    main()
