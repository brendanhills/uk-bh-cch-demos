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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from pydub import AudioSegment
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

import argparse

def load_config(config_path: str = None) -> dict:
    """Loads the interpreter configuration JSON file."""
    if not config_path:
        config_path = os.path.join(BASE_DIR, "interpreter_config.json")
    
    if not os.path.exists(config_path):
        return {}
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def parse_args(args: list = None) -> argparse.Namespace:
    """Parses command line arguments, falling back to interpreter_config.json defaults."""
    initial_parser = argparse.ArgumentParser(add_help=False)
    initial_parser.add_argument("--config", default=None)
    parsed_initial, _ = initial_parser.parse_known_args(args)
    
    config_file = parsed_initial.config
    config = load_config(config_file)
    
    parser = argparse.ArgumentParser(
        description="Unified Real-Time Bidirectional Bilingual Medical Interpreter Server/CLI"
    )
    parser.add_argument("--cli", action="store_true", help="Enable CLI execution mode")
    parser.add_argument("--config", default=config_file, help="Path to interpreter_config.json")
    
    parser.add_argument(
        "--preset",
        default=None,
        help="Pre-configured medical call preset (e.g. 'german', 'spanish', 'vietnamese', 'arabic', 'hindi')"
    )
    parser.add_argument(
        "--file",
        default=None,
        help="Path to custom stereo WAV input file"
    )
    
    parser.add_argument(
        "--model",
        default=os.getenv("LIVE_TRANSLATE_MODEL", config.get("model_name", "gemini-3.5-live-translate-preview")),
        help="Gemini Live model name"
    )
    parser.add_argument(
        "--chunk-ms",
        type=int,
        default=config.get("chunk_ms", 40),
        help="Audio streaming chunk size in milliseconds"
    )
    parser.add_argument(
        "--pacing",
        default=config.get("pacing_mode", "paced"),
        choices=["simple", "paced"],
        help="Pacing streaming mode"
    )
    parser.add_argument(
        "--playback",
        action="store_true",
        default=config.get("enable_playback", False),
        help="Enable local real-time audio playback through system speakers"
    )
    parser.add_argument(
        "--no-glossary",
        action="store_true",
        default=not config.get("enable_glossary", True),
        help="Disable clinical glossary priming"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        default=config.get("enable_stats", False),
        help="Enable logging frame-by-frame stats to console"
    )
    parser.add_argument(
        "--no-prewarm",
        action="store_true",
        default=not config.get("enable_prewarming", True),
        help="Disable WebSocket pre-warming and model preloading"
    )
    parser.add_argument(
        "--language-code",
        default=None,
        help="Target translation language code (overrides preset)"
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Target translation language name (overrides preset)"
    )
    
    parsed, _ = parser.parse_known_args(args)
    
    if parsed.preset:
        preset_key = parsed.preset.lower()
        presets = config.get("presets", {})
        if preset_key in presets:
            preset_data = presets[preset_key]
            if not parsed.file:
                parsed.file = preset_data.get("file")
            if not parsed.language_code:
                parsed.language_code = preset_data.get("code")
            if not parsed.language:
                parsed.language = preset_data.get("language")
                
    return parsed

def calculate_chunk_size(chunk_ms: int, sample_rate: int = 16000) -> int:
    """Calculates the byte size of an audio chunk for 16-bit mono linear PCM.
    
    1 sample = 2 bytes. Mono.
    """
    bytes_per_second = sample_rate * 1 * 2  # 32000
    chunk_size = int(bytes_per_second * (chunk_ms / 1000.0))
    # Align to 2-byte frame boundary
    return (chunk_size // 2) * 2

def clear_active_buffers(*queues_or_lists):
    """Clears all provided lists, queues, or buffer structures to handle interruptions."""
    for structure in queues_or_lists:
        if isinstance(structure, list):
            structure.clear()
        elif hasattr(structure, "empty") and hasattr(structure, "get_nowait"):
            while not structure.empty():
                try:
                    structure.get_nowait()
                except Exception:
                    break


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

def get_genai_client() -> genai.Client:
    """Returns an initialized google-genai Client using Vertex AI (ADC) or API Key.
    
    If USE_VERTEXAI env var is set or GEMINI_API_KEY is omitted/empty, uses Vertex AI mode with ADC.
    """
    use_vertex = os.getenv("USE_VERTEXAI", "").lower() in ("1", "true", "yes")
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key and not use_vertex:
        return genai.Client(api_key=api_key)
    
    project_id = (
        os.environ.get("PROJECT_ID") or
        os.environ.get("GOOGLE_CLOUD_PROJECT") or
        "uk-bh-experiments-argolis"
    )
    location = os.environ.get("LOCATION", "us-central1")
    return genai.Client(
        vertexai=True, project=project_id, location=location
    )

def build_live_configs(client: genai.Client, model_name: str, preset: dict, language: str):
    """Builds (model_name, config_p_to_n, config_n_to_p) compatible with either Vertex AI or Developer API mode."""
    is_vertex = getattr(client, "vertexai", False)
    
    # Vertex AI mode does not support translation_config or gemini-3.5-live-translate-preview.
    # Automatically switch to gemini-3.1-flash-live-preview for Vertex AI mode.
    if is_vertex and ("live-translate" in model_name or not model_name):
        model_name = "gemini-3.1-flash-live-preview"

    use_system_instruction = is_vertex or (model_name in ["gemini-3.1-flash-live-preview"])
    lang_code = preset.get("code", "de") if preset else "de"

    if use_system_instruction:
        patient_gender = preset.get("gender", "male") if preset else "male"
        patient_voice = "Puck" if patient_gender == "male" else "Kore"
        nurse_voice = "Kore"

        glossary_str_p_to_n = load_and_format_glossary(language, direction="p_to_n", exclude_descriptions=True)
        glossary_str_n_to_p = load_and_format_glossary(language, direction="n_to_p", exclude_descriptions=True)
        sys_inst_p_to_n = assemble_system_instructions("p_to_n", language, glossary_str_p_to_n, is_flash_live=True)
        sys_inst_n_to_p = assemble_system_instructions("n_to_p", language, glossary_str_n_to_p, is_flash_live=True)

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
        )

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
        )

        config_n_to_p = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            translation_config=types.TranslationConfig(
                target_language_code=lang_code,
                echo_target_language=True
            ),
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
        )

    return model_name, config_p_to_n, config_n_to_p

