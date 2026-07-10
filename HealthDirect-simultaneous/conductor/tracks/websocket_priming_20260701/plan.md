# Implementation Plan: Australian Medical Glossary WebSocket Priming & System Instructions (Track: `websocket_priming_20260701`)

This plan covers the implementation of dynamic session priming and custom system instructions for Gemini Live Translate sessions inside `web_server.py`, ensuring accurate, localized Australian medical translations.

## Phase 1: Dynamic Glossary Loader & Formatter

- [x] **Task: Phase 1 Setup and TDD Framework**
    - [x] Create a dedicated unit test suite for glossary loading and formatting.
- [x] **Task: Implement Glossary Loader & Formatter**
    - [x] Write failing test for loading terms by language from `dictionary/glossary.json`.
    - [x] Implement robust parsing of `dictionary/glossary.json` with fallback handling if the file is missing/malformed.
    - [x] Format the terms cleanly as key-value pairs (e.g., "Term (English) -> Translation (Target Language): Definition") to be easily appended to system instructions.
    - [x] **Regression Check:** Run existing highlighting tests and verify zero regressions with the frontend `/api/glossary` endpoint and the user's recent frontend highlighting implementation.
    - [x] Verify tests pass and check coverage (>80%).
- [x] **Task: Conductor - User Manual Verification 'Phase 1: Glossary Loader' (Protocol in workflow.md)**

## Phase 2: System Instructions Prompt Assembly

- [x] **Task: Phase 2 Setup and TDD Prompt Tests**
    - [x] Create tests to verify clinical persona prompt assembly and glossary integration.
- [x] **Task: Implement Persona and Glossary Assembly**
    - [x] Write failing test verifying the full system instruction string is constructed with the clinical persona, Australian spelling preferences, and the formatted language-specific glossary terms.
    - [x] Implement the system instruction prompt builder in `web_server.py`.
    - [x] Verify tests pass and check coverage.
- [x] **Task: Conductor - User Manual Verification 'Phase 2: System Instructions Assembly' (Protocol in workflow.md)**

## Phase 3: WebSocket Connection Priming

- [x] **Task: Phase 3 Setup and Connection Config Tests**
    - [x] Create tests to verify `LiveConnectConfig` is correctly injected during WebSocket startup.
- [x] **Task: Inject System Instructions into Live Connect Handshake**
    - [x] Write failing test verifying that `system_instruction` is included in the WebSocket's initial config when a patient/nurse session initializes.
    - [x] Integrate the prompt assembler into `web_server.py` connection handlers.
    - [x] Verify all automated tests pass seamlessly.
- [x] **Task: Conductor - User Manual Verification 'Phase 3: Connection Priming' (Protocol in workflow.md)**

## Phase 4: Dynamic Web UI Glossary Reload Button

- [x] **Task: Web UI Reload Button Interface**
    - [x] Add reload button to `web/index.html` within a neat title alignment container.
- [x] **Task: Premium Styling and Transitions**
    - [x] Style the button in `web/style.css` with transparent glassmorphism, active hover scale-downs, and a custom `@keyframes spin-reload` rotation transition.
- [x] **Task: Click Event Wireup and Feedback**
    - [x] Implement `reloadGlossaryBtn` event listeners in `web/main.js` that toggle active `.spinning` classes and dynamically request `/api/glossary`.

