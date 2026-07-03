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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web_server")

GLOSSARY_PATH = "dictionary/glossary.json"

app = FastAPI(title="Bilingual Medical Interpreter API")

# Define preset medical call files (make sure paths match workspace)
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
        samples = array.array('h', chunk)
        return any(abs(s) > threshold for s in samples)
    except Exception:
        return False

@app.get("/api/glossary")
async def get_glossary(language: str = None):
    glossary_path = GLOSSARY_PATH
    if not os.path.exists(glossary_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        fallback_path = os.path.join(base_dir, "dictionary/glossary.json")
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

def load_and_format_glossary(target_language: str) -> str:
    """
    Loads active glossary terms from GLOSSARY_PATH, filters by target_language
    (case-insensitive matching), and formats each matching term into a clean
    key-value pair representation.
    """
    glossary_path = GLOSSARY_PATH
    if not os.path.exists(glossary_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        fallback_path = os.path.join(base_dir, "dictionary/glossary.json")
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
        
    formatted_lines = []
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
            if description:
                formatted_lines.append(f"- {english} -> {translation}: {description}")
            else:
                formatted_lines.append(f"- {english} -> {translation}")
                
    return "\n".join(formatted_lines)

def assemble_system_instructions(direction: str, target_language: str, glossary_str: str) -> str:
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
        glossary_section = (
            f"ACTIVE BILINGUAL GLOSSARY:\n"
            f"Below is a list of approved bilingual translations. When any of these concepts are mentioned "
            f"by the speaker, you MUST strictly use the corresponding translation provided:\n"
            f"{glossary_str}"
        )
    else:
        glossary_section = "ACTIVE BILINGUAL GLOSSARY:\nNo custom glossary terms are available for this session. Use standard medical terms."
        
    prompt = (
        f"{persona}\n\n"
        f"{australian_rules}\n\n"
        f"{task_description}\n\n"
        f"{glossary_section}\n\n"
        f"Remember: Do not add commentary or hold external side conversations. Translate the audio directly and faithfully."
    )
    return prompt

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
        
        if data.get("action") != "start":
            await websocket.send_json({"type": "error", "message": "Invalid starting command."})
            return
            
        preset_name = data.get("preset", "german")
        pacing_mode = data.get("pacing", "auto") # "auto" or "manual"
        timeout_sec = float(data.get("pause", data.get("timeout", 0.0)))
        timeout_sec = max(0.0, timeout_sec)
        
        if preset_name not in PRESETS:
            await websocket.send_json({"type": "error", "message": f"Preset '{preset_name}' is not recognized."})
            return
            
        preset = PRESETS[preset_name]
        file_path = preset["file"]
        lang_code = preset["code"]
        language = preset["language"]
        
        logger.info(f"Starting real-time interpretation call. Language: {language} ({lang_code}) File: {file_path}")
        
        # Load and split audio channels
        try:
            patient_bytes, nurse_bytes, chunk_size = load_and_split_channels(file_path)
        except Exception as e:
            await websocket.send_json({"type": "error", "message": f"Failed to prepare audio sample: {str(e)}"})
            return

        # Notify client of success and preparation details
        await websocket.send_json({
            "type": "status", 
            "status": "ready", 
            "language": language, 
            "code": lang_code,
            "duration_ms": len(patient_bytes) // 32 # 32 bytes per ms for 16kHz 16-bit mono
        })

        # Load and format language-specific glossary
        glossary_str = load_and_format_glossary(language)
        
        # Assemble structured medical system instructions
        sys_inst_p_to_n = assemble_system_instructions("p_to_n", language, glossary_str)
        sys_inst_n_to_p = assemble_system_instructions("n_to_p", language, glossary_str)

        # Define Live Translate session configurations
        # 1. Config Patient -> Nurse (translates Patient native language to English)
        config_p_to_n = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            system_instruction=types.Content(
                parts=[types.Part.from_text(text=sys_inst_p_to_n)]
            ),
            translation_config=types.TranslationConfig(
                target_language_code="en",
                echo_target_language=True
            ),
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
        )

        # 2. Config Nurse -> Patient (translates English to Patient native language)
        config_n_to_p = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            system_instruction=types.Content(
                parts=[types.Part.from_text(text=sys_inst_n_to_p)]
            ),
            translation_config=types.TranslationConfig(
                target_language_code=lang_code,
                echo_target_language=True
            ),
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
        )

        model_name = "gemini-3.5-live-translate-preview"
        
        # Connect both Live sessions in parallel
        async with client.aio.live.connect(model=model_name, config=config_p_to_n) as session_p_to_n, \
                   client.aio.live.connect(model=model_name, config=config_n_to_p) as session_n_to_p:
                   
            await websocket.send_json({"type": "status", "status": "connected"})
            logger.info("Parallel Gemini translation sessions successfully established.")

            # Track translation completions to coordinate speaker pacing
            patient_translation_complete = asyncio.Event()
            nurse_translation_complete = asyncio.Event()
            manual_next_event = asyncio.Event()
            stream_state = {"is_paused": False}

            # Task: Read responses from Patient -> Nurse session (translating to English)
            async def receive_p_to_n():
                try:
                    async for response in session_p_to_n.receive():
                        server_content = response.server_content
                        if server_content:
                            # Forward Translated English Audio (24kHz Mono PCM) to client
                            if server_content.model_turn:
                                for part in server_content.model_turn.parts:
                                    if part.inline_data:
                                        encoded_audio = base64.b64encode(part.inline_data.data).decode("utf-8")
                                        await websocket.send_json({
                                            "type": "translated_audio",
                                            "stream": "p_to_n",
                                            "data": encoded_audio
                                        })
                                        
                            # Forward Patient Original text transcript (interim segments)
                            if server_content.input_transcription and server_content.input_transcription.text:
                                await websocket.send_json({
                                    "type": "transcript",
                                    "speaker": "patient",
                                    "event": "original",
                                    "text": server_content.input_transcription.text,
                                    "final": server_content.input_transcription.finished
                                })
                                
                            # Forward Nurse Translation text transcript (interim segments)
                            if server_content.output_transcription and server_content.output_transcription.text:
                                await websocket.send_json({
                                    "type": "transcript",
                                    "speaker": "nurse",
                                    "event": "translation",
                                    "text": server_content.output_transcription.text,
                                    "final": False # turns are marked completed via turn_complete
                                })
                                
                            # Handle turn completion
                            if server_content.turn_complete:
                                patient_translation_complete.set()
                                await websocket.send_json({
                                    "type": "turn_complete",
                                    "speaker": "patient"
                                })
                                
                            if server_content.interrupted:
                                await websocket.send_json({
                                    "type": "interrupted",
                                    "speaker": "patient"
                                })
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Error in Patient->Nurse receiver: {e}")

            # Task: Read responses from Nurse -> Patient session (translating to target language)
            async def receive_n_to_p():
                try:
                    async for response in session_n_to_p.receive():
                        server_content = response.server_content
                        if server_content:
                            # Forward Translated Target Audio (24kHz Mono PCM) to client
                            if server_content.model_turn:
                                for part in server_content.model_turn.parts:
                                    if part.inline_data:
                                        encoded_audio = base64.b64encode(part.inline_data.data).decode("utf-8")
                                        await websocket.send_json({
                                            "type": "translated_audio",
                                            "stream": "n_to_p",
                                            "data": encoded_audio
                                        })
                                        
                            # Forward Nurse Original text transcript
                            if server_content.input_transcription and server_content.input_transcription.text:
                                await websocket.send_json({
                                    "type": "transcript",
                                    "speaker": "nurse",
                                    "event": "original",
                                    "text": server_content.input_transcription.text,
                                    "final": server_content.input_transcription.finished
                                })
                                
                            # Forward Patient Translation text transcript
                            if server_content.output_transcription and server_content.output_transcription.text:
                                await websocket.send_json({
                                    "type": "transcript",
                                    "speaker": "patient",
                                    "event": "translation",
                                    "text": server_content.output_transcription.text,
                                    "final": False
                                })
                                
                            # Handle turn completion
                            if server_content.turn_complete:
                                nurse_translation_complete.set()
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
                    pass
                except Exception as e:
                    logger.error(f"Error in Nurse->Patient receiver: {e}")

            # Task: Feed audio streams in synchronized real-time with Dynamic Hold/Resume
            async def send_audio():
                try:
                    max_len = max(len(patient_bytes), len(nurse_bytes))
                    
                    active_speaker = None
                    silence_counter = 0
                    SILENCE_CHUNKS_THRESHOLD = 3 # 3 chunks * 200ms = 600ms of silence
                    takeover_cooldown = 0
                    
                    for i in range(0, max_len, chunk_size):
                        # Check user pause
                        if stream_state["is_paused"]:
                            logger.info("Streaming paused by user. Feeding silence to Gemini to hold connection...")
                            while stream_state["is_paused"]:
                                silence_chunk = b'\x00' * chunk_size
                                await session_p_to_n.send_realtime_input(
                                    audio=types.Blob(data=silence_chunk, mime_type="audio/pcm;rate=16000")
                                )
                                await session_n_to_p.send_realtime_input(
                                    audio=types.Blob(data=silence_chunk, mime_type="audio/pcm;rate=16000")
                                )
                                await asyncio.sleep(0.2)
                            logger.info("Streaming resumed.")

                        if takeover_cooldown > 0:
                            takeover_cooldown -= 1
                            
                        chunk_p = patient_bytes[i : i + chunk_size]
                        chunk_n = nurse_bytes[i : i + chunk_size]
                        
                        p_has = has_speech(chunk_p)
                        n_has = has_speech(chunk_n)
                        
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
                            
                            if pacing_mode == "manual":
                                # Clear the manual resume event
                                manual_next_event.clear()
                                
                                # Notify client we are waiting for a manual next turn confirmation
                                await websocket.send_json({
                                    "type": "waiting_for_next",
                                    "speaker": speaker_finished
                                })
                                
                                logger.info(f"Entering manual hold state for {speaker_finished}. Waiting for user 'Next' trigger...")
                                
                                # Keep streaming silence to Gemini in a loop to keep connections alive
                                # Timeout after 1500 iterations (5 minutes max safety timeout)
                                for _ in range(1500):
                                    if manual_next_event.is_set():
                                        logger.info("Received manual next_turn trigger. Exiting hold state.")
                                        break
                                        
                                    await session_p_to_n.send_realtime_input(
                                        audio=types.Blob(data=silence_chunk, mime_type="audio/pcm;rate=16000")
                                    )
                                    await session_n_to_p.send_realtime_input(
                                        audio=types.Blob(data=silence_chunk, mime_type="audio/pcm;rate=16000")
                                    )
                                    await asyncio.sleep(0.2)
                                else:
                                    logger.warning(f"Manual hold state timed out after 5 minutes for {speaker_finished}. Proceeding.")
                                    
                            else:
                                # Auto Pacing mode
                                event_to_wait = patient_translation_complete if speaker_finished == "patient" else nurse_translation_complete
                                
                                # Fix the race condition: Check if the translation is already complete!
                                if event_to_wait.is_set():
                                    logger.info(f"Gemini already completed translation for {speaker_finished} before entering hold state.")
                                else:
                                    logger.info(f"Entering dynamic silence-streaming hold state for {speaker_finished}. Waiting for Gemini turn_complete...")
                                    
                                    # Loop up to timeout_sec (each iteration is 0.2s)
                                    iterations = int(timeout_sec * 5)
                                    for i in range(iterations):
                                        if event_to_wait.is_set():
                                            logger.info(f"Received turn_complete from Gemini for {speaker_finished} after {i * 0.2:.1f}s. Exiting hold loop.")
                                            break
                                            
                                        # Keep Gemini sessions alive and progressing with silence
                                        await session_p_to_n.send_realtime_input(
                                            audio=types.Blob(data=silence_chunk, mime_type="audio/pcm;rate=16000")
                                        )
                                        await session_n_to_p.send_realtime_input(
                                            audio=types.Blob(data=silence_chunk, mime_type="audio/pcm;rate=16000")
                                        )
                                        await asyncio.sleep(0.2)
                                    else:
                                        logger.warning(f"Silence-streaming hold state timed out after {timeout_sec}s for {speaker_finished}. Proceeding.")
                                        
                                # Insert an additional 2.0s pause for natural turn-taking transition and client playback clearance
                                logger.info("Pausing for 2.0s additional natural transition time...")
                                for _ in range(10):
                                    await session_p_to_n.send_realtime_input(
                                        audio=types.Blob(data=silence_chunk, mime_type="audio/pcm;rate=16000")
                                    )
                                    await session_n_to_p.send_realtime_input(
                                        audio=types.Blob(data=silence_chunk, mime_type="audio/pcm;rate=16000")
                                    )
                                    await asyncio.sleep(0.2)
                                    
                                # Clear the translation complete event ONLY at the end of the turn
                                event_to_wait.clear()
                            
                            # Reset active speaker state and silence counter after exiting hold/pacing block
                            active_speaker = next_speaker
                            silence_counter = 0
                            if active_speaker is not None:
                                takeover_cooldown = 10  # 10 chunks = 2.0s cooldown to prevent cascading takeovers
                            logger.info(f"Resuming pre-recorded stream with active speaker state: {active_speaker}")
                            
                        # Send patient channel to Gemini and forward original to browser
                        if chunk_p:
                            await session_p_to_n.send_realtime_input(
                                audio=types.Blob(data=chunk_p, mime_type="audio/pcm;rate=16000")
                            )
                            encoded_p = base64.b64encode(chunk_p).decode("utf-8")
                            await websocket.send_json({
                                "type": "original_audio",
                                "speaker": "patient",
                                "data": encoded_p
                            })
                                
                        # Send nurse channel to Gemini and forward original to browser
                        if chunk_n:
                            await session_n_to_p.send_realtime_input(
                                audio=types.Blob(data=chunk_n, mime_type="audio/pcm;rate=16000")
                            )
                            encoded_n = base64.b64encode(chunk_n).decode("utf-8")
                            await websocket.send_json({
                                "type": "original_audio",
                                "speaker": "nurse",
                                "data": encoded_n
                            })
                                
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
                            logger.info("Received next_turn signal from client.")
                            manual_next_event.set()
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
app.mount("/", StaticFiles(directory="web", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Start the server on localhost:8000
    uvicorn.run("web_server:app", host="127.0.0.1", port=8000, reload=True)