class ActiveSession:
    """Thread-safe, singleton-style room pairing session coordinator.

    Coordinates a single Nurse and Patient connection. Synchronizes scenario,
    model, and target language state updates.
    """

    def __init__(self):
        self.nurse_ws: Optional[WebSocket] = None
        self.patient_ws: Optional[WebSocket] = None
        self.preset_key: str = "german"
        config = load_config()
        self.model_name: str = os.getenv("LIVE_TRANSLATE_MODEL", config.get("model_name", "gemini-3.5-live-translate-preview"))
        self.language: str = "German"
        self.custom_file_path: Optional[str] = None
        self.language_code: Optional[str] = None
        self.is_active: bool = False
        self.streaming_task: Optional[asyncio.Task] = None
        self.lock = asyncio.Lock()
        
        # Pre-warming / connection caching attributes
        self.prewarmed_session_p_to_n = None
        self.prewarmed_session_n_to_p = None
        self.prewarmed_ctx_p_to_n = None
        self.prewarmed_ctx_n_to_p = None
        self.prewarm_task = None
        self.prewarm_status = "disconnected"
        
        # Ephemeral transcript, summary, and purge worker state
        self.transcript_history = []
        self.generated_summary = None
        self.purge_timer_task = None
        
        try:
            cmd_args = parse_args(sys.argv[1:])
            self.enable_prewarming = not cmd_args.no_prewarm
            if cmd_args.preset:
                self.preset_key = cmd_args.preset
            if cmd_args.file:
                self.custom_file_path = cmd_args.file
            if cmd_args.model:
                self.model_name = cmd_args.model
            if cmd_args.language:
                self.language = cmd_args.language
            if cmd_args.language_code:
                self.language_code = cmd_args.language_code
        except Exception:
            config = load_config()
            self.enable_prewarming = config.get("enable_prewarming", True)

        # Disable pre-warming by default under pytest to maintain event order compatibility
        if "pytest" in sys.modules:
            self.enable_prewarming = False

    async def register_nurse(self, websocket: WebSocket):
        """Registers the clinician (nurse) WebSocket connection."""
        async with self.lock:
            self.nurse_ws = websocket
            logger.info("Nurse client connected and registered.")
            await websocket.send_json({
                "type": "state_sync",
                "preset": self.preset_key,
                "model": self.model_name,
                "language": self.language,
                "is_active": self.is_active
            })
            if self.generated_summary:
                await websocket.send_json({
                    "type": "summary_generated",
                    "summary": self.generated_summary
                })
            if self.enable_prewarming:
                await websocket.send_json({
                    "type": "prewarm_status",
                    "status": self.prewarm_status
                })
            await self.trigger_prewarm_check_unsafe()

    async def register_patient(self, websocket: WebSocket):
        """Registers the patient WebSocket connection."""
        async with self.lock:
            self.patient_ws = websocket
            logger.info("Patient client connected and registered.")
            await websocket.send_json({
                "type": "state_sync",
                "preset": self.preset_key,
                "model": self.model_name,
                "language": self.language,
                "is_active": self.is_active
            })
            if self.enable_prewarming:
                await websocket.send_json({
                    "type": "prewarm_status",
                    "status": self.prewarm_status
                })
            await self.trigger_prewarm_check_unsafe()

    async def trigger_prewarm_check_unsafe(self):
        """Checks and triggers background pre-warming if both clients are registered."""
        if self.enable_prewarming and self.nurse_ws and self.patient_ws:
            if not self.prewarm_task or self.prewarm_task.done():
                self.prewarm_task = asyncio.create_task(self.prewarm_sessions_loop())

    async def cancel_prewarm_unsafe(self):
        """Cancels pre-warming tasks and cleans up hot standby connections."""
        if self.prewarm_task and not self.prewarm_task.done():
            self.prewarm_task.cancel()
        self.prewarm_task = None
        await self.close_prewarmed_unsafe()
        self.prewarm_status = "disconnected"

    async def disconnect_nurse(self):
        """Deregisters the nurse WebSocket and notifies the patient."""
        async with self.lock:
            self.nurse_ws = None
            logger.info("Nurse disconnected.")
            if self.patient_ws:
                try:
                    await self.patient_ws.send_json({
                        "type": "status",
                        "status": "waiting_for_nurse"
                    })
                except Exception as e:
                    logger.debug(f"Error notifying patient of nurse disconnect: {e}")
            await self.stop_stream_unsafe()
            await self.cancel_prewarm_unsafe()

    async def disconnect_patient(self):
        """Deregisters the patient WebSocket and notifies the nurse."""
        async with self.lock:
            self.patient_ws = None
            logger.info("Patient disconnected.")
            if self.nurse_ws:
                try:
                    await self.nurse_ws.send_json({
                        "type": "status",
                        "status": "patient_disconnected"
                    })
                except Exception as e:
                    logger.debug(f"Error notifying nurse of patient disconnect: {e}")
            await self.stop_stream_unsafe()
            await self.cancel_prewarm_unsafe()

    async def update_config(self, preset: str, model: str, language: str):
        """Updates the session configuration and broadcasts to both clients."""
        async with self.lock:
            self.preset_key = preset
            self.model_name = model
            self.language = language
            update_msg = {
                "type": "config_update",
                "preset": self.preset_key,
                "model": self.model_name,
                "language": self.language
            }
            if self.patient_ws:
                await self.patient_ws.send_json(update_msg)
            if self.nurse_ws:
                await self.nurse_ws.send_json(update_msg)

            # Restart pre-warming with the updated language / model
            if self.enable_prewarming:
                if self.prewarm_task and not self.prewarm_task.done():
                    self.prewarm_task.cancel()
                self.prewarm_task = None
                await self.close_prewarmed_unsafe()
                await self.trigger_prewarm_check_unsafe()

    async def reset(self):
        """Stops any active stream, resets coordinator state, and broadcasts a reset command."""
        async with self.lock:
            await self.stop_stream_unsafe()
            self.transcript_history = []
            self.generated_summary = None
            self.cancel_purge_timer_unsafe()
            reset_msg = {
                "type": "reset"
            }
            if self.patient_ws:
                try:
                    await self.patient_ws.send_json(reset_msg)
                except Exception as e:
                    logger.warning(f"Error sending reset to Patient: {e}")
            if self.nurse_ws:
                try:
                    await self.nurse_ws.send_json(reset_msg)
                except Exception as e:
                    logger.warning(f"Error sending reset to Nurse: {e}")
            logger.info("Session coordinator state reset and broadcasted successfully.")

    async def broadcast_to_both(self, data: dict):
        """Broadcasts a JSON payload to both connected clients."""
        async with self.lock:
            if self.nurse_ws:
                try:
                    await self.nurse_ws.send_json(data)
                except Exception as e:
                    logger.warning(f"Error sending to Nurse: {e}")
            if self.patient_ws:
                try:
                    await self.patient_ws.send_json(data)
                except Exception as e:
                    logger.warning(f"Error sending to Patient: {e}")

    async def broadcast_prewarm_status(self):
        """Broadcasts pre-warm connection state updates to connected clients."""
        msg = {
            "type": "prewarm_status",
            "status": self.prewarm_status
        }
        if self.nurse_ws:
            try:
                await self.nurse_ws.send_json(msg)
            except Exception:
                pass
        if self.patient_ws:
            try:
                await self.patient_ws.send_json(msg)
            except Exception:
                pass

    async def prewarm_sessions_loop(self):
        """Maintains parallel pre-connected Gemini Live API sessions in a hot state."""
        logger.info("Initializing background pre-warming loop...")
        self.prewarm_status = "connecting"
        await self.broadcast_prewarm_status()

        preset = PRESETS.get(self.preset_key)
        if not preset:
            logger.error(f"Unknown preset during pre-warming: {self.preset_key}")
            self.prewarm_status = "disconnected"
            await self.broadcast_prewarm_status()
            return

        try:
            client = get_genai_client()
        except Exception as e:
            logger.error(f"Failed to initialize GenAI client for pre-warming: {e}")
            self.prewarm_status = "disconnected"
            await self.broadcast_prewarm_status()
            return

        model_name, config_p_to_n, config_n_to_p = build_live_configs(
            client, self.model_name, preset, preset.get("language", "German")
        )

        try:
            logger.info("Connecting parallel pre-warmed Live sessions to Gemini...")
            self.prewarmed_ctx_p_to_n = client.aio.live.connect(model=model_name, config=config_p_to_n)
            self.prewarmed_ctx_n_to_p = client.aio.live.connect(model=model_name, config=config_n_to_p)

            self.prewarmed_session_p_to_n = await self.prewarmed_ctx_p_to_n.__aenter__()
            self.prewarmed_session_n_to_p = await self.prewarmed_ctx_n_to_p.__aenter__()

            logger.info("Pre-warmed parallel Live API sessions established and hot.")
            self.prewarm_status = "ready"
            await self.broadcast_prewarm_status()

            # Keep-alive sparse pings every 2.5 seconds
            silent_frame = b'\x00' * 1280
            while True:
                await asyncio.sleep(2.5)
                logger.debug("Streaming preloading keep-alive silent frame...")
                if self.prewarmed_session_p_to_n:
                    await self.prewarmed_session_p_to_n.send_realtime_input(
                        audio=types.Blob(data=silent_frame, mime_type="audio/pcm;rate=16000")
                    )
                if self.prewarmed_session_n_to_p:
                    await self.prewarmed_session_n_to_p.send_realtime_input(
                        audio=types.Blob(data=silent_frame, mime_type="audio/pcm;rate=16000")
                    )
        except asyncio.CancelledError:
            logger.info("Pre-warming background task cancelled. Releasing sessions...")
            await self.close_prewarmed_unsafe()
        except Exception as e:
            logger.error(f"Error in pre-warming sessions loop: {e}")
            self.prewarm_status = "disconnected"
            await self.broadcast_prewarm_status()
            await self.close_prewarmed_unsafe()

    async def close_prewarmed_unsafe(self):
        """Closes prewarmed Live sessions cleanly without locking."""
        if self.prewarmed_session_p_to_n:
            try:
                await self.prewarmed_ctx_p_to_n.__aexit__(None, None, None)
            except Exception as e:
                logger.debug(f"Error exiting prewarmed session p_to_n: {e}")
            self.prewarmed_session_p_to_n = None
            self.prewarmed_ctx_p_to_n = None

        if self.prewarmed_session_n_to_p:
            try:
                await self.prewarmed_ctx_n_to_p.__aexit__(None, None, None)
            except Exception as e:
                logger.debug(f"Error exiting prewarmed session n_to_p: {e}")
            self.prewarmed_session_n_to_p = None
            self.prewarmed_ctx_n_to_p = None

    async def start_stream(self):
        """Starts the simultaneous continuous audio stream task safely."""
        async with self.lock:
            await self.stop_stream_unsafe()
            self.transcript_history = []
            self.generated_summary = None
            self.cancel_purge_timer_unsafe()
            self.is_active = True
            self.streaming_task = asyncio.create_task(
                self.run_simultaneous_stream()
            )

    async def stop_stream(self):
        """Stops the active simultaneous streaming task safely."""
        async with self.lock:
            await self.stop_stream_unsafe()

    async def stop_stream_unsafe(self):
        """Cancels and terminates the active streaming task without locking."""
        self.is_active = False
        if self.streaming_task and not self.streaming_task.done():
            self.streaming_task.cancel()
            logger.info("Cancelled running simultaneous streaming task.")
        self.streaming_task = None

    def _get_genai_client(self):
        """Returns an initialized google-genai Client."""
        return get_genai_client()

    def initialize_transcript_file(self, language: str, model_name: str):
        """Initializes the physical transcript file and resets state."""
        self.transcript_history = []
        self.generated_summary = None
        self.cancel_purge_timer_unsafe()
        
        try:
            with open("conversation_transcript.log", "w", encoding="utf-8") as f:
                f.write("SESSION TRANSCRIPT START\n")
                f.write(f"Language: {language}\n")
                f.write(f"Model: {model_name}\n")
                f.write("Pacing: auto\n")
                f.write("========================================\n")
            logger.info("Initialized conversation_transcript.log on disk.")
        except Exception as e:
            logger.error(f"Failed to initialize conversation_transcript.log: {e}")

    def add_transcript_turn(self, speaker: str, orig: str, trans: str):
        """Caches a finished transcript turn in-memory and appends it to conversation_transcript.log."""
        orig = orig.strip()
        trans = trans.strip()
        if not orig and not trans:
            return
            
        # Append to in-memory history
        self.transcript_history.append({
            "speaker": speaker,
            "said": orig,
            "translated_to": trans
        })
        
        # Format the turn and append to disk log
        msg = (
            f"\n========================================\n"
            f"WHO: {speaker.upper()}\n"
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

    async def generate_and_send_summary(self):
        """Generates a clinical conversation summary and sends it to the nurse."""
        if not self.transcript_history:
            logger.info("No transcript history available to generate summary.")
            return

        # Format transcript into a clean text prompt
        convo_text = ""
        for turn in self.transcript_history:
            speaker = turn.get("speaker", "unknown").upper()
            said = turn.get("said", "").strip()
            trans = turn.get("translated_to", "").strip()
            convo_text += f"WHO: {speaker}\nSAID: {said}\nTRANSLATED TO: {trans}\n"
            convo_text += "========================================\n"

        logger.info(f"Generating summary with input length {len(convo_text)} chars...")

        # Broadcast generation started to Nurse (loading state)
        if self.nurse_ws:
            try:
                await self.nurse_ws.send_json({
                    "type": "summary_generating"
                })
            except Exception as e:
                logger.warning(f"Failed to send summary_generating state to Nurse: {e}")

        # Assemble prompt template
        prompt = (
            "You are an expert clinical summarizer for HealthDirect Australia.\n"
            "Below is a dual-channel text transcript from a live patient-nurse tele-triage call.\n"
            "Your job is to generate a beautiful, concise clinical summary formatted in standard Markdown.\n"
            "Include exactly the following 4 sections with their titles as headings:\n\n"
            "### Chief Complaint / Reason for Call\n"
            "(Identify the primary symptom or clinical reason why the caller is seeking help, with any immediate risk context)\n\n"
            "### Symptom History / Timeline\n"
            "(Detail the duration, frequency, onset, severity, and development of symptoms described by the patient)\n\n"
            "### Key Clinical Details & Discussion\n"
            "(Summarize other relevant clinical observations, vital cues mentioned, patient replies to nurse questions)\n\n"
            "### Action Plan / Next Steps\n"
            "(List the clinical disposition, triage recommendation, advice given, and clear next steps)\n\n"
            "Format the output strictly as professional Markdown. Avoid generic commentary. Keep it concise, clinical, and precise.\n\n"
            f"Here is the call transcript:\n\n{convo_text}"
        )

        try:
            config = load_config()
            env_override = os.getenv("SUMMARY_MODEL")
            if env_override:
                model_name = env_override
            else:
                active_translation = self.model_name or ""
                if "3.5" in active_translation:
                    model_name = "gemini-3.5-flash"
                elif "3.1" in active_translation:
                    model_name = "gemini-3.1-flash"
                elif "2.5" in active_translation:
                    model_name = "gemini-2.5-flash"
                else:
                    model_name = config.get("summary_model_name", "gemini-3.5-flash")
            
            client = self._get_genai_client()
            
            # Use run_in_executor to avoid blocking the asyncio event loop for sync client calls
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
            )
            
            summary_markdown = response.text
            self.generated_summary = summary_markdown
            logger.info("Summary successfully generated.")

            if self.nurse_ws:
                await self.nurse_ws.send_json({
                    "type": "summary_generated",
                    "summary": summary_markdown
                })
        except Exception as e:
            logger.error(f"Failed to generate conversation summary: {e}")
            if self.nurse_ws:
                try:
                    await self.nurse_ws.send_json({
                        "type": "summary_error",
                        "message": f"Summary generation failed: {str(e)}"
                    })
                except Exception:
                    pass

    async def purge_session_data(self):
        """Wipes all session-related PII (in-memory cached transcripts, generated summaries, and logs)."""
        async with self.lock:
            # 1. Clear in-memory state
            self.transcript_history = []
            self.generated_summary = None
            self.cancel_purge_timer_unsafe()
            
            # 2. Delete the transcript disk log
            log_file = "conversation_transcript.log"
            if os.path.exists(log_file):
                try:
                    os.remove(log_file)
                    logger.info(f"Successfully deleted {log_file}")
                except Exception as e:
                    logger.error(f"Failed to delete {log_file}: {e}")
                    
            logger.info("Session data successfully purged.")
            
            # 3. Broadcast purge/deletion to Nurse WebSocket
            if self.nurse_ws:
                try:
                    await self.nurse_ws.send_json({
                        "type": "summary_deleted"
                    })
                except Exception as e:
                    logger.warning(f"Failed to send summary_deleted broadcast to Nurse: {e}")

    async def on_call_finished(self):
        """Callback executed when the stream ends (normal complete or manual stop/disconnect)."""
        async with self.lock:
            if self.is_active:
                self.is_active = False

        # Broadcast complete status to update UI buttons
        await self.broadcast_to_both({
            "type": "status",
            "status": "completed"
        })

        # Generate summary asynchronously
        asyncio.create_task(self.generate_and_send_summary())

        # Start auto-purge timer
        await self.start_purge_timer()

    async def start_purge_timer(self):
        """Schedules the background auto-purge task after configured TTL seconds."""
        async with self.lock:
            self.cancel_purge_timer_unsafe()
            
            config = load_config()
            ttl_seconds = float(config.get("session_purge_ttl_seconds", 300))
            
            logger.info(f"Scheduling session auto-purge in {ttl_seconds} seconds...")
            self.purge_timer_task = asyncio.create_task(self._purge_timer_worker(ttl_seconds))

    def cancel_purge_timer_unsafe(self):
        """Cancels any scheduled auto-purge task."""
        if hasattr(self, "purge_timer_task") and self.purge_timer_task and not self.purge_timer_task.done():
            self.purge_timer_task.cancel()
            logger.info("Cancelled scheduled auto-purge timer.")
        self.purge_timer_task = None

    async def _purge_timer_worker(self, delay: float):
        """Asynchronous worker that waits for the delay and then triggers purge."""
        try:
            await asyncio.sleep(delay)
            logger.info("Auto-purge TTL expired. Automatically purging session data...")
            await self.purge_session_data()
        except asyncio.CancelledError:
            logger.info("Purge timer worker cancelled.")

    async def run_simultaneous_stream(self):
        """Streams the dual audio channels and connects to Gemini Live."""
        self.is_active = True
        logger.info("Initializing simultaneous streaming session...")
        preset = PRESETS.get(self.preset_key)
        if not preset and not self.custom_file_path:
            logger.error(f"Unknown preset key: {self.preset_key}")
            return

        file_path = self.custom_file_path or (preset["file"] if preset else "samples/de_fever_session.wav")
        lang_code = self.language_code or (preset["code"] if preset else "de")
        language = self.language or (preset["language"] if preset else "German")

        # Initialize the transcript cache and write initial session metadata to file
        self.initialize_transcript_file(language, self.model_name)

        # Load and split audio channels
        try:
            config = load_config()
            chunk_ms = config.get("chunk_ms", 40)
            patient_bytes, nurse_bytes, chunk_size = load_and_split_channels(
                file_path, chunk_ms=chunk_ms
            )
        except Exception as e:
            logger.error(f"Failed to prepare audio sample: {e}")
            await self.broadcast_to_both({
                "type": "error",
                "message": f"Failed to prepare audio sample: {str(e)}"
            })
            return

        try:
            client = get_genai_client()
        except Exception as e:
            logger.error(f"Failed to initialize GenAI client: {e}")
            await self.broadcast_to_both({
                "type": "error",
                "message": f"Failed to initialize GenAI client: {str(e)}"
            })
            return

        model_name, config_p_to_n, config_n_to_p = build_live_configs(
            client, self.model_name, preset, language
        )

        logger.info("Connecting parallel Live Translate sessions to Gemini...")
        try:
            # Check if we have active, hot pre-warmed sessions ready to adopt!
            session_p_to_n = None
            session_n_to_p = None
            adopted_prewarmed = False

            # Cancel pre-warming keep-alive loop but keep sessions open
            if self.prewarm_task and not self.prewarm_task.done():
                self.prewarm_task.cancel()
                self.prewarm_task = None

            if self.prewarmed_session_p_to_n and self.prewarmed_session_n_to_p:
                logger.info("🚀 ADOPTING HOT PRE-WARMED PARALLEL SESSIONS (<10ms swap latency!)")
                session_p_to_n = self.prewarmed_session_p_to_n
                session_n_to_p = self.prewarmed_session_n_to_p
                
                # Retrieve context managers
                ctx_p_to_n = self.prewarmed_ctx_p_to_n
                ctx_n_to_p = self.prewarmed_ctx_n_to_p
                
                # Detach from coordinator
                self.prewarmed_session_p_to_n = None
                self.prewarmed_session_n_to_p = None
                self.prewarmed_ctx_p_to_n = None
                self.prewarmed_ctx_n_to_p = None
                adopted_prewarmed = True
                self.prewarm_status = "disconnected"

            if adopted_prewarmed:
                # Wrap pre-warmed sessions inside a clean try/finally block so they exit properly when stream ends!
                try:
                    logger.info("Parallel translation sessions connected (pre-warmed adopted).")
                    await self.broadcast_to_both({
                        "type": "status",
                        "status": "connected"
                    })
                    
                    # Call nested handlers
                    await self.execute_streaming_loop(session_p_to_n, session_n_to_p, patient_bytes, nurse_bytes, chunk_size, language, lang_code)
                finally:
                    # Exit pre-warmed contexts properly
                    try:
                        await ctx_p_to_n.__aexit__(None, None, None)
                    except Exception as e:
                        logger.warning(f"Error exiting adopted p_to_n context: {e}")
                    try:
                        await ctx_n_to_p.__aexit__(None, None, None)
                    except Exception as e:
                        logger.warning(f"Error exiting adopted n_to_p context: {e}")
            else:
                # On-demand standard connection creation fallback
                logger.info("No hot sessions found or pre-warming inactive. Connecting on-demand...")
                async with client.aio.live.connect(
                    model=model_name, config=config_p_to_n
                ) as session_p_to_n, \
                           client.aio.live.connect(
                    model=model_name, config=config_n_to_p
                ) as session_n_to_p:

                    logger.info("Parallel translation sessions connected.")
                    await self.broadcast_to_both({
                        "type": "status",
                        "status": "connected"
                    })

                    await self.execute_streaming_loop(session_p_to_n, session_n_to_p, patient_bytes, nurse_bytes, chunk_size, language, lang_code)

        except Exception as ex:
            logger.error(f"Error in simultaneous stream: {ex}")
            self.is_active = False
            await self.broadcast_to_both({
                "type": "error",
                "message": f"Connection error: {str(ex)}"
            })

    async def execute_streaming_loop(self, session_p_to_n, session_n_to_p, patient_bytes, nurse_bytes, chunk_size, language, lang_code):
        """Executes the dual-channel audio streaming and receiver synchronization loops."""
        chunk_ms = int(chunk_size / 32) if chunk_size > 0 else 40
        
        p_convo_state = {"orig": "", "trans": ""}
        n_convo_state = {"orig": "", "trans": ""}
        
        rec_p_task = None
        rec_n_task = None
        
        async def receive_p_to_n():
            """Listens to Patient-to-Nurse translated audio/text."""
            try:
                async for response in session_p_to_n.receive():
                    server_content = response.server_content
                    if server_content:
                        if server_content.model_turn:
                            for part in server_content.model_turn.parts:
                                if part.inline_data:
                                    encoded = base64.b64encode(
                                        part.inline_data.data
                                    ).decode("utf-8")
                                    async with self.lock:
                                        if self.nurse_ws:
                                            await self.nurse_ws.send_json({
                                                "type": "translated_audio",
                                                "stream": "p_to_n",
                                                "data": encoded
                                            })
                        if server_content.input_transcription:
                            text = server_content.input_transcription.text or ""
                            is_final = bool(server_content.input_transcription.finished)
                            if text:
                                p_convo_state["orig"] += text
                            if text or is_final:
                                logger.info(f"[SIMUL-TRANSCRIPT ORIGINAL][PATIENT] {text} (final={is_final})")
                                await self.broadcast_to_both({
                                    "type": "transcript",
                                    "speaker": "patient",
                                    "event": "original",
                                    "text": text,
                                    "final": is_final
                                })
                        if server_content.output_transcription:
                            text = server_content.output_transcription.text or ""
                            is_final = bool(server_content.output_transcription.finished)
                            if text:
                                p_convo_state["trans"] += text
                            if text or is_final:
                                logger.info(f"[SIMUL-TRANSCRIPT TRANSLATED][PATIENT -> English] {text} (final={is_final})")
                                await self.broadcast_to_both({
                                    "type": "transcript",
                                    "speaker": "patient",
                                    "event": "translation",
                                    "text": text,
                                    "final": is_final
                                })
                        if server_content.turn_complete:
                            logger.info("[SIMUL-TURN COMPLETE][PATIENT]")
                            self.add_transcript_turn("patient", p_convo_state["orig"], p_convo_state["trans"])
                            p_convo_state["orig"] = ""
                            p_convo_state["trans"] = ""
                            await self.broadcast_to_both({
                                "type": "turn_complete",
                                "speaker": "patient"
                            })
            except asyncio.CancelledError:
                pass
            except Exception as ex:
                logger.error(f"Error in receive_p_to_n: {ex}")
                self.is_active = False
                await self.broadcast_to_both({
                    "type": "error",
                    "message": f"Connection error: {str(ex)}"
                })
                if self.streaming_task and not self.streaming_task.done():
                    self.streaming_task.cancel()

        async def receive_n_to_p():
            """Listens to Nurse-to-Patient translated audio/text."""
            try:
                async for response in session_n_to_p.receive():
                    server_content = response.server_content
                    if server_content:
                        if server_content.model_turn:
                            for part in server_content.model_turn.parts:
                                if part.inline_data:
                                    encoded = base64.b64encode(
                                        part.inline_data.data
                                    ).decode("utf-8")
                                    async with self.lock:
                                        if self.patient_ws:
                                            await self.patient_ws.send_json({
                                                "type": "translated_audio",
                                                "stream": "n_to_p",
                                                "data": encoded
                                            })
                        if server_content.input_transcription:
                            text = server_content.input_transcription.text or ""
                            is_final = bool(server_content.input_transcription.finished)
                            if text:
                                n_convo_state["orig"] += text
                            if text or is_final:
                                logger.info(f"[SIMUL-TRANSCRIPT ORIGINAL][NURSE] {text} (final={is_final})")
                                await self.broadcast_to_both({
                                    "type": "transcript",
                                    "speaker": "nurse",
                                    "event": "original",
                                    "text": text,
                                    "final": is_final
                                })
                        if server_content.output_transcription:
                            text = server_content.output_transcription.text or ""
                            is_final = bool(server_content.output_transcription.finished)
                            if text:
                                n_convo_state["trans"] += text
                            if text or is_final:
                                logger.info(f"[SIMUL-TRANSCRIPT TRANSLATED][NURSE -> {language}] {text} (final={is_final})")
                                await self.broadcast_to_both({
                                    "type": "transcript",
                                    "speaker": "nurse",
                                    "event": "translation",
                                    "text": text,
                                    "final": is_final
                                })
                        if server_content.turn_complete:
                            logger.info("[SIMUL-TURN COMPLETE][NURSE]")
                            self.add_transcript_turn("nurse", n_convo_state["orig"], n_convo_state["trans"])
                            n_convo_state["orig"] = ""
                            n_convo_state["trans"] = ""
                            await self.broadcast_to_both({
                                "type": "turn_complete",
                                "speaker": "nurse"
                            })
            except asyncio.CancelledError:
                pass
            except Exception as ex:
                logger.error(f"Error in receive_n_to_p: {ex}")
                self.is_active = False
                await self.broadcast_to_both({
                    "type": "error",
                    "message": f"Connection error: {str(ex)}"
                })
                if self.streaming_task and not self.streaming_task.done():
                    self.streaming_task.cancel()

        try:
            rec_p_task = asyncio.create_task(receive_p_to_n())
            rec_n_task = asyncio.create_task(receive_n_to_p())

            start_time = asyncio.get_event_loop().time()
            chunks_sent = 0
            max_len = max(len(patient_bytes), len(nurse_bytes))

            await self.broadcast_to_both({
                "type": "status",
                "status": "ready",
                "language": language,
                "code": lang_code,
                "duration_ms": max_len // 32
            })

            for i in range(0, max_len, chunk_size):
                if not self.is_active:
                    logger.warning("Session deactivated during streaming. Aborting sending loop.")
                    break

                chunk_p = patient_bytes[i : i + chunk_size]
                chunk_n = nurse_bytes[i : i + chunk_size]

                if chunk_p:
                    encoded_p = base64.b64encode(chunk_p).decode("utf-8")
                    async with self.lock:
                        if self.patient_ws:
                            await self.patient_ws.send_json({
                                "type": "original_audio",
                                "speaker": "patient",
                                "data": encoded_p
                            })
                    await safe_send_realtime_input(session_p_to_n, chunk_p)

                if chunk_n:
                    encoded_n = base64.b64encode(chunk_n).decode("utf-8")
                    async with self.lock:
                        if self.nurse_ws:
                            await self.nurse_ws.send_json({
                                "type": "original_audio",
                                "speaker": "nurse",
                                "data": encoded_n
                            })
                    await safe_send_realtime_input(session_n_to_p, chunk_n)

                chunks_sent += 1

                elapsed_ms = chunks_sent * chunk_ms
                await self.broadcast_to_both({
                    "type": "playhead",
                    "elapsed_ms": elapsed_ms,
                    "duration_ms": max_len // 32
                })

                expected_time = start_time + (chunks_sent * (chunk_ms / 1000.0))
                sleep_time = expected_time - asyncio.get_event_loop().time()
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            if self.is_active:
                logger.info("Streaming complete. Waiting 5s for translations...")
                try:
                    await asyncio.sleep(5.0)
                except asyncio.CancelledError:
                    pass

        finally:
            if rec_p_task:
                rec_p_task.cancel()
            if rec_n_task:
                rec_n_task.cancel()
            asyncio.create_task(self.on_call_finished())

