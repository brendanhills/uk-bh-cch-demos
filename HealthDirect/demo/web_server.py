#!/usr/bin/env python3
"""
FastAPI Backend Server for Real-Time Bidirectional Bilingual Medical Interpreter
Coordinates audio splitting, dual Gemini Live connections, and WebSocket streaming to the Web UI.
"""

import asyncio
import os
import sys
import json
import base64
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from pydub import AudioSegment

# Force standard TLS/HTTPS to prevent client certificate/mTLS issues on VMs
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"

from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("web_server")
logger.setLevel(logging.INFO)

# Clear any existing handlers to avoid duplicates
if logger.handlers:
    logger.handlers.clear()

formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

# Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File Handler
file_handler = logging.FileHandler("interpreter_session.log", mode="w", encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

async def safe_send_realtime_input(session_or_managed, chunk: bytes, mime_type: str = "audio/pcm;rate=16000"):
    """
    Sends audio data to Gemini session safely and catches any connection errors.
    Supports raw sessions or ManagedSession helper objects.
    """
    session = session_or_managed
    if hasattr(session_or_managed, "session"):
        session = session_or_managed.session
        
    if session is None:
        # Session is currently connecting/disconnected, skip chunk
        return
        
    try:
        await session.send_realtime_input(
            audio=types.Blob(data=chunk, mime_type=mime_type)
        )
    except Exception as e:
        logger.warning(f"Failed to send realtime input on session {id(session)}: {e}")

GLOSSARY_PATH = "glossary/glossary.json"

app = FastAPI(title="Bilingual Medical Interpreter API")

# Define preset medical call files (make sure paths match workspace)
PRESETS = {
    "german": {
        "file": "samples/de_fever_session.wav",
        "code": "de",
        "language": "German",
        "gender": "male"
    },
    "spanish": {
        "file": "samples/es_ear_session.wav",
        "code": "es",
        "language": "Spanish",
        "gender": "male"
    },
    "vietnamese": {
        "file": "samples/paediatric_vietnamese_demo.wav",
        "code": "vi",
        "language": "Vietnamese",
        "gender": "female"
    },
    "arabic": {
        "file": "samples/ar_asthma_session.wav",
        "code": "ar",
        "language": "Arabic",
        "gender": "male"
    }
}

def load_and_split_channels(file_path: str, target_sample_rate: int = 16000) -> tuple[bytes, bytes, int]:
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
        left_mono = seg
        right_mono = seg
    else:
        # Split into left and right mono channels
        left_mono, right_mono = seg.split_to_mono()

    patient_bytes = left_mono.raw_data
    nurse_bytes = right_mono.raw_data

    # 16-bit mono bytes per second = 16000 * 1 * 2 = 32000
    bytes_per_sec = target_sample_rate * 1 * 2
    # 200ms chunk = 0.2s
    chunk_size = int(bytes_per_sec * 0.2)
    # Align to 2-byte frame boundary
    chunk_size = (chunk_size // 2) * 2

    return patient_bytes, nurse_bytes, chunk_size

def has_speech(chunk: bytes, threshold: int = 1000) -> bool:
    """
    Returns True if the max absolute value of 16-bit mono PCM samples
    in the chunk exceeds the given threshold.
    """
    if not chunk:
        return False
    import array
    try:
        # Align to 2-byte boundary to prevent ValueError from odd length chunks
        if len(chunk) % 2 != 0:
            chunk = chunk[:len(chunk) - 1]
        samples = array.array('h', chunk)
        return any(abs(s) > threshold for s in samples)
    except Exception:
        return False

@app.get("/api/glossary")
async def get_glossary(language: str = None):
    glossary_path = GLOSSARY_PATH
    if not os.path.exists(glossary_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        fallback_path = os.path.join(base_dir, "glossary/glossary.json")
        if os.path.exists(fallback_path):
            glossary_path = fallback_path

    if not os.path.exists(glossary_path):
        return {"glossary": []}

    try:
        with open(glossary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            entries = data.get("glossary", [])
    except Exception as e:
        logger.error(f"Error loading glossary: {e}")
        return {"glossary": []}

    if language:
        filtered_entries = []
        for entry in entries:
            translations = entry.get("translations", {})
            if language.lower() == "english" or any(l.lower() == language.lower() for l in translations.keys()):
                filtered_entries.append(entry)
        return {"glossary": filtered_entries}

    return {"glossary": entries}

@app.get("/api/pacing-config")
async def get_pacing_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "pacing_config.json")
    if not os.path.exists(config_path):
        return {
            "turn_timeout_sec": 15.0,
            "ceased_audio_threshold": 4.5,
            "startup_audio_threshold": 15.0,
            "additional_pause_sec": 2.0
        }
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading pacing config: {e}")
        return {
            "turn_timeout_sec": 15.0,
            "ceased_audio_threshold": 4.5,
            "startup_audio_threshold": 15.0,
            "additional_pause_sec": 2.0
        }

def scan_and_log_clinical_terms(orig_text: str, trans_text: str, target_language: str, speaker: str):
    """
    Scans the original and translated texts of a turn for active medical glossary terms
    and logs them to the server terminal.
    """
    if not orig_text and not trans_text:
        return

    # Load glossary
    glossary_path = GLOSSARY_PATH
    if not os.path.exists(glossary_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        fallback_path = os.path.join(base_dir, "glossary/glossary.json")
        if os.path.exists(fallback_path):
            glossary_path = fallback_path
    
    if not os.path.exists(glossary_path):
        return
        
    try:
        with open(glossary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            entries = data.get("glossary", [])
    except Exception as e:
        logger.error(f"Error loading glossary for term scanning: {e}")
        return

    import re

    def get_val_string(val):
        if not val:
            return ""
        if isinstance(val, list):
            return ", ".join(get_val_string(item) for item in val if item)
        if isinstance(val, dict):
            parts = []
            if val.get("formal"):
                parts.append(get_val_string(val["formal"]))
            if val.get("informal"):
                inf = val["informal"]
                if isinstance(inf, list):
                    parts.extend(get_val_string(item) for item in inf if item)
                else:
                    parts.append(get_val_string(inf))
            return ", ".join(p for p in parts if p)
        return str(val).strip()

    matches = []
    
    # Check both english and target_language terms
    for entry in entries:
        english_term = entry.get("english", "")
        translations = entry.get("translations", {})
        
        # Get target translation string
        trans_val = ""
        for lang_key, val in translations.items():
            if lang_key.lower() == target_language.lower():
                trans_val = get_val_string(val)
                break
                
        # Split synonyms by comma or semicolon
        english_syns = [s.strip() for s in re.split(r'[,;]+', english_term) if s.strip()]
        trans_syns = [s.strip() for s in re.split(r'[,;]+', trans_val) if s.strip()] if trans_val else []
        
        matched_eng = []
        matched_trans = []
        
        if speaker.lower() == "nurse":
            # Nurse speaks English
            for syn in english_syns:
                pattern = r'\b' + re.escape(syn) + r'\b'
                if re.search(pattern, orig_text, re.IGNORECASE):
                    matched_eng.append(syn)
            # Translation to foreign
            for syn in trans_syns:
                pattern = r'(?<!\w)' + re.escape(syn) + r'(?!\w)'
                if re.search(pattern, trans_text, re.IGNORECASE):
                    matched_trans.append(syn)
        else:
            # Patient speaks foreign
            for syn in trans_syns:
                pattern = r'(?<!\w)' + re.escape(syn) + r'(?!\w)'
                if re.search(pattern, orig_text, re.IGNORECASE):
                    matched_trans.append(syn)
            # Translation to English
            for syn in english_syns:
                pattern = r'\b' + re.escape(syn) + r'\b'
                if re.search(pattern, trans_text, re.IGNORECASE):
                    matched_eng.append(syn)
                    
        if matched_eng or matched_trans:
            matches.append({
                "english": english_term,
                "translation": trans_val,
                "description": entry.get("description", ""),
                "matched_english": matched_eng,
                "matched_translation": matched_trans
            })

    if matches:
        logger.info(f"\n💡 [CLINICAL TERMS IDENTIFIED][{speaker.upper()} TURN]")
        for m in matches:
            details = []
            if m["matched_english"]:
                details.append(f"English matched: '{', '.join(m['matched_english'])}'")
            if m["matched_translation"]:
                details.append(f"Translation matched: '{', '.join(m['matched_translation'])}'")
            logger.info(f"  • {m['english']} -> {m['translation']} ({'; '.join(details)}) | Desc: {m['description']}")
        logger.info("")

def load_and_format_glossary(target_language: str, direction: str = "n_to_p", exclude_descriptions: bool = False) -> str:
    """
    Loads active glossary terms from GLOSSARY_PATH, filters by target_language
    (case-insensitive matching), and formats each matching term into a clean
    key-value pair representation.
    """
    glossary_path = GLOSSARY_PATH
    if not os.path.exists(glossary_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        fallback_path = os.path.join(base_dir, "glossary/glossary.json")
        if os.path.exists(fallback_path):
            glossary_path = fallback_path

    if not os.path.exists(glossary_path):
        logger.warning(f"Glossary file not found at {glossary_path}.")
        return ""

    try:
        with open(glossary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            entries = data.get("glossary", [])
    except Exception as e:
        logger.error(f"Error loading glossary for formatting: {e}")
        return ""

    raw_rules = []
    target_lang_lower = target_language.lower()
    for entry in entries:
        english = entry.get("english", "")
        translations = entry.get("translations", {})
        description = entry.get("description", "")

        # Find the case-insensitive matching language key
        matched_lang_key = None
        for lang_key in translations.keys():
            if lang_key.lower() == target_lang_lower:
                matched_lang_key = lang_key
                break

        if matched_lang_key:
            translation = translations[matched_lang_key]
            if isinstance(translation, dict):
                formal_lang = translation.get("formal")
                informal_lang_list = []
                informal_raw = translation.get("informal")
                if informal_raw:
                    if isinstance(informal_raw, list):
                        informal_lang_list.extend(informal_raw)
                    elif isinstance(informal_raw, str):
                        informal_lang_list.append(informal_raw)

                formal_eng = english
                informal_eng_list = entry.get("informal_english", [])

                if direction == "p_to_n":
                    # Formal mapping: Cephalgie -> cephalalgia
                    if formal_lang:
                        raw_rules.append((formal_lang, formal_eng, description))
                    # Informal mapping: Kopfschmerzen -> headache
                    if informal_lang_list:
                        target_informal_eng = informal_eng_list[0] if (informal_eng_list and len(informal_eng_list) > 0) else formal_eng
                        for inf_lang in informal_lang_list:
                            raw_rules.append((inf_lang, target_informal_eng, description))
                else:
                    # Nurse -> Patient (English -> Foreign)
                    # Formal mapping: cephalalgia -> Cephalgie
                    if formal_lang:
                        raw_rules.append((formal_eng, formal_lang, description))
                    # Informal mapping: headache -> Kopfschmerzen
                    if informal_eng_list and informal_lang_list:
                        for inf_eng in informal_eng_list:
                            raw_rules.append((inf_eng, ", ".join(informal_lang_list), description))
                    elif informal_lang_list:
                        raw_rules.append((formal_eng, ", ".join(informal_lang_list), description))
            else:
                # Flat string translation (e.g. "Fieber" -> "extreme fire flame")
                translation_str = str(translation)
                if direction == "p_to_n":
                    raw_rules.append((translation_str, english, description))
                else:
                    raw_rules.append((english, translation_str, description))

    # Now deduplicate rules with priority logic to prevent conflicting instructions
    unique_rules = {}
    for from_term, to_term, desc in raw_rules:
        from_term_clean = from_term.strip().lower()
        if from_term_clean in unique_rules:
            existing_to = unique_rules[from_term_clean][1]
            
            # Priority 1: 'extreme fire flame' always wins (demo priority override)
            if to_term.strip().lower() == "extreme fire flame":
                unique_rules[from_term_clean] = (from_term, to_term, desc)
            elif existing_to.strip().lower() == "extreme fire flame":
                pass
            # Priority 2: 'headache' (singular) overrides 'headaches' (plural) for natural translation
            elif to_term.strip().lower() == "headache":
                unique_rules[from_term_clean] = (from_term, to_term, desc)
            elif existing_to.strip().lower() == "headache":
                pass
            else:
                # Default: keep latest mapping
                unique_rules[from_term_clean] = (from_term, to_term, desc)
        else:
            unique_rules[from_term_clean] = (from_term, to_term, desc)

    # Format the deduplicated rules
    formatted_lines = []
    for from_term, to_term, desc in unique_rules.values():
        term_rule = f"{from_term} -> {to_term}"
        if desc and not exclude_descriptions:
            formatted_lines.append(f"- {term_rule}: {desc}")
        else:
            formatted_lines.append(f"- {term_rule}")

    return "\n".join(formatted_lines)


def assemble_system_instructions(direction: str, target_language: str, glossary_str: str, is_flash_live: bool = False) -> str:
    """
    Assembles a highly structured system instruction prompt for Gemini Live Translate.
    Fuses clinical persona, Australian spelling constraints, and dynamic glossary mappings.
    """
    persona = (
        "You are a highly professional, accurate, and empathetic bilingual medical interpreter. "
        "Your role is to translate spoken conversation in real-time between a clinician (Nurse) and a patient. "
        "Maintain a neutral, professional medical tone. Translate exactly what is said without summarizing, "
        "embellishing, or adding medical advice."
    )

    australian_rules = (
        "CRITICAL SPELLING & NOMENCLATURE CONSTRAINT:\n"
        "You must strictly adhere to Australian medical standards, terminology, and spelling conventions.\n"
        "- Use 'paracetamol' instead of 'acetaminophen'.\n"
        "- Use 'Emergency Department' instead of 'ER' or 'Emergency Room'.\n"
        "- Use Australian/Commonwealth spelling: e.g., 'paediatric' (not 'pediatric'), 'haematology' (not 'hematology'), "
        "'gastroenteritis' (not 'stomach flu')."
    )

    passive_constraint = ""
    if is_flash_live:
        passive_constraint = (
            "CRITICAL PASSIVE INTERPRETER CONSTRAINT:\n"
            "You are a completely passive, transparent, and silent interpreter. "
            "You must NOT engage in conversation, answer questions, provide medical disclaimers, or warn the speaker. "
            "Your ONLY output must be the direct, faithful translation of the speaker's words. "
            "Do NOT add any surrounding text, explanations, greetings, or commentary. "
            "Do NOT say 'Please consult a doctor', 'This is not medical advice' or any other medical safety disclaimers. "
            "Output ONLY the translated words. If the speaker says 'Ich habe etwas Fieber', you must translate it "
            "directly and cleanly, respecting the active bilingual glossary.\n"
            "CRITICAL BOUNDARY FOR PASSIVE TRANSLATION (ALL LANGUAGES):\n"
            "You must act strictly as a translation channel, NOT a conversational partner. "
            "Even if the speaker is crying, begs you for help, expresses extreme distress, describes a life-threatening medical emergency, "
            "or directly asks you questions (in any language, e.g., Arabic, Spanish, Vietnamese, German, English), "
            "you must NEVER speak back to them, reassure them, offer comfort, or answer them. "
            "Do NOT talk back to the patient. Do NOT address the speaker directly under any circumstances. "
            "Your only task is to translate their spoken statement or plea EXACTLY and directly into the target language for the other party.\n"
            "TONE, URGENCY & EMPATHY PRESERVATION:\n"
            "While remaining a passive and transparent interpreter, you MUST fully match and preserve the speaker's "
            "tone, urgency, emotional intensity, clinical empathy, and pace. If the speaker conveys panic, pain, "
            "or distress, your translated output voice delivery and phrasing must accurately reflect that level of "
            "urgency and empathy without sounding mechanical or robotic."
        )

    if direction == "p_to_n":
        task_description = (
            f"DIRECTIONS:\n"
            f"You are interpreting from the Patient (speaking {target_language}) to the Nurse (speaking English).\n"
            f"Your job is to translate the patient's spoken statements into natural, clear English. "
            f"Ensure all clinical terms are aligned to standard Australian medical concepts."
        )
    else:
        task_description = (
            f"DIRECTIONS:\n"
            f"You are interpreting from the Nurse (speaking English) to the Patient (speaking {target_language}).\n"
            f"Your job is to translate the clinician's English explanations and questions into accurate, "
            f"comprehensible, and culturally appropriate {target_language}. Keep clinical terms precise."
        )

    glossary_section = ""
    if glossary_str:
        if is_flash_live:
            glossary_section = (
                f"MANDATORY GLOSSARY TRANSLATION RULE (CRITICAL):\n"
                f"This translation session is governed by a strict medical glossary. "
                f"Whenever translating the speaker's words (whether from audio or text), you MUST override any default or standard translations "
                f"with the mappings defined in the ACTIVE BILINGUAL GLOSSARY below. "
                f"This rule is absolute. Under no circumstances should you use the standard translation if a glossary term exists.\n"
                f"For example: If the active glossary maps 'Aspirin -> Magic Pain Dust', you must output 'Magic Pain Dust' whenever translating 'Aspirin' (do NOT translate as 'aspirin' under any circumstances).\n\n"
                f"ACTIVE BILINGUAL GLOSSARY:\n"
                f"{glossary_str}"
            )
        else:
            glossary_section = (
                f"ACTIVE BILINGUAL GLOSSARY:\n"
                f"Below is a list of approved bilingual translations. When any of these concepts are mentioned "
                f"by the speaker, you MUST strictly use the corresponding translation provided:\n"
                f"{glossary_str}"
            )
    else:
        glossary_section = "ACTIVE BILINGUAL GLOSSARY:\nNo custom glossary terms are available for this session. Use standard medical terms."

    parts = []
    if is_flash_live:
        # Front-load critical constraints and glossary rules for Gemini 3.1 to override audio translation weights
        if passive_constraint:
            parts.append(passive_constraint)
        parts.append(glossary_section)
        parts.append(persona)
        parts.append(australian_rules)
        parts.append(task_description)
    else:
        # Standard configuration
        parts.append(persona)
        parts.append(australian_rules)
        parts.append(task_description)
        parts.append(glossary_section)

    parts.append(
        "Remember: You are a strict passive translation channel. "
        "Do not speak to or answer the speaker directly. "
        "Do not add any commentary, reassuring words, or hold side conversations. "
        "Translate all spoken statements directly and faithfully."
    )

    return "\n\n".join(parts)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client connected to interpreter WebSocket.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        await websocket.send_json({"type": "error", "message": "GEMINI_API_KEY is not configured on the backend server."})
        await websocket.close()
        return

    client = genai.Client(api_key=api_key)
    active_tasks = []

    try:
        # Wait for the client to send the "start" message specifying the preset
        init_message = await websocket.receive_text()
        data = json.loads(init_message)
        logger.info(f"Received starting handshake payload from client: {data}")

        if data.get("action") != "start":
            await websocket.send_json({"type": "error", "message": "Invalid starting command."})
            return

        preset_name = data.get("preset", "german")
        timeout_sec = float(data.get("pause", data.get("timeout", 15.0)))
        if timeout_sec <= 0.0:
            timeout_sec = 15.0

        ceased_audio_threshold = float(data.get("ceased_audio_threshold", 4.5))
        startup_audio_threshold = float(data.get("startup_audio_threshold", 15.0))
        additional_pause_sec = float(data.get("additional_pause_sec", 2.0))

        if preset_name not in PRESETS:
            await websocket.send_json({"type": "error", "message": f"Preset '{preset_name}' is not recognized."})
            return

        preset = PRESETS[preset_name]
        file_path = preset["file"]
        lang_code = preset["code"]
        language = preset["language"]

        # Select appropriate prebuilt voice names based on preset gender
        patient_gender = preset.get("gender", "male")
        patient_voice = "Puck" if patient_gender == "male" else "Kore"
        nurse_voice = "Kore"  # Nurse Sarah is always female


        logger.info(f"Starting real-time interpretation call. Language: {language} ({lang_code}) File: {file_path}")

        # Load and split audio channels
        try:
            patient_bytes, nurse_bytes, chunk_size = load_and_split_channels(file_path)
        except Exception as e:
            await websocket.send_json({"type": "error", "message": f"Failed to prepare audio sample: {str(e)}"})
            return

        # Fail-fast in-memory audio slicing
        limit_seconds = data.get("limit_seconds")
        if limit_seconds:
            try:
                # 16kHz, 16-bit mono = 32000 bytes per second
                limit_bytes = int(16000 * 2 * float(limit_seconds))
                if chunk_size > 0:
                    limit_bytes = (limit_bytes // chunk_size) * chunk_size
                patient_bytes = patient_bytes[:limit_bytes]
                nurse_bytes = nurse_bytes[:limit_bytes]
                logger.info(f"Fail-fast testing: sliced in-memory audio to the first {limit_seconds} seconds ({len(patient_bytes)} bytes).")
            except Exception as slice_err:
                logger.warning(f"Failed to apply limit_seconds slice: {slice_err}")

        # Notify client of success and preparation details
        await websocket.send_json({
            "type": "status",
            "status": "ready",
            "language": language,
            "code": lang_code,
            "duration_ms": len(patient_bytes) // 32 # 32 bytes per ms for 16kHz 16-bit mono
        })

        # Detect active model
        model_name = data.get("model", "gemini-3.5-live-translate-preview")
        if model_name not in ["gemini-3.5-live-translate-preview", "gemini-3.1-flash-live-preview"]:
            model_name = "gemini-3.5-live-translate-preview"

        is_flash_live = (model_name in ["gemini-3.1-flash-live-preview"])
        logger.info(f"Using model: {model_name} (Glossary Enforced: {is_flash_live})")

        # Load and format language-specific directed glossaries
        glossary_str_p_to_n = load_and_format_glossary(language, direction="p_to_n", exclude_descriptions=is_flash_live)
        glossary_str_n_to_p = load_and_format_glossary(language, direction="n_to_p", exclude_descriptions=is_flash_live)


        # Initialize/reset the transcript file at the start of the WebSocket session
        try:
            with open("conversation_transcript.log", "w", encoding="utf-8") as f:
                f.write("SESSION TRANSCRIPT START\n")
                f.write(f"Language: {language}\n")
                f.write(f"Model: {model_name}\n")
                f.write("Pacing: auto\n")
                f.write("========================================\n")
        except Exception as e:
            logger.error(f"Failed to initialize conversation_transcript.log: {e}")

        # Assemble structured medical system instructions
        sys_inst_p_to_n = assemble_system_instructions("p_to_n", language, glossary_str_p_to_n, is_flash_live=is_flash_live)
        sys_inst_n_to_p = assemble_system_instructions("n_to_p", language, glossary_str_n_to_p, is_flash_live=is_flash_live)

        # Define Live Translate session configurations
        # 1. Config Patient -> Nurse (translates Patient native language to English)
        if is_flash_live:
            config_p_to_n = types.LiveConnectConfig(
                response_modalities=[types.Modality.AUDIO],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=patient_voice)
                    )
                ),
                system_instruction=types.Content(
                    parts=[types.Part.from_text(text=sys_inst_p_to_n)]
                ),
                input_audio_transcription=types.AudioTranscriptionConfig(),
                output_audio_transcription=types.AudioTranscriptionConfig(),
                realtime_input_config=types.RealtimeInputConfig(
                    automatic_activity_detection=types.AutomaticActivityDetection(
                        silence_duration_ms=400
                    )
                ),
            )
        else:
            config_p_to_n = types.LiveConnectConfig(
                response_modalities=[types.Modality.AUDIO],
                translation_config=types.TranslationConfig(
                    target_language_code="en",
                    echo_target_language=True
                ),
                input_audio_transcription=types.AudioTranscriptionConfig(),
                output_audio_transcription=types.AudioTranscriptionConfig(),
                realtime_input_config=types.RealtimeInputConfig(
                    automatic_activity_detection=types.AutomaticActivityDetection(
                        silence_duration_ms=400
                    )
                ),
            )

        # 2. Config Nurse -> Patient (translates English to Patient native language)
        if is_flash_live:
            config_n_to_p = types.LiveConnectConfig(
                response_modalities=[types.Modality.AUDIO],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=nurse_voice)
                    )
                ),
                system_instruction=types.Content(
                    parts=[types.Part.from_text(text=sys_inst_n_to_p)]
                ),
                input_audio_transcription=types.AudioTranscriptionConfig(),
                output_audio_transcription=types.AudioTranscriptionConfig(),
                realtime_input_config=types.RealtimeInputConfig(
                    automatic_activity_detection=types.AutomaticActivityDetection(
                        silence_duration_ms=400
                    )
                ),
            )
        else:
            config_n_to_p = types.LiveConnectConfig(
                response_modalities=[types.Modality.AUDIO],
                translation_config=types.TranslationConfig(
                    target_language_code=lang_code,
                    echo_target_language=True
                ),
                input_audio_transcription=types.AudioTranscriptionConfig(),
                output_audio_transcription=types.AudioTranscriptionConfig(),
                realtime_input_config=types.RealtimeInputConfig(
                    automatic_activity_detection=types.AutomaticActivityDetection(
                        silence_duration_ms=400
                    )
                ),
            )

        class ManagedSession:
            def __init__(self, direction, client, model_name, config):
                self.direction = direction
                self.client = client
                self.model_name = model_name
                self.config = config
                self.cm = None
                self.session = None

            async def connect(self):
                if self.cm:
                    try:
                        await self.cm.__aexit__(None, None, None)
                    except Exception as e:
                        logger.warning(f"Error closing previous session in connect for {self.direction}: {e}")
                    self.cm = None
                    self.session = None

                self.cm = self.client.aio.live.connect(model=self.model_name, config=self.config)
                self.session = await self.cm.__aenter__()
                logger.info(f"Connected fresh session for {self.direction}")
                return self.session

            async def __aenter__(self):
                await self.connect()
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                if self.cm:
                    try:
                        await self.cm.__aexit__(exc_type, exc_val, exc_tb)
                    except Exception as e:
                        logger.warning(f"Error in __aexit__ for {self.direction}: {e}")
                    self.cm = None
                    self.session = None

        managed_p_to_n = ManagedSession("patient_to_nurse", client, model_name, config_p_to_n)
        managed_n_to_p = ManagedSession("nurse_to_patient", client, model_name, config_n_to_p)

        # Connect both Live sessions in parallel using the chosen model
        logger.info(f"Connecting to dual live sessions using model: {model_name}")

        async with managed_p_to_n, managed_n_to_p:

            await websocket.send_json({"type": "status", "status": "connected"})
            logger.info("Parallel Gemini translation sessions successfully established.")

            # Track translation completions to coordinate speaker pacing
            patient_translation_complete = asyncio.Event()
            nurse_translation_complete = asyncio.Event()
            stream_state = {
                "is_paused": False,
                "last_audio_p_to_n": 0.0,
                "last_audio_n_to_p": 0.0
            }
            convo_state = {
                "patient_orig": "",
                "patient_trans": "",
                "nurse_orig": "",
                "nurse_trans": ""
            }

            # Task: Read responses from Patient -> Nurse session (translating to English)
            async def receive_p_to_n():
                try:
                    while True:
                        session = managed_p_to_n.session
                        if session is None:
                            await asyncio.sleep(0.1)
                            continue
                        try:
                            async for response in session.receive():
                                server_content = response.server_content
                                if server_content:
                                    # Forward Translated English Audio (24kHz Mono PCM) to client
                                    if server_content.model_turn:
                                        for part in server_content.model_turn.parts:
                                            if part.inline_data:
                                                if has_speech(part.inline_data.data, threshold=500):
                                                    stream_state["last_audio_p_to_n"] = asyncio.get_running_loop().time()
                                                encoded_audio = base64.b64encode(part.inline_data.data).decode("utf-8")
                                                await websocket.send_json({
                                                    "type": "translated_audio",
                                                    "stream": "p_to_n",
                                                    "data": encoded_audio
                                                })
                                            if part.text:
                                                logger.info(f"[MODEL PART TEXT][p_to_n]: {part.text}")
                                                if is_flash_live:
                                                    convo_state["patient_trans"] += part.text
                                                    await websocket.send_json({
                                                        "type": "transcript",
                                                        "speaker": "nurse",
                                                        "event": "translation",
                                                        "text": part.text,
                                                        "final": False
                                                    })

                                    # Forward Patient Original text transcript (interim segments)
                                    if server_content.input_transcription and server_content.input_transcription.text:
                                        text = server_content.input_transcription.text
                                        is_final = server_content.input_transcription.finished
                                        convo_state["patient_orig"] += text
                                        logger.info(f"[TRANSCRIPT ORIGINAL][PATIENT] {text} (final={is_final})")
                                        await websocket.send_json({
                                            "type": "transcript",
                                            "speaker": "patient",
                                            "event": "original",
                                            "text": text,
                                            "final": is_final
                                        })

                                    # Forward Nurse Translation text transcript (interim segments)
                                    if server_content.output_transcription and server_content.output_transcription.text:
                                        text = server_content.output_transcription.text
                                        convo_state["patient_trans"] += text
                                        logger.info(f"[TRANSCRIPT TRANSLATED][PATIENT -> English] {text}")
                                        await websocket.send_json({
                                            "type": "transcript",
                                            "speaker": "nurse",
                                            "event": "translation",
                                            "text": text,
                                            "final": False # turns are marked completed via turn_complete
                                        })

                                    # Handle turn completion
                                    if server_content.turn_complete:
                                        patient_translation_complete.set()
                                        logger.info("[TURN COMPLETE][PATIENT]")
                                        orig = convo_state.get("patient_orig", "").strip()
                                        trans = convo_state.get("patient_trans", "").strip()
                                        if orig or trans:
                                            msg = (
                                                f"\n========================================\n"
                                                f"WHO: PATIENT\n"
                                                f"SAID: {orig}\n"
                                                f"TRANSLATED TO: {trans}\n"
                                                f"========================================\n"
                                            )
                                            logger.info(msg)
                                            try:
                                                with open("conversation_transcript.log", "a", encoding="utf-8") as f:
                                                    f.write(msg)
                                            except Exception as e:
                                                logger.error(f"Failed to append to conversation_transcript.log: {e}")
                                            convo_state["patient_orig"] = ""
                                            convo_state["patient_trans"] = ""
                                        await websocket.send_json({
                                            "type": "turn_complete",
                                            "speaker": "patient"
                                        })

                                    if server_content.interrupted:
                                        logger.info("[INTERRUPTED][PATIENT]")
                                        await websocket.send_json({
                                            "type": "interrupted",
                                            "speaker": "patient"
                                        })
                        except asyncio.CancelledError:
                            break
                        except Exception as e:
                            logger.error(f"Error in Patient->Nurse session receive loop: {e}")
                            await asyncio.sleep(0.2)
                except asyncio.CancelledError:
                    pass

            # Task: Read responses from Nurse -> Patient session (translating to target language)
            async def receive_n_to_p():
                try:
                    while True:
                        session = managed_n_to_p.session
                        if session is None:
                            await asyncio.sleep(0.1)
                            continue
                        try:
                            async for response in session.receive():
                                server_content = response.server_content
                                if server_content:
                                    # Forward Translated Target Audio (24kHz Mono PCM) to client
                                    if server_content.model_turn:
                                        for part in server_content.model_turn.parts:
                                            if part.inline_data:
                                                if has_speech(part.inline_data.data, threshold=500):
                                                    stream_state["last_audio_n_to_p"] = asyncio.get_running_loop().time()
                                                encoded_audio = base64.b64encode(part.inline_data.data).decode("utf-8")
                                                await websocket.send_json({
                                                    "type": "translated_audio",
                                                    "stream": "n_to_p",
                                                    "data": encoded_audio
                                                })
                                            if part.text:
                                                logger.info(f"[MODEL PART TEXT][n_to_p]: {part.text}")
                                                if is_flash_live:
                                                    convo_state["nurse_trans"] += part.text
                                                    await websocket.send_json({
                                                        "type": "transcript",
                                                        "speaker": "patient",
                                                        "event": "translation",
                                                        "text": part.text,
                                                        "final": False
                                                    })

                                    # Forward Nurse Original text transcript
                                    if server_content.input_transcription and server_content.input_transcription.text:
                                        text = server_content.input_transcription.text
                                        is_final = server_content.input_transcription.finished
                                        convo_state["nurse_orig"] += text
                                        logger.info(f"[TRANSCRIPT ORIGINAL][NURSE] {text} (final={is_final})")
                                        await websocket.send_json({
                                            "type": "transcript",
                                            "speaker": "nurse",
                                            "event": "original",
                                            "text": text,
                                            "final": is_final
                                        })

                                    # Forward Patient Translation text transcript
                                    if server_content.output_transcription and server_content.output_transcription.text:
                                        text = server_content.output_transcription.text
                                        convo_state["nurse_trans"] += text
                                        logger.info(f"[TRANSCRIPT TRANSLATED][NURSE -> PATIENT] {text}")
                                        await websocket.send_json({
                                            "type": "transcript",
                                            "speaker": "patient",
                                            "event": "translation",
                                            "text": text,
                                            "final": False
                                        })

                                    # Handle turn completion
                                    if server_content.turn_complete:
                                        nurse_translation_complete.set()
                                        logger.info("[TURN COMPLETE][NURSE]")
                                        orig = convo_state.get("nurse_orig", "").strip()
                                        trans = convo_state.get("nurse_trans", "").strip()
                                        if orig or trans:
                                            msg = (
                                                f"\n========================================\n"
                                                f"WHO: NURSE\n"
                                                f"SAID: {orig}\n"
                                                f"TRANSLATED TO: {trans}\n"
                                                f"========================================\n"
                                            )
                                            logger.info(msg)
                                            try:
                                                with open("conversation_transcript.log", "a", encoding="utf-8") as f:
                                                    f.write(msg)
                                            except Exception as e:
                                                logger.error(f"Failed to append to conversation_transcript.log: {e}")
                                            convo_state["nurse_orig"] = ""
                                            convo_state["nurse_trans"] = ""
                                        await websocket.send_json({
                                            "type": "turn_complete",
                                            "speaker": "nurse"
                                        })

                                    if server_content.interrupted:
                                        await websocket.send_json({
                                            "type": "interrupted",
                                            "speaker": "nurse"
                                        })
                        except asyncio.CancelledError:
                            break
                        except Exception as e:
                            logger.error(f"Error in Nurse->Patient session receive loop: {e}")
                            await asyncio.sleep(0.2)
                except asyncio.CancelledError:
                    pass

            # Task: Feed audio streams in synchronized real-time with Dynamic Hold/Resume
            async def send_audio():
                try:
                    max_len = max(len(patient_bytes), len(nurse_bytes))

                    active_speaker = None
                    silence_counter = 0
                    # Dynamically calculate the silence threshold based on ceased_audio_threshold (each chunk is 200ms)
                    # Enforce a robust minimum of 4 chunks (800ms) to prevent overly aggressive cutoffs
                    SILENCE_CHUNKS_THRESHOLD = max(4, int(ceased_audio_threshold / 0.2))
                    logger.info(f"Using dynamic SILENCE_CHUNKS_THRESHOLD = {SILENCE_CHUNKS_THRESHOLD} ({SILENCE_CHUNKS_THRESHOLD * 200}ms) based on ceased_audio_threshold = {ceased_audio_threshold}s")
                    takeover_cooldown = 0
                    loop_counter = 0

                    patient_translation_complete.clear()
                    nurse_translation_complete.clear()

                    silence_chunk = b'\x00' * chunk_size

                    for i in range(0, max_len, chunk_size):
                        loop_counter += 1
                        # Check user pause
                        if stream_state["is_paused"]:
                            logger.info("Streaming paused by user...")
                            while stream_state["is_paused"]:
                                await asyncio.sleep(0.2)
                            logger.info("Streaming resumed.")

                        if takeover_cooldown > 0:
                            takeover_cooldown -= 1

                        chunk_p = patient_bytes[i : i + chunk_size]
                        chunk_n = nurse_bytes[i : i + chunk_size]

                        p_has = has_speech(chunk_p)
                        n_has = has_speech(chunk_n)

                        if p_has:
                            patient_translation_complete.clear()
                        if n_has:
                            nurse_translation_complete.clear()

                        speaker_finished = None
                        next_speaker = None

                        # 1. Update and check speech detection state machine for Turn Transitions
                        if p_has and n_has:
                            # Both speaking simultaneously.
                            # If we have an active speaker, the other starting is treated as a takeover if cooldown is clear.
                            if takeover_cooldown == 0 and active_speaker == "nurse":
                                speaker_finished = "nurse"
                                next_speaker = "patient"
                            elif takeover_cooldown == 0 and active_speaker == "patient":
                                speaker_finished = "patient"
                                next_speaker = "nurse"
                            else:
                                silence_counter = 0
                        elif p_has and not n_has:
                            if takeover_cooldown == 0 and active_speaker == "nurse":
                                # Case B: Direct takeover by Patient
                                speaker_finished = "nurse"
                                next_speaker = "patient"
                            elif active_speaker is None:
                                active_speaker = "patient"
                                logger.info("Detected Patient speech starting in raw file.")
                            silence_counter = 0
                        elif n_has and not p_has:
                            if takeover_cooldown == 0 and active_speaker == "patient":
                                # Case C: Direct takeover by Nurse
                                speaker_finished = "patient"
                                next_speaker = "nurse"
                            elif active_speaker is None:
                                active_speaker = "nurse"
                                logger.info("Detected Nurse speech starting in raw file.")
                            silence_counter = 0
                        elif not p_has and not n_has:
                            if active_speaker is not None:
                                silence_counter += 1
                                if silence_counter >= SILENCE_CHUNKS_THRESHOLD:
                                    # Case A: Silence threshold met
                                    speaker_finished = active_speaker
                                    next_speaker = None

                        # 2. Trigger Turn Hold & Pacing Block if a turn finished
                        if speaker_finished is not None:
                            logger.info(f"{speaker_finished.capitalize()} finished speaking (takeover/silence). Pausing stream to wait for translation playback.")

                            # Notify client that backend has paused sending original audio
                            await websocket.send_json({
                                "type": "stream_paused",
                                "speaker": speaker_finished
                            })

                            silence_chunk = b'\x00' * chunk_size

                            # Auto Pacing mode
                            event_to_wait = patient_translation_complete if speaker_finished == "patient" else nurse_translation_complete
                            event_to_wait.clear() # Clear immediately to prevent prior turns' late events from bypassing hold

                            # Reset the audio envelope tracker for the active stream
                            audio_tracker_key = "last_audio_p_to_n" if speaker_finished == "patient" else "last_audio_n_to_p"
                            stream_state[audio_tracker_key] = 0.0
                            hold_start_time = asyncio.get_running_loop().time()

                            # Fix the race condition: Check if the translation is already complete!
                            if event_to_wait.is_set():
                                logger.info(f"Gemini already completed translation for {speaker_finished} before entering hold state.")
                            else:
                                logger.info(f"Entering dynamic silence-streaming hold state for {speaker_finished}. Waiting for Gemini turn_complete...")

                                # Loop up to safety-net timeout (each iteration is 0.2s)
                                # Using max(timeout_sec, 25.0) prevents long/slow translations from being cut off prematurely
                                iterations = int(max(timeout_sec, 25.0) * 5)
                                for hold_idx in range(iterations):
                                    if event_to_wait.is_set():
                                        logger.info(f"Received turn_complete from Gemini for {speaker_finished} after {hold_idx * 0.2:.1f}s. Exiting hold loop.")
                                        break
 
                                    # Audio power envelope/activity fallback monitoring
                                    now = asyncio.get_running_loop().time()
                                    last_audio_time = stream_state[audio_tracker_key]
 
                                    if last_audio_time > 0.0:
                                        # Audio was received, check if it has ceased for more than ceased_audio_threshold seconds
                                        if now - last_audio_time > ceased_audio_threshold:
                                            logger.info(f"Audio envelope detection: Translation audio ceased for {now - last_audio_time:.1f}s (Threshold: {ceased_audio_threshold}s). Assuming turn complete.")
                                            break
                                    else:
                                        # No audio received yet. Timeout if we have waited more than startup_audio_threshold seconds for first audio
                                        if now - hold_start_time > startup_audio_threshold:
                                            logger.info(f"Audio envelope detection: No translation audio received within {startup_audio_threshold}s startup window. Assuming turn complete or silent.")
                                            break
 
                                    # Keep Gemini sessions alive with continuous active/inactive silence streaming
                                    if is_flash_live:
                                        # For 3.1 Flash: send silence to BOTH sessions to keep connections hot and VAD active
                                        await safe_send_realtime_input(managed_p_to_n, silence_chunk)
                                        await safe_send_realtime_input(managed_n_to_p, silence_chunk)
                                    else:
                                        # For 3.5 Translate: stream silence ONLY to the inactive session sparsely to keep it alive
                                        # and avoid sending to the active session which does not support input during generation
                                        if hold_idx % 15 == 0:
                                            if speaker_finished == "patient":
                                                await safe_send_realtime_input(managed_n_to_p, silence_chunk)
                                            else:
                                                await safe_send_realtime_input(managed_p_to_n, silence_chunk)
                                    await asyncio.sleep(0.2)
                                else:
                                    logger.warning(f"Silence-streaming hold state timed out after safety window for {speaker_finished}. Proceeding.")
 
                            # Insert an additional pause for natural turn-taking transition and client playback clearance
                            logger.info(f"Pausing for {additional_pause_sec}s additional natural transition time...")
                            for pause_idx in range(max(1, int(additional_pause_sec * 5))):
                                # Send silence to BOTH sessions to keep them hot and active during transition pause
                                await safe_send_realtime_input(managed_p_to_n, silence_chunk)
                                await safe_send_realtime_input(managed_n_to_p, silence_chunk)
                                await asyncio.sleep(0.2)
 
                            # Clear the translation complete event ONLY at the end of the turn
                            event_to_wait.clear()
 
                            # Reset active speaker state and silence counter after exiting hold/pacing block
                            active_speaker = next_speaker
                            silence_counter = 0
                            if active_speaker is not None:
                                takeover_cooldown = 10  # 10 chunks = 2.0s cooldown to prevent cascading takeovers
                            logger.info(f"Resuming pre-recorded stream with active speaker state: {active_speaker}")
 
                            # Recycle the finished speaker's session asynchronously under 3.1 Flash Live
                            if is_flash_live:
                                if speaker_finished == "patient":
                                    logger.info("Asynchronously recycling Patient->Nurse session...")
                                    asyncio.create_task(managed_p_to_n.connect())
                                elif speaker_finished == "nurse":
                                    logger.info("Asynchronously recycling Nurse->Patient session...")
                                    asyncio.create_task(managed_n_to_p.connect())
 
                        # Send patient channel original audio to browser
                        if chunk_p:
                            encoded_p = base64.b64encode(chunk_p).decode("utf-8")
                            await websocket.send_json({
                                "type": "original_audio",
                                "speaker": "patient",
                                "data": encoded_p
                            })
 
                        # Send nurse channel original audio to browser
                        if chunk_n:
                            encoded_n = base64.b64encode(chunk_n).decode("utf-8")
                            await websocket.send_json({
                                "type": "original_audio",
                                "speaker": "nurse",
                                "data": encoded_n
                            })
 
                        # Stream real-time speech/silence to keep BOTH Gemini Live sessions hot
                        if active_speaker == "patient":
                            if chunk_p:
                                await safe_send_realtime_input(managed_p_to_n, chunk_p)
                            else:
                                await safe_send_realtime_input(managed_p_to_n, silence_chunk)
                            # Send silence keepalive to the inactive nurse session
                            if is_flash_live:
                                await safe_send_realtime_input(managed_n_to_p, silence_chunk)
                            else:
                                if loop_counter % 15 == 0:
                                    await safe_send_realtime_input(managed_n_to_p, silence_chunk)
                        elif active_speaker == "nurse":
                            if chunk_n:
                                await safe_send_realtime_input(managed_n_to_p, chunk_n)
                            else:
                                await safe_send_realtime_input(managed_n_to_p, silence_chunk)
                            # Send silence keepalive to the inactive patient session
                            if is_flash_live:
                                await safe_send_realtime_input(managed_p_to_n, silence_chunk)
                            else:
                                if loop_counter % 15 == 0:
                                    await safe_send_realtime_input(managed_p_to_n, silence_chunk)
                        else:
                            # Both sessions are currently idle, send silence to both
                            if is_flash_live:
                                await safe_send_realtime_input(managed_p_to_n, silence_chunk)
                                await safe_send_realtime_input(managed_n_to_p, silence_chunk)
                            else:
                                if loop_counter % 15 == 0:
                                    await safe_send_realtime_input(managed_p_to_n, silence_chunk)
                                    await safe_send_realtime_input(managed_n_to_p, silence_chunk)
 
                        # Dynamic-friendly 200ms throttle sleep (avoids catchup bug on resume)
                        await asyncio.sleep(0.2)


                    logger.info("Finished streaming pre-recorded audio channels.")
                    # Keep sessions alive for any final translation trailing content
                    await asyncio.sleep(6)
                    await websocket.send_json({"type": "status", "status": "completed"})

                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Error in sender thread: {e}")

            # Task: Listen to incoming WebSocket messages from the client (e.g. "resume" commands)
            async def receive_client_messages():
                try:
                    while True:
                        msg_text = await websocket.receive_text()
                        msg_data = json.loads(msg_text)
                        action = msg_data.get("action")
                        if action == "resume":
                            logger.info(f"Received resume signal from client for speaker turn: {msg_data.get('speaker')} (Ignoring - backend resumes automatically)")
                        elif action == "next_turn":
                            logger.info("Received next_turn signal from client. (Ignoring - manual pacing is removed)")
                        elif action == "pause":
                            logger.info("User requested call pause. Setting stream_state['is_paused'] = True.")
                            stream_state["is_paused"] = True
                        elif action == "resume_call":
                            logger.info("User requested call resume. Setting stream_state['is_paused'] = False.")
                            stream_state["is_paused"] = False
                except WebSocketDisconnect:
                    logger.info("Client disconnected from WebSocket.")
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Error in client message receiver: {e}")

            # Schedule the parallel tasks
            rec_p_to_n_task = asyncio.create_task(receive_p_to_n())
            rec_n_to_p_task = asyncio.create_task(receive_n_to_p())
            send_audio_task = asyncio.create_task(send_audio())
            rec_client_task = asyncio.create_task(receive_client_messages())

            active_tasks.extend([rec_p_to_n_task, rec_n_to_p_task, send_audio_task, rec_client_task])

            # Wait for either the streaming to finish, or the client connection to break
            done, pending = await asyncio.wait(
                [send_audio_task, rec_client_task],
                return_when=asyncio.FIRST_COMPLETED
            )

    except WebSocketDisconnect:
        logger.info("Client disconnected from WebSocket.")
    except Exception as e:
        logger.error(f"WebSocket endpoint exception: {e}")
    finally:
        # Cancel any active running background threads to prevent resource leaks
        for task in active_tasks:
            if not task.done():
                task.cancel()
        logger.info("Cleaned up and shut down translation session tasks.")

# Mount the static files directory to serve the frontend html/js/css
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "web"), html=True), name="static")
WEBSERVER_PORT=int(os.getenv("WEBSERVER_PORT"))

if __name__ == "__main__":
    import uvicorn
    # Start the server on localhost:9000
    # Ensure uvicorn's path resolution succeeds even if run directly as a script
    parent_dir = os.path.dirname(BASE_DIR)
    uvicorn.run("demo.web_server:app", host="127.0.0.1", port=WEBSERVER_PORT, reload=True, app_dir=parent_dir, log_config=None)
