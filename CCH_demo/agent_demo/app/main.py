# Load environment variables at the absolute entrypoint BEFORE importing any Google or ADK libraries
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True)

# Force IPv4 to resolve WebSocket handshake timeouts caused by broken IPv6 routing on this environment
import socket
_old_getaddrinfo = socket.getaddrinfo
def _new_getaddrinfo(*args, **kwargs):
    responses = _old_getaddrinfo(*args, **kwargs)
    return [r for r in responses if r[0] == socket.AF_INET]
socket.getaddrinfo = _new_getaddrinfo

import asyncio

import base64
import json
import logging
import warnings

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from google.adk.agents.live_request_queue import LiveRequestQueue
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from cch_agent.agent import agent


# Configure main application logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Setup dedicated call transcript file logger (#BUG-24)
logs_dir = Path(__file__).parent / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)
transcript_log_file = logs_dir / "call_transcripts.log"

transcript_formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
transcript_handler = logging.FileHandler(transcript_log_file, encoding="utf-8")
transcript_handler.setFormatter(transcript_formatter)

call_transcript_logger = logging.getLogger("call_transcripts")
call_transcript_logger.setLevel(logging.INFO)
call_transcript_logger.addHandler(transcript_handler)

# Suppress verbose third-party loggers (websockets frames, HTTP connections, OpenTelemetry detach warnings)
logging.getLogger("websockets").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("google").setLevel(logging.WARNING)
logging.getLogger("google_adk").setLevel(logging.WARNING)
logging.getLogger("opentelemetry").setLevel(logging.ERROR)

# Suppress Pydantic serialization warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
warnings.filterwarnings("ignore", message=".*Failed to detach context.*")

# Application name constant
APP_NAME = "cch-demo"

# ========================================
# Phase 1: Application Initialization (once at startup)
# ========================================

app = FastAPI()

# Mount static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Define your session service
session_service = InMemorySessionService()

# Define your runner
runner = Runner(app_name=APP_NAME, agent=agent, session_service=session_service)

# ========================================
# HTTP Endpoints
# ========================================


@app.get("/")
async def root():
    """Serve the index.html page."""
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/favicon.ico")
async def favicon():
    """Serve Cymbal Children's Hospital favicon.ico asset (#BUG-47)."""
    favicon_path = Path(__file__).parent / "static" / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/x-icon")
    from fastapi.responses import Response
    return Response(status_code=204)


# ========================================
# WebSocket Endpoint
# ========================================