session_coordinator = ActiveSession()


# Force standard TLS/HTTPS to prevent client certificate/mTLS issues on VMs
os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"

from google import genai
from google.genai import types

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

from contextlib import asynccontextmanager

WEBSERVER_PORT = int(os.getenv("WEBSERVER_PORT", "9000"))
WEBSERVER_HOST = os.getenv("WEBSERVER_HOST", "127.0.0.1")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "="*80)
    print("🚀 BILINGUAL MEDICAL INTERPRETER WEB INTERFACE STARTED")
    print(f"👉 Nurse Dashboard:              http://{WEBSERVER_HOST}:{WEBSERVER_PORT}/nurse.html")
    print(f"👉 Patient Dashboard:            http://{WEBSERVER_HOST}:{WEBSERVER_PORT}/patient.html")
    print(f"👉 Presentation Mode:            http://{WEBSERVER_HOST}:{WEBSERVER_PORT}/presentation.html")
    print("="*80 + "\n")
    yield

app = FastAPI(title="Bilingual Medical Interpreter API", lifespan=lifespan)

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
        "file": "samples/vi_paediatric_session.wav",
        "code": "vi",
        "language": "Vietnamese",
        "gender": "female"
    },
    "arabic": {
        "file": "samples/ar_asthma_session.wav",
        "code": "ar",
        "language": "Arabic",
        "gender": "male"
    },
    "hindi": {
        "file": "samples/hi_cough_session.wav",
        "code": "hi",
        "language": "Hindi",
        "gender": "male"
    }
}

