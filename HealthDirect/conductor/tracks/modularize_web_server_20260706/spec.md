# Specification: Web Server Modularization (`modularize_web_server_20260706`)

## Overview
The current `web_server.py` is a monolithic file of approximately 950 lines that mixes audio manipulation, clinical glossary formatting, Gemini Live instruction assembly, real-time bidirectional audio orchestration, and FastAPI endpoint/route management. 

This track aims to refactor and modularize `web_server.py` by extracting decoupled components into a structured `backend/` Python package. This makes the underlying services reusable for standalone CLI scripts, tests, or alternative interfaces.

## Proposed Component Architecture

### 1. `backend/audio.py` (Audio Utilities)
- Responsible for audio file processing and speech detection.
- Functions to extract:
  - `load_and_split_channels(file_path, target_sample_rate)`: Loads stereo wavs, forces 16kHz 16-bit PCM, splits stereo channels.
  - `has_speech(chunk, threshold)`: Determines speech presence via PCM power envelope.
- Dependencies: `pydub`, standard libraries. **Strictly decoupled from FastAPI/GenAI SDK.**

### 2. `backend/glossary.py` (Glossary & Prompt Engine)
- Responsible for loading clinical glossaries and building system instructions.
- Functions to extract:
  - `load_and_format_glossary(target_language, direction)`: Resolves glossary file paths, filters by language, formats into key-value pairs.
  - `assemble_system_instructions(direction, target_language, glossary_str, is_flash_live)`: Injects clinical persona, Australian spelling rules, passive interpreter constraints, and active glossaries.
- Dependencies: Standard libraries. **Strictly decoupled from FastAPI/GenAI SDK.**

### 3. `backend/session.py` (Bilingual Interpreter Session Manager)
- Stateful session class (e.g., `BilingualInterpreterSession`) managing the core life cycle of a live translation session.
- Handles:
  - Parallel Gemini Live WebSockets (`aio.live.connect`).
  - Active audio pacing state machine (cooldowns, takeover detection, silence-streaming, manual resume, timeouts, and natural turn-taking transitions).
  - Background task scheduling and lifecycle cleanup.
- Communicates with callers (like the FastAPI WebSocket) via clear callbacks/async events for original audio, translated audio, transcripts, and status/turn updates.
- Dependencies: `google-genai` SDK, `backend.audio`, `backend.glossary`. **Decoupled from FastAPI.**

### 4. `web_server.py` (Lean FastAPI Wrapper)
- Rebuilt as a high-level wrapper.
- Responsibilities:
  - FastAPI app initialization, serving static files (`/` mapped to `web/`).
  - HTTP endpoints (e.g. `/api/glossary` querying `backend/glossary.py`).
  - `/ws` WebSocket endpoint: Handles handshake, instantiates `BilingualInterpreterSession`, binds callbacks to push events back to the client, and forwards client actions (pause, resume, next_turn) into the session.

---

## Acceptance Criteria
1. **Component Decoupling**: `backend/audio.py` and `backend/glossary.py` can be imported and executed in isolation without importing `FastAPI` or setting up web servers.
2. **Behavioral Parity**:
   - Dual-channel real-time audio splitting operates exactly as before.
   - Pacing state machine (auto/manual modes) matches identical behavior, including takeover detection, silence streaming, and manual next-turn triggers.
   - Transcription logging to `conversation_transcript.log` and session logging to `interpreter_session.log` function identically.
3. **Compatibility**: Fully compatible with the existing frontend `web/` assets; no changes to the WebSocket protocol.
4. **No Performance Regression**: Modular design must not introduce audio latency or streaming stutter.

## Out of Scope
- Modifying frontend files (`web/index.html`, `web/main.js`, `web/style.css`).
- Changing default speech thresholds or default system prompt guidelines.
- Adding new presets or languages.