@app.websocket("/ws/{user_id}/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    session_id: str,
    proactivity: bool = False,
    affective_dialog: bool = False,
    fresh: bool = False,
) -> None:
    """WebSocket endpoint for bidirectional streaming with ADK.

    Args:
        websocket: The WebSocket connection
        user_id: User identifier
        session_id: Session identifier
        proactivity: Enable proactive audio (native audio models only)
        affective_dialog: Enable affective dialog (native audio models only)
        fresh: Force creation of a fresh clean session, wiping any previous history/images
    """
    logger.debug(
        f"WebSocket connection request: user_id={user_id}, session_id={session_id}, "
        f"proactivity={proactivity}, affective_dialog={affective_dialog}, fresh={fresh}"
    )
    await websocket.accept()
    logger.debug("WebSocket connection accepted")

    # ========================================
    # Phase 2: Session Initialization (once per streaming session)
    # ========================================

    # Automatically determine response modality based on model architecture
    model_name = agent.model
    is_native_audio = "native-audio" in model_name.lower()

    # Session resumption should only be enabled if explicitly requested and NOT a fresh run
    # Disabling session resumption by default prevents old practice run images/turns from leaking into new sessions
    session_resumption_cfg = None if fresh else types.SessionResumptionConfig()

    if is_native_audio:
        response_modalities = ["AUDIO"]

        # Note: Proactivity (proactive_audio) is currently rejected by the Gemini Live API backend
        # for standard live models with APIError 1000. Disable it with a warning if requested.
        effective_proactivity = None
        if proactivity:
            logger.warning(
                f"Proactivity (proactive audio) is currently not supported by the Live API endpoint "
                f"for model {model_name}. Disabling proactivity to prevent Live API error 1000."
            )

        input_audio_transcription_cfg = types.AudioTranscriptionConfig(
            language_hints=types.LanguageHints(language_codes=["en-AU", "ar"])
        )

        output_audio_transcription_cfg = types.AudioTranscriptionConfig(
            language_hints=types.LanguageHints(language_codes=["en-AU", "ar"])
        )

        speech_cfg = types.SpeechConfig(
            language_code="en-AU",
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Aoede")
            )
        )

        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=response_modalities,
            speech_config=speech_cfg,
            input_audio_transcription=input_audio_transcription_cfg,
            output_audio_transcription=output_audio_transcription_cfg,
            session_resumption=session_resumption_cfg,
            proactivity=effective_proactivity,
            enable_affective_dialog=affective_dialog
            if affective_dialog
            else None,
        )
        logger.debug(
            f"Native audio model detected: {model_name}, "
            f"using AUDIO response modality, "
            f"proactivity={proactivity}, affective_dialog={affective_dialog}"
        )
    else:
        response_modalities = ["TEXT"]
        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=response_modalities,
            input_audio_transcription=None,
            output_audio_transcription=None,
            session_resumption=session_resumption_cfg,
        )
        logger.debug(
            f"Half-cascade model detected: {model_name}, "
            "using TEXT response modality"
        )
        if proactivity or affective_dialog:
            logger.warning(
                f"Proactivity and affective dialog are only supported on native "
                f"audio models. Current model: {model_name}. "
                f"These settings will be ignored."
            )
    logger.debug(f"RunConfig created: {run_config}")

    # Get or create session
    if fresh:
        logger.info(f"Fresh session requested for user_id={user_id}, session_id={session_id}. Resetting session state.")
        await session_service.delete_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
    else:
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
        if not session:
            session = await session_service.create_session(
                app_name=APP_NAME, user_id=user_id, session_id=session_id
            )

    live_request_queue = LiveRequestQueue()

    # ========================================
    # Phase 3: Active Session (concurrent bidirectional communication)
    # ========================================

    async def upstream_task() -> None:
        """Receives messages from WebSocket and sends to LiveRequestQueue."""
        logger.debug("upstream_task started")
        try:
            while True:
                # Receive message from WebSocket (text or binary)
                try:
                    message = await websocket.receive()
                except (WebSocketDisconnect, RuntimeError):
                    logger.debug("Upstream websocket disconnected or closed")
                    break

                if message.get("type") == "websocket.disconnect":
                    logger.debug("Upstream disconnect message received")
                    break

                # Handle binary frames (audio data)
                if "bytes" in message:
                    audio_data = message["bytes"]
                    logger.debug(
                        f"Received binary audio chunk: {len(audio_data)} bytes"
                    )

                    audio_blob = types.Blob(
                        mime_type="audio/pcm;rate=16000", data=audio_data
                    )
                    live_request_queue.send_realtime(audio_blob)

                # Handle text frames (JSON messages)
                elif "text" in message:
                    text_data = message["text"]
                    logger.debug(f"Received text message: {text_data[:100]}...")

                    json_message = json.loads(text_data)

                    # Extract text from JSON and send to LiveRequestQueue
                    if json_message.get("type") == "text":
                        text_val = json_message["text"]
                        logger.debug(
                            f"Sending text content: {text_val}"
                        )
                        call_transcript_logger.info(f"[USER_TEXT] user_id={user_id} session_id={session_id}: {text_val}")
                        content = types.Content(
                            parts=[types.Part(text=text_val)]
                        )
                        live_request_queue.send_content(content)

                    # Handle image data
                    elif json_message.get("type") == "image":
                        image_data = base64.b64decode(json_message["data"])
                        mime_type = json_message.get("mimeType", "image/jpeg")
                        send_as_content = json_message.get("send_as_content", False)

                        logger.info(
                            f"[DOC_IMAGE_RECEIVED] Processing image payload: {len(image_data)} bytes, "
                            f"type: {mime_type}, as_content: {send_as_content}"
                        )
                        call_transcript_logger.info(f"[USER_IMAGE_ATTACHMENT] user_id={user_id} session_id={session_id}: Attached document image ({len(image_data)} bytes)")

                        # Send image as blob
                        image_blob = types.Blob(
                            mime_type=mime_type, data=image_data
                        )

                        if send_as_content:
                            # Send as persistent conversational turn part
                            content = types.Content(
                                parts=[
                                    types.Part(text="[DOCUMENT_IMAGE_PAYLOAD_ATTACHED]"),
                                    types.Part(inline_data=image_blob)
                                ]
                            )
                            live_request_queue.send_content(content)
                        else:
                            # Send as transient real-time stream chunk
                            live_request_queue.send_realtime(image_blob)
        except asyncio.CancelledError:
            logger.debug("upstream_task cancelled")

    def _truncate_long_fields(data: dict) -> dict:
        """Recursively truncate very long string values in a dictionary for cleaner logging."""
        if isinstance(data, dict):
            return {k: _truncate_long_fields(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [_truncate_long_fields(x) for x in data]
        elif isinstance(data, str) and len(data) > 100:
            return f"{data[:60]}... [truncated {len(data)} chars]"
        return data

    async def downstream_task() -> None:
        """Receives Events from run_live() and sends to WebSocket."""
        logger.debug("downstream_task started, calling runner.run_live()")
        logger.debug(
            f"Starting run_live with user_id={user_id}, session_id={session_id}"
        )
        try:
            async for event in runner.run_live(
                user_id=user_id,
                session_id=session_id,
                live_request_queue=live_request_queue,
                run_config=run_config,
            ):
                event_json = event.model_dump_json(exclude_none=True, by_alias=True)
                log_event = _truncate_long_fields(json.loads(event_json))
                logger.debug(f"[SERVER] Event: {json.dumps(log_event)}")

                # Log extracted agent text / transcription to file logger (#BUG-24)
                if hasattr(event, "content") and event.content and hasattr(event.content, "parts"):
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            logger.info(f"[AGENT_OUTPUT_INFO] {part.text}")
                            call_transcript_logger.info(f"[AGENT_OUTPUT] user_id={user_id} session_id={session_id}: {part.text}")

                await websocket.send_text(event_json)
        except (GeneratorExit, ValueError) as gen_err: # Suppress OpenTelemetry detach warnings (#BUG-34)
            logger.debug(f"GeneratorExit caught in downstream_task: {gen_err}")
        except Exception as live_err:
            err_str = str(live_err)
            if "1011" in err_str or "unavailable" in err_str.lower(): # Gemini Live API 1011 recovery (#BUG-32)
                logger.warning(
                    f"[LIVE_API_RECOVERY] Gemini Live API 1011 service unavailable encountered for user_id={user_id}, "
                    f"session_id={session_id}: {live_err}. Notifying client for seamless reconnect."
                )
                try:
                    await websocket.send_text(json.dumps({
                        "type": "service_unavailable",
                        "message": "Gemini Live API connection interrupted (1011). Please retry."
                    }))
                except Exception:
                    pass
            else:
                logger.error(f"Error in runner.run_live(): {live_err}", exc_info=True)
        logger.debug("run_live() generator completed")

    # Run both tasks concurrently
    # Exceptions from either task will propagate and cancel the other task
    try:
        logger.debug(
            "Starting asyncio.gather for upstream and downstream tasks"
        )
        await asyncio.gather(upstream_task(), downstream_task())
        logger.debug("asyncio.gather completed normally")
    except WebSocketDisconnect:
        logger.debug("Client disconnected normally")
    except Exception as e:
        logger.error(f"Unexpected error in streaming tasks: {e}", exc_info=True)
    finally:
        # ========================================
        # Phase 4: Session Termination
        # ========================================

        # Always close the queue, even if exceptions occurred
        logger.debug("Closing live_request_queue")
        live_request_queue.close()