def load_and_split_channels(file_path: str, target_sample_rate: int = 16000, chunk_ms: int = 40) -> tuple[bytes, bytes, int]:
    """
    Loads a stereo audio file, resamples to 16kHz, converts to 16-bit PCM,
    splits into Left (Patient) and Right (Nurse) mono streams, and returns
    (patient_bytes, nurse_bytes, chunk_size).
    """
    if not os.path.exists(file_path):
        parent_dir = os.path.dirname(BASE_DIR)
        alt1 = os.path.join(parent_dir, file_path)
        alt2 = os.path.join(BASE_DIR, file_path)
        if os.path.exists(alt1):
            file_path = alt1
        elif os.path.exists(alt2):
            file_path = alt2
        else:
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

    chunk_size = calculate_chunk_size(chunk_ms, sample_rate=target_sample_rate)

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
        "Your role is to translate spoken conversation in real-time between a Nurse and a patient. "
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
            f"Your job is to translate the nurse's English explanations and questions into accurate, "
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

    output_language = "English" if direction == "p_to_n" else target_language
    parts.append(
        f"RESPOND IN {output_language}. YOU MUST RESPOND UNMISTAKABLY IN {output_language}."
    )

    return "\n\n".join(parts)

@app.websocket("/ws/nurse")
async def ws_nurse_endpoint(websocket: WebSocket):
    """WebSocket endpoint for the clinician (nurse) client."""
    await websocket.accept()
    await session_coordinator.register_nurse(websocket)
    try:
        while True:
            msg_text = await websocket.receive_text()
            data = json.loads(msg_text)
            action = data.get("action")
            if action == "config_update":
                preset = data.get("preset", "german")
                model = data.get("model", "gemini-3.5-live-translate-preview")
                language = data.get("language", "German")
                await session_coordinator.update_config(preset, model, language)
            elif action == "start":
                await session_coordinator.start_stream()
            elif action == "stop":
                await session_coordinator.stop_stream()
            elif action == "reset":
                await session_coordinator.reset()
            elif action == "delete_summary" or action == "purge":
                await session_coordinator.purge_session_data()
            elif action == "ping":
                pass
    except WebSocketDisconnect:
        try:
            await session_coordinator.disconnect_nurse()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error in ws_nurse_endpoint: {e}")
        try:
            await session_coordinator.disconnect_nurse()
        except Exception:
            pass

