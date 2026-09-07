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
  - Create `tests/test_soap_note_endpoint.py`
  - Write test verifying `/api/session/soap_note` returns the generated Markdown SOAP note JSON payload
  - Verify tests fail before endpoint wiring (Red Phase)

- [x] **Task 1.2: Implement background SOAP note generator & REST endpoint in main.py (Green Phase)**
  - Wire `soap_generator` sub-agent in `app/main.py`
  - Extract session events from `InMemorySessionService` (`session.events`)
  - Invoke `soap_generator` sub-agent to generate Subjective, Objective, Assessment, and Plan sections
  - Add endpoint `POST /api/session/soap_note` returning JSON `{ "status": "success", "soap_note": "<markdown>" }`
  - Verify tests pass (Green Phase)

- [x] Task: Phase 1 Verification & Checkpoint (Refer to workflow.md)

---

## Phase 2: Frontend Stage Demo Controls & Clinical SOAP Modal

- [x] **Task 2.1: Add new Export SOAP Note button, End Call button, and SOAP modal HTML markup**
  - Add call lifecycle controls in `app/static/index.html`:
    - `id="soapNoteButton"` ("📄 Export SOAP Note") in header
    - `id="endCallButton"` ("📞 End Call") in bottom toolbar
    - (Keep existing `id="stopAudioButton"` ("🛑 Stop Mic"))
  - Add modal container `#soapModal` in `app/static/index.html` for rendering Markdown clinical SOAP notes upon call completion

- [x] **Task 2.2: Implement frontend call lifecycle handlers in app.js & CSS**
  - Wire up `soapNoteButton` & `endCallButton`:
    1. Stops audio recording/playback via `stopAudio()`.
    2. Fetches and displays generated clinical SOAP note from `/api/session/soap_note` in `#soapModal`.
    3. Provides Clipboard copy and Print formatting.
  - Style stage demo buttons and modal overlay in `app/static/css/style.css`

- [x] Task: Phase 2 Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Integration Verification & Stage Dry Run

- [x] **Task 3.1: Execute automated regression suite & verify live BIDI audio stability**
  - Run `uv run pytest tests/` to confirm zero regressions (13/13 passing)
  - Verify code coverage for new handlers

- [x] Task: Phase 3 Verification & Checkpoint (Refer to workflow.md)
