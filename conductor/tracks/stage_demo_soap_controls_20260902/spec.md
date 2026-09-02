# Track Specification: Stage Demo Call Controls & Automated SOAP Note Modal

## Overview

This track introduces dedicated stage demo call lifecycle controls (**"📞 Start Call"** and **"📞 End Call"**) and automated post-call clinical SOAP note generation with a pop-up modal interface (`#soapModal`). 

During live stage presentations, presenters need seamless controls to initiate calls without manually greeting the model, pause audio capture to speak to the audience without triggering agent responses (using existing **"🛑 Stop Mic"** functionality), and end calls cleanly while displaying an automated clinical SOAP note export.

---

## Functional Requirements

### 1. Stage Demo Call Lifecycle UI Toolbar
- **`Start Call` Button (`#startCallButton`) [NEW]**:
  - Connects/initializes the Live API BIDI WebSocket session (if disconnected).
  - Automatically sends a synthetic `"Hello"` text payload to ADK `live_request_queue` to trigger Jennie's warm hospital opening greeting (*"Hello, thank you for calling Cymbal Children's Hospital..."*).
  - Activates audio microphone streaming (`startAudio()`).
- **`Pause Mic` / `Resume Mic` Button (`#stopAudioButton`) [EXISTING FUNCTIONALITY]**:
  - Leverages existing `stopAudioButton` / `startAudioButton` handlers to pause/resume microphone audio worklet streaming without closing the WebSocket connection or ending the session.
  - Allows the presenter to address stage audiences mid-demo without the agent responding.
- **`End Call` Button (`#endCallButton`) [NEW]**:
  - Stops audio input and playback worklets cleanly.
  - Sends an explicit `{ "type": "end_call" }` message over the WebSocket.
  - Closes the WebSocket session.
  - Triggers the automated post-call SOAP note modal.

### 2. Backend Asynchronous Post-Call SOAP Generation
- **WebSocket Protocol**:
  - `main.py` handles `{ "type": "end_call" }` in `upstream_task()`.
  - Spawns a non-blocking background task `_generate_post_call_soap_note(user_id, session_id)`.
- **SOAP Generator Sub-Agent Execution**:
  - Extracts turn history (`session.events`) from `InMemorySessionService`.
  - Invokes `soap_generator` (`gemini-2.5-flash`) with `SOAP_GENERATOR_INSTRUCTION` to synthesize Subjective, Objective, Assessment, and Plan notes.
  - Saves formatted Markdown note to `app/logs/soap_notes/{session_id}.md`.
- **REST Endpoint**:
  - `GET /api/soap/{session_id}`: Returns JSON `{ "status": "ready", "soap_note": "<markdown>" }` or loading status.

### 3. Frontend Clinical SOAP Note Modal (`#soapModal`) [NEW]
- Displays a clean, high-contrast modal overlay when `End Call` is clicked.
- Renders formatted Markdown clinical SOAP notes returned by `GET /api/soap/{session_id}`.
- Includes a copy/download button and close button.

---

## Non-Functional Requirements

- **Zero Audio Stream Latency Impact**: Post-call SOAP note generation MUST execute asynchronously without blocking WebSocket teardown or live audio playback.
- **Graceful Error Handling**: If SOAP generation fails or times out, the modal gracefully displays session transcript details without breaking UI functionality.

---

## Acceptance Criteria

1. Clicking **"Start Call"** connects WebSocket, turns on mic, and immediately triggers Jennie's opening hospital script without needing to say "Hi".
2. Existing **"Stop Mic"** functionality successfully pauses audio, allowing stage explanation while keeping session state alive.
3. Clicking **"End Call"** closes connection and immediately launches the **Clinical SOAP Note Modal**.
4. The generated SOAP note accurately captures Subjective, Objective, Assessment, and Plan sections from `session.events`.
5. Existing unit and integration tests (`pytest tests/`) pass with zero regressions.

---

## Out of Scope

- Direct EMR API synchronization (mocked via local file storage `app/logs/soap_notes/`).
- Multi-user concurrent SOAP note editor state.