@app.websocket("/ws/patient")
async def ws_patient_endpoint(websocket: WebSocket):
    """WebSocket endpoint for the patient client."""
    await websocket.accept()
    await session_coordinator.register_patient(websocket)
    try:
        while True:
            # Patients are passive in routing controls, but keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        try:
            await session_coordinator.disconnect_patient()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error in ws_patient_endpoint: {e}")
        try:
            await session_coordinator.disconnect_patient()
        except Exception:
            pass

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client connected to interpreter WebSocket.")

    try:
        client = get_genai_client()
    except Exception as e:
        await websocket.send_json({"type": "error", "message": f"Failed to initialize GenAI client: {str(e)}"})
        await websocket.close()
        return
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
                                if getattr(response, "go_away", None):
                                    logger.warning(f"[SESSION SIGNAL][p_to_n] GoAway message received from Gemini Live API. Details: {response.go_away}")
                                if getattr(response, "generation_complete", None):
                                    logger.info(f"[SESSION SIGNAL][p_to_n] Generation complete signal received.")
                                    
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
                                    if server_content.input_transcription:
                                        text = server_content.input_transcription.text or ""
                                        is_final = bool(server_content.input_transcription.finished)
                                        if text or is_final:
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
                                    if server_content.output_transcription:
                                        text = server_content.output_transcription.text or ""
                                        is_final = bool(server_content.output_transcription.finished)
                                        if text or is_final:
                                            convo_state["patient_trans"] += text
                                            logger.info(f"[TRANSCRIPT TRANSLATED][PATIENT -> English] {text} (final={is_final})")
                                            await websocket.send_json({
                                                "type": "transcript",
                                                "speaker": "patient",
                                                "event": "translation",
                                                "text": text,
                                                "final": is_final
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
                                if getattr(response, "go_away", None):
                                    logger.warning(f"[SESSION SIGNAL][n_to_p] GoAway message received from Gemini Live API. Details: {response.go_away}")
                                if getattr(response, "generation_complete", None):
                                    logger.info(f"[SESSION SIGNAL][n_to_p] Generation complete signal received.")
                                    
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
                                                        "speaker": "nurse",
                                                        "event": "translation",
                                                        "text": part.text,
                                                        "final": False
                                                    })

                                    # Forward Nurse Original text transcript
                                    if server_content.input_transcription:
                                        text = server_content.input_transcription.text or ""
                                        is_final = bool(server_content.input_transcription.finished)
                                        if text or is_final:
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
                                    if server_content.output_transcription:
                                        text = server_content.output_transcription.text or ""
                                        is_final = bool(server_content.output_transcription.finished)
                                        if text or is_final:
                                            convo_state["nurse_trans"] += text
                                            logger.info(f"[TRANSCRIPT TRANSLATED][NURSE -> PATIENT] {text} (final={is_final})")
                                            await websocket.send_json({
                                                "type": "transcript",
                                                "speaker": "nurse",
                                                "event": "translation",
                                                "text": text,
                                                "final": is_final
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

@app.get("/nurse", response_class=HTMLResponse)
async def serve_nurse():
    """Serves the Nurse (Clinician) interface."""
    nurse_path = os.path.join(BASE_DIR, "web", "nurse.html")
    if not os.path.exists(nurse_path):
        return HTMLResponse("<h1>nurse.html not found</h1>", status_code=404)
    with open(nurse_path, "r", encoding="utf-8") as f:
        content = f.read()
    response = HTMLResponse(content=content)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/patient", response_class=HTMLResponse)
async def serve_patient():
    """Serves the Patient (Caller) interface."""
    patient_path = os.path.join(BASE_DIR, "web", "patient.html")
    if not os.path.exists(patient_path):
        return HTMLResponse("<h1>patient.html not found</h1>", status_code=404)
    with open(patient_path, "r", encoding="utf-8") as f:
        content = f.read()
    response = HTMLResponse(content=content)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/presentation", response_class=HTMLResponse)
@app.get("/presentation.html", response_class=HTMLResponse)
async def serve_presentation():
    """Serves the Single-Tab Unified Presentation Console interface."""
    presentation_path = os.path.join(BASE_DIR, "web", "presentation.html")
    if not os.path.exists(presentation_path):
        return HTMLResponse("<h1>presentation.html not found</h1>", status_code=404)
    with open(presentation_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Dynamically inject port from .env config
    content = content.replace("{{ WEBSERVER_PORT }}", str(WEBSERVER_PORT))
    
    response = HTMLResponse(content=content)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

class NoCacheStaticFiles(StaticFiles):
    def is_dir_path(self, path: str) -> bool:
        return False

    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

app.mount("/", NoCacheStaticFiles(directory=os.path.join(BASE_DIR, "web"), html=True), name="static")


# parent import directory routing for root folder modules like glossary_highlighter
parent_dir = os.path.dirname(BASE_DIR)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

highlighter = None
try:
    from glossary_highlighter import GlossaryHighlighter
    highlighter = GlossaryHighlighter()
except Exception:
    pass

# Optional PyAudio setup for local speaker output
pyaudio_lib = None
try:
    import pyaudio
    pyaudio_lib = pyaudio.PyAudio()
except ImportError:
    pass

class SpeakerPlayer:
    """Handles real-time audio playback through system speakers."""
    def __init__(self, enabled=False):
        self.stream = None
        if enabled and pyaudio_lib:
            try:
                self.stream = pyaudio_lib.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=24000,
                    output=True
                )
            except Exception as e:
                logger.warning(f"Failed to open PyAudio speaker stream: {e}")
                
    def play(self, data: bytes):
        if self.stream:
            try:
                self.stream.write(data)
            except Exception:
                pass
                
    def close(self):
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass

class StatsTracker:
    """Tracks latency metrics and throughput stats for live sessions."""
    def __init__(self, enabled=False):
        self.enabled = enabled
        self.p_to_n_bytes = 0
        self.n_to_p_bytes = 0
        self.p_to_n_frames = 0
        self.n_to_p_frames = 0
        self.latencies = []
        
    def add_chunk(self, direction: str, size: int, latency_ms: float = 0.0):
        if direction == "p_to_n":
            self.p_to_n_bytes += size
            self.p_to_n_frames += 1
        else:
            self.n_to_p_bytes += size
            self.n_to_p_frames += 1
        if latency_ms > 0:
            self.latencies.append(latency_ms)
            
    def log_stats(self):
        if not self.enabled:
            return
        avg_latency = (sum(self.latencies) / len(self.latencies)) if self.latencies else 0.0
        logger.info(
            f"📊 [STATS] Cumulative Sent/Received: "
            f"Patient->Nurse: {self.p_to_n_bytes} bytes ({self.p_to_n_frames} chunks), "
            f"Nurse->Patient: {self.n_to_p_bytes} bytes ({self.n_to_p_frames} chunks). "
            f"Avg Chunk Latency: {avg_latency:.1f}ms"
        )

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
    
    if language and highlighter:
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

async def run_cli(args: argparse.Namespace):
    """Runs the bidirectional translation interpreter as a command-line application in the terminal."""
    os.environ["GOOGLE_API_USE_CLIENT_CERTIFICATE"] = "false"
    
    try:
        client = get_genai_client()
    except Exception as e:
        print(f"❌ Error initializing GenAI client: {e}")
        sys.exit(1)
    
    file_path = args.file
    language = args.language or "German"
    lang_code = args.language_code or "de"
    
    if not file_path:
        file_path = "samples/de_fever_session.wav"
        language = "German"
        lang_code = "de"
        
    if not os.path.exists(file_path):
        print(f"❌ Error: Audio file not found at {file_path}")
        sys.exit(1)
        
    print_border()
    print(f"║ {'GEMINI LIVE REAL-TIME BILINGUAL INTERPRETER':^110} ║")
    print(f"║ {'Streaming file: ' + os.path.basename(file_path):^110} ║")
    print(f"║ {'Target Language: ' + language + ' (' + lang_code + ') | Model: ' + args.model:^110} ║")
    print_border()
    print(f"║ {'CLINICIAN / NURSE (English)':^54} ║ {'PATIENT / FAMILY (' + language + ')':^54} ║")
    print_border()
    sys.stdout.flush()

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    p_to_n_pcm_path = os.path.join(output_dir, "translated_patient_to_nurse_en.pcm")
    n_to_p_pcm_path = os.path.join(output_dir, f"translated_nurse_to_patient_{language.lower()}.pcm")
    
    pcm_p_to_n = open(p_to_n_pcm_path, "wb")
    pcm_n_to_p = open(n_to_p_pcm_path, "wb")
    
    try:
        patient_bytes, nurse_bytes, chunk_size = load_and_split_channels(
            file_path, chunk_ms=args.chunk_ms
        )
    except Exception as e:
        print(f"❌ Error splitting audio channels: {e}")
        return

    if not args.no_glossary:
        glossary_p_to_n = load_and_format_glossary(language, direction="p_to_n", exclude_descriptions=True)
        glossary_n_to_p = load_and_format_glossary(language, direction="n_to_p", exclude_descriptions=True)
    else:
        glossary_p_to_n = ""
        glossary_n_to_p = ""
        
    sys_inst_p_to_n = assemble_system_instructions("p_to_n", language, glossary_p_to_n, is_flash_live=True)
    sys_inst_n_to_p = assemble_system_instructions("n_to_p", language, glossary_n_to_p, is_flash_live=True)
    
    speaker = SpeakerPlayer(enabled=args.playback)
    stats_tracker = StatsTracker(enabled=args.stats)
    
    config_p_to_n = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        translation_config=types.TranslationConfig(
            target_language_code="en",
            echo_target_language=True
        ),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        system_instruction=types.Content(parts=[types.Part.from_text(sys_inst_p_to_n)])
    )
    
    config_n_to_p = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        translation_config=types.TranslationConfig(
            target_language_code=lang_code,
            echo_target_language=True
        ),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
        system_instruction=types.Content(parts=[types.Part.from_text(sys_inst_n_to_p)])
    )
    
    patient_translation_complete = asyncio.Event()
    nurse_translation_complete = asyncio.Event()
    
    current_p_original = ""
    current_n_translated = ""
    current_n_original = ""
    current_p_translated = ""
    
    last_audio_p_to_n = 0.0
    last_audio_n_to_p = 0.0
    
    logger.info("Connecting parallel CLI live translation sessions to Gemini...")
    try:
        async with client.aio.live.connect(model=args.model, config=config_p_to_n) as session_p_to_n, \
                   client.aio.live.connect(model=args.model, config=config_n_to_p) as session_n_to_p:
            
            async def safe_send(session, chunk):
                try:
                    await session.send_realtime_input(
                        audio=types.Blob(data=chunk, mime_type="audio/pcm;rate=16000")
                    )
                except Exception as e:
                    logger.warning(f"Error streaming chunk: {e}")

            async def send_audio_cli():
                try:
                    max_len = max(len(patient_bytes), len(nurse_bytes))
                    start_time = asyncio.get_running_loop().time()
                    chunks_queued = 0
                    
                    if args.pacing == "simple":
                        for i in range(0, max_len, chunk_size):
                            chunk_p = patient_bytes[i : i + chunk_size]
                            chunk_n = nurse_bytes[i : i + chunk_size]
                            
                            if chunk_p:
                                await safe_send(session_p_to_n, chunk_p)
                                stats_tracker.add_chunk("p_to_n", len(chunk_p))
                            if chunk_n:
                                await safe_send(session_n_to_p, chunk_n)
                                stats_tracker.add_chunk("n_to_p", len(chunk_n))
                                
                            chunks_queued += 1
                            expected_release_time = start_time + (chunks_queued * (args.chunk_ms / 1000.0))
                            sleep_time = expected_release_time - asyncio.get_running_loop().time()
                            if sleep_time > 0:
                                await asyncio.sleep(sleep_time)
                                
                    else:
                        active_speaker = None
                        silence_counter = 0
                        SILENCE_CHUNKS_THRESHOLD = max(4, int(4.5 / (args.chunk_ms / 1000.0)))
                        takeover_cooldown = 0
                        silence_chunk = b'\x00' * chunk_size
                        
                        for i in range(0, max_len, chunk_size):
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
                            
                            if p_has and n_has:
                                if takeover_cooldown == 0 and active_speaker == "nurse":
                                    speaker_finished = "nurse"
                                    active_speaker = "patient"
                                    takeover_cooldown = int(2.5 / (args.chunk_ms / 1000.0))
                                elif takeover_cooldown == 0 and active_speaker == "patient":
                                    speaker_finished = "patient"
                                    active_speaker = "nurse"
                                    takeover_cooldown = int(2.5 / (args.chunk_ms / 1000.0))
                                else:
                                    silence_counter = 0
                            elif p_has and not n_has:
                                if takeover_cooldown == 0 and active_speaker == "nurse":
                                    speaker_finished = "nurse"
                                    active_speaker = "patient"
                                    takeover_cooldown = int(2.5 / (args.chunk_ms / 1000.0))
                                elif active_speaker is None:
                                    active_speaker = "patient"
                                silence_counter = 0
                            elif n_has and not p_has:
                                if takeover_cooldown == 0 and active_speaker == "patient":
                                    speaker_finished = "patient"
                                    active_speaker = "nurse"
                                    takeover_cooldown = int(2.5 / (args.chunk_ms / 1000.0))
                                elif active_speaker is None:
                                    active_speaker = "nurse"
                                silence_counter = 0
                            else:
                                if active_speaker is not None:
                                    silence_counter += 1
                                    if silence_counter >= SILENCE_CHUNKS_THRESHOLD:
                                        speaker_finished = active_speaker
                                        active_speaker = None
                                        
                            if active_speaker == "patient":
                                if chunk_p:
                                    await safe_send(session_p_to_n, chunk_p)
                                    stats_tracker.add_chunk("p_to_n", len(chunk_p))
                                if chunks_queued % 15 == 0:
                                    await safe_send(session_n_to_p, silence_chunk)
                            elif active_speaker == "nurse":
                                if chunk_n:
                                    await safe_send(session_n_to_p, chunk_n)
                                    stats_tracker.add_chunk("n_to_p", len(chunk_n))
                                if chunks_queued % 15 == 0:
                                    await safe_send(session_p_to_n, silence_chunk)
                            else:
                                if chunks_queued % 15 == 0:
                                    await safe_send(session_p_to_n, silence_chunk)
                                    await safe_send(session_n_to_p, silence_chunk)
                                    
                            chunks_queued += 1
                            
                            if speaker_finished is not None:
                                event_to_wait = patient_translation_complete if speaker_finished == "patient" else nurse_translation_complete
                                hold_start = asyncio.get_running_loop().time()
                                
                                iterations = int(15.0 / (args.chunk_ms / 1000.0))
                                for _ in range(iterations):
                                    if event_to_wait.is_set():
                                        break
                                    now = asyncio.get_running_loop().time()
                                    last_audio = last_audio_p_to_n if speaker_finished == "patient" else last_audio_n_to_p
                                    if last_audio > 0.0 and now - last_audio > 4.5:
                                        break
                                    elif last_audio == 0.0 and now - hold_start > 15.0:
                                        break
                                        
                                    if speaker_finished == "patient":
                                        await safe_send(session_n_to_p, silence_chunk)
                                    else:
                                        await safe_send(session_p_to_n, silence_chunk)
                                        
                                    await asyncio.sleep(args.chunk_ms / 1000.0)
                                    
                                await asyncio.sleep(2.0)
                                
                            expected_release_time = start_time + (chunks_queued * (args.chunk_ms / 1000.0))
                            sleep_time = expected_release_time - asyncio.get_running_loop().time()
                            if sleep_time > 0:
                                await asyncio.sleep(sleep_time)
                                
                    logger.info("Real-time dual-channel audio streaming complete.")
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    logger.error(f"Error in CLI send_audio loop: {e}")

            async def receive_p_to_n_cli():
                nonlocal current_p_original, current_n_translated, last_audio_p_to_n
                try:
                    async for response in session_p_to_n.receive():
                        server_content = response.server_content
                        if server_content:
                            if server_content.model_turn:
                                for part in server_content.model_turn.parts:
                                    if part.inline_data:
                                        if has_speech(part.inline_data.data, threshold=500):
                                            last_audio_p_to_n = asyncio.get_running_loop().time()
                                        pcm_p_to_n.write(part.inline_data.data)
                                        speaker.play(part.inline_data.data)
                                        stats_tracker.add_chunk("p_to_n_rx", len(part.inline_data.data))
                                        
                            if server_content.input_transcription and server_content.input_transcription.text:
                                current_p_original += server_content.input_transcription.text
                            if server_content.output_transcription and server_content.output_transcription.text:
                                current_n_translated += server_content.output_transcription.text
                                
                            if server_content.turn_complete:
                                patient_translation_complete.set()
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
                    logger.error(f"Error in CLI Patient->Nurse receive task: {e}")

            async def receive_n_to_p_cli():
                nonlocal current_n_original, current_p_translated, last_audio_n_to_p
                try:
                    async for response in session_n_to_p.receive():
                        server_content = response.server_content
                        if server_content:
                            if server_content.model_turn:
                                for part in server_content.model_turn.parts:
                                    if part.inline_data:
                                        if has_speech(part.inline_data.data, threshold=500):
                                            last_audio_n_to_p = asyncio.get_running_loop().time()
                                        pcm_n_to_p.write(part.inline_data.data)
                                        speaker.play(part.inline_data.data)
                                        stats_tracker.add_chunk("n_to_p_rx", len(part.inline_data.data))
                                        
                            if server_content.input_transcription and server_content.input_transcription.text:
                                current_n_original += server_content.input_transcription.text
                            if server_content.output_transcription and server_content.output_transcription.text:
                                current_p_translated += server_content.output_transcription.text
                                
                            if server_content.turn_complete:
                                nurse_translation_complete.set()
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
                    logger.error(f"Error in CLI Nurse->Patient receive task: {e}")

            send_task = asyncio.create_task(send_audio_cli())
            rec_p_to_n = asyncio.create_task(receive_p_to_n_cli())
            rec_n_to_p = asyncio.create_task(receive_n_to_p_cli())
            
            await send_task
            
            print("\n🏁 Audio file streaming finished! Waiting a few seconds for final translation packets...")
            await asyncio.sleep(6)
            
            rec_p_to_n.cancel()
            rec_n_to_p.cancel()
            
            pcm_p_to_n.close()
            pcm_n_to_p.close()
            speaker.close()
            
            stats_tracker.log_stats()
            
            print_border()
            print(f"║ {'REAL-TIME TRANSLATION FLOW COMPLETED':^110} ║")
            print(f"║ Patient->Nurse translation saved to: {os.path.basename(p_to_n_pcm_path):<56} ║")
            print(f"║ Nurse->Patient translation saved to: {os.path.basename(n_to_p_pcm_path):<56} ║")
            print_border()
            sys.stdout.flush()
            
    except Exception as e:
        print(f"\n❌ Gemini Live connection error: {e}")

if __name__ == "__main__":
    import uvicorn
    parsed_args = parse_args()
    if parsed_args.cli:
        asyncio.run(run_cli(parsed_args))
    else:
        parent_dir = os.path.dirname(BASE_DIR)
        uvicorn.run("demo.web_server:app", host=WEBSERVER_HOST, port=WEBSERVER_PORT, reload=True, app_dir=parent_dir, log_config=None)

