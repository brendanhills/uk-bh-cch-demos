# Implementation Plan: Australian Medical Glossary WebSocket Priming & System Instructions (Track: `websocket_priming_20260701`)

This plan covers the implementation of dynamic session priming and custom system instructions for Gemini Live Translate sessions inside `web_server.py`, ensuring accurate, localized Australian medical translations.

## Phase 1: Dynamic Glossary Loader & Formatter

- [ ] **Task: Phase 1 Setup and TDD Framework**
    - [ ] Create a dedicated unit test suite for glossary loading and formatting.
- [ ] **Task: Implement Glossary Loader & Formatter**
    - [ ] Write failing test for loading terms by language from `dictionary/glossary.json`.
    - [ ] Implement robust parsing of `dictionary/glossary.json` with fallback handling if the file is missing/malformed.
    - [ ] Format the terms cleanly as key-value pairs (e.g., "Term (English) -> Translation (Target Language): Definition") to be easily appended to system instructions.
    - [ ] **Regression Check:** Run existing highlighting tests and verify zero regressions with the frontend `/api/glossary` endpoint and the user's recent frontend highlighting implementation.
    - [ ] Verify tests pass and check coverage (>80%).
- [ ] **Task: Conductor - User Manual Verification 'Phase 1: Glossary Loader' (Protocol in workflow.md)**

## Phase 2: System Instructions Prompt Assembly

- [ ] **Task: Phase 2 Setup and TDD Prompt Tests**
    - [ ] Create tests to verify clinical persona prompt assembly and glossary integration.
- [ ] **Task: Implement Persona and Glossary Assembly**
    - [ ] Write failing test verifying the full system instruction string is constructed with the clinical persona, Australian spelling preferences, and the formatted language-specific glossary terms.
    - [ ] Implement the system instruction prompt builder in `web_server.py`.
    - [ ] Verify tests pass and check coverage.
- [ ] **Task: Conductor - User Manual Verification 'Phase 2: System Instructions Assembly' (Protocol in workflow.md)**

## Phase 3: WebSocket Connection Priming

- [ ] **Task: Phase 3 Setup and Connection Config Tests**
    - [ ] Create tests to verify `LiveConnectConfig` is correctly injected during WebSocket startup.
- [ ] **Task: Inject System Instructions into Live Connect Handshake**
    - [ ] Write failing test verifying that `system_instruction` is included in the WebSocket's initial config when a patient/nurse session initializes.
    - [ ] Integrate the prompt assembler into `web_server.py` connection handlers.
    - [ ] Verify all automated tests pass seamlessly.
- [ ] **Task: Conductor - User Manual Verification 'Phase 3: Connection Priming' (Protocol in workflow.md)**
