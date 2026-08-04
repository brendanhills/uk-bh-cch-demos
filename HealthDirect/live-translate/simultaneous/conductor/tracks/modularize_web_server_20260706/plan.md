# Implementation Plan: Web Server Modularization

This plan outlines the step-by-step decoupling of `web_server.py` into a modular `backend/` Python package.

## Phase 1: Package Scaffolding & Audio Decoupling
Extract audio loading and voice activity detection utilities into `backend/audio.py`.

- [ ] Task: Scaffolding and Audio Extraction
    - [ ] Create `backend/` package with `backend/__init__.py`.
    - [ ] Create `backend/audio.py` and implement `load_and_split_channels` and `has_speech`.
    - [ ] Write unit tests verifying identical output of audio utilities under `tests/test_backend_audio.py`.
    - [ ] Ensure test coverage targets >80% for new code.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Package Scaffolding & Audio Decoupling' (Protocol in workflow.md)

## Phase 2: Glossary & Prompt Decoupling
Extract custom clinical dictionary loading, translation direction filtering, and system instructions generation into `backend/glossary.py`.

- [ ] Task: Glossary and Prompt Extraction
    - [ ] Create `backend/glossary.py`.
    - [ ] Extract and implement `load_and_format_glossary` and `assemble_system_instructions`.
    - [ ] Write unit tests verifying identical output of glossary and instruction utilities under `tests/test_backend_glossary.py`.
    - [ ] Ensure test coverage targets >80% for new code.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Glossary & Prompt Decoupling' (Protocol in workflow.md)

## Phase 3: Stateful Session Decoupling
Extract the dynamic real-time bidirectional streaming session engine from `web_server.py` into a stateful, decoupled `BilingualInterpreterSession` class.

- [ ] Task: Stateful Session Extraction
    - [ ] Create `backend/session.py` and define `BilingualInterpreterSession`.
    - [ ] Implement parallel Gemini Live WebSocket connection setup in `BilingualInterpreterSession.connect`.
    - [ ] Implement state management (takeover detection, silence streaming, dynamic hold/resume, and manual pacing) inside the session class.
    - [ ] Use callback functions or async queues to forward original/translated audio, transcript, and event updates to callers, eliminating any dependency on FastAPI.
    - [ ] Extract cleanup and cancellation logic into `BilingualInterpreterSession.close`.
    - [ ] Write unit tests verifying session state machine transitions under `tests/test_backend_session.py`.
    - [ ] Ensure test coverage targets >80% for new code.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Stateful Session Decoupling' (Protocol in workflow.md)

## Phase 4: Lean Web Server Integration & End-to-End Verification
Integrate the `backend` package back into `web_server.py`, slim down the server, and verify full end-to-end functionality.

- [ ] Task: Web Server Integration
    - [ ] Refactor `web_server.py` to use `backend/audio.py`, `backend/glossary.py`, and `backend/session.py`.
    - [ ] Slim down the FastAPI server to only initialize the application, mount static files, serve the `/api/glossary` endpoint, and route `/ws`.
    - [ ] In `/ws`, instantiate `BilingualInterpreterSession` and bind callbacks to push events back to the FastAPI client.
    - [ ] Adapt existing tests (like `tests/test_pacing_state_machine.py`) to run successfully against the refactored server.
    - [ ] Run full automated test suite and manual end-to-end checks to ensure flawless parity with the original server.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Lean Web Server Integration & End-to-End Verification' (Protocol in workflow.md)
