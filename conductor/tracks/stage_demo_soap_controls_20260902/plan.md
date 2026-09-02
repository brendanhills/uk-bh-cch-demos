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

- [ ] **Task 1.1: Write failing unit and integration tests for SOAP note generation (Red Phase)**
  - Create `tests/test_soap_generation.py`
  - Write test verifying `{ "type": "end_call" }` triggers `_generate_post_call_soap_note` background task
  - Write test verifying `GET /api/soap/{session_id}` returns the generated Markdown SOAP note JSON payload
  - Write test verifying existing mic pause ("Stop Mic") does NOT terminate session or generate SOAP prematurely
  - Verify tests fail (Red Phase)

- [ ] **Task 1.2: Implement background SOAP note generator & REST endpoint in main.py (Green Phase)**
  - Add `_generate_post_call_soap_note(user_id, session_id)` background task in `app/main.py`
  - Handle `{ "type": "end_call" }` in WebSocket `upstream_task()`
  - Extract session events from `InMemorySessionService` (`session.events`)
  - Invoke `soap_generator` sub-agent to generate Subjective, Objective, Assessment, and Plan sections
  - Write markdown note to `app/logs/soap_notes/{session_id}.md`
  - Add endpoint `GET /api/soap/{session_id}` returning JSON `{ "status": "ready", "soap_note": "<markdown>" }`
  - Verify tests pass (Green Phase)

- [ ] Task: Phase 1 Verification & Checkpoint (Refer to workflow.md)

---

## Phase 2: Frontend Stage Demo Controls & Clinical SOAP Modal

- [ ] **Task 2.1: Add new Start Call, End Call buttons, and SOAP modal HTML markup**
  - Add call lifecycle buttons in `app/static/index.html`:
    - `id="startCallButton"` ("📞 Start Call") [NEW]
    - `id="endCallButton"` ("📞 End Call") [NEW]
    - (Keep existing `id="stopAudioButton"` ("🛑 Stop Mic"))
  - Add modal container `#soapModal` in `app/static/index.html` for rendering Markdown clinical SOAP notes upon call completion [NEW]

- [ ] **Task 2.2: Implement frontend call lifecycle handlers in app.js & CSS**
  - Wire up `startCallButton`:
    1. Opens/resets WebSocket session if needed.
    2. Sends initial text trigger `{"type": "text", "text": "Hello"}` to initiate Jennie's opening greeting.
    3. Enables audio mic input (`startAudio()`).
  - Wire up `endCallButton`:
    1. Stops audio recording/playback using existing `stopAudio()`.
    2. Sends `{ "type": "end_call" }` over WebSocket.
    3. Closes WebSocket connection cleanly.
    4. Fetches and displays generated SOAP note from `/api/soap/{session_id}` in `#soapModal`.
  - Style stage demo buttons and modal overlay in `app/static/css/style.css`

- [ ] Task: Phase 2 Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Integration Verification & Stage Dry Run

- [ ] **Task 3.1: Execute automated regression suite & verify live BIDI audio stability**
  - Run `uv run pytest tests/` to confirm zero regressions
  - Verify code coverage >80% for new handlers

- [ ] Task: Phase 3 Verification & Checkpoint (Refer to workflow.md)
