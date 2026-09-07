# Implementation Plan: Stage Demo Call Controls & Automated SOAP Generation

Enhance stage demo UX with explicit **"📞 Start Call"** and **"📞 End Call"** controls, leveraging existing **"🛑 Stop Mic"** controls, and automated background clinical SOAP note modal generation in the Cymbal Children's Hospital ADK Concierge application.

## User Requirements & Review

> [!IMPORTANT]
> **Stage Demo Call Lifecycle Controls**:
> - **"📞 Start Call" [NEW]**: Connects WebSocket (if needed), enables mic, and automatically sends an initial greeting trigger so Jennie greets the audience immediately without the presenter needing to say "Hi".
> - **"🛑 Pause Mic" [EXISTING]**: Uses existing `stopAudioButton` / `startAudio()` functionality to temporarily pause mic capture so the presenter can address the stage audience without the agent responding. Keeps session active.
> - **"📞 End Call" [NEW]**: Signals call completion, closes stream, triggers background SOAP generation, and pops up the **Clinical SOAP Note Modal**.

---

## Phase 1: Backend Protocol & Asynchronous SOAP Generation

- [x] **Task 1.1: Write failing unit and integration tests for SOAP note generation (Red Phase)**
  - Create `tests/test_soap_tool.py`
  - Write test verifying tool context and model fallback
  - Write test verifying `POST /api/session/soap_note` returns the generated Markdown SOAP note JSON payload
  - Write test verifying existing mic pause ("Stop Mic") does NOT terminate session or generate SOAP prematurely
  - Verify tests fail (Red Phase)

- [x] **Task 1.2: Implement background SOAP note generator & REST endpoint in main.py (Green Phase)**
  - Add decoupled ADK tool `complete_consultation_and_export_soap` in `app/cch_agent/tools/soap_export.py`
  - Handle `{ "type": "end_call" }` in WebSocket `upstream_task()`
  - Extract session events from `session_service` (`session.events`)
  - Invoke Gemini (with `SOAP_MODEL` fallback) to generate Subjective, Objective, Assessment, and Plan sections
  - Add endpoint `POST /api/session/soap_note` returning JSON `{ "status": "success", "soap_note": "<markdown>" }`
  - Verify tests pass (Green Phase)

- [x] Task: Phase 1 Verification & Checkpoint (Refer to workflow.md)

---

## Phase 2: Frontend Stage Demo Controls & Clinical SOAP Modal

- [x] **Task 2.1: Add new Start Call, End Call buttons, and SOAP modal HTML markup**
  - Add call lifecycle buttons in `app/static/index.html`:
    - `id="startCallButton"` ("📞 Start Call") [NEW]
    - `id="endCallButton"` ("📞 End Call") [NEW]
    - (Keep existing `id="stopAudioButton"` ("🛑 Stop Mic"))
  - Add modal container `#soapModal` in `app/static/index.html` for rendering Markdown clinical SOAP notes upon call completion [NEW]

- [x] **Task 2.2: Implement frontend call lifecycle handlers in app.js & CSS**
  - Wire up `startCallButton`:
    1. Opens/resets WebSocket session if needed.
    2. Sends initial trigger `{"type": "start_call"}` with `[CALL_CONNECTED]` to prompt Jennie's opening greeting immediately.
    3. Enables audio mic input (`startAudio()`).
  - Wire up `endCallButton`:
    1. Stops audio recording/playback using existing `stopAudio()`.
    2. Sends `{ "type": "end_call" }` over WebSocket.
    3. Fetches and displays generated SOAP note from `/api/session/soap_note` in `#soapModal`.
  - Style stage demo buttons and modal overlay in `app/static/css/style.css`

- [x] Task: Phase 2 Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Integration Verification & Stage Dry Run

- [x] **Task 3.1: Execute automated regression suite & verify live BIDI audio stability**
  - Run `uv run pytest tests/` to confirm zero regressions (16/16 passed)
  - Verify code coverage for new handlers and tools

- [ ] **Task 3.2: Manual End-to-End Stage Dry Run & Browser Verification**
  - Run `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
  - Verify **📞 Start Call** triggers Jennie's immediate opening greeting
  - Verify **📞 End Call** generates and displays clinical SOAP note in modal
  - Verify Copy to Clipboard and Print buttons

- [ ] Task: Phase 3 Verification & Track Sign-off
