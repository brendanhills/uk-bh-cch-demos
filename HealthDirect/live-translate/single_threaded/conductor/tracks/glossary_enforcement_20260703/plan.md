# Implementation Plan: Enforce Glossary in Gemini Live Translation

## Phase 1: Frontend Model Selection
- [x] Task: Add a model selector dropdown in `web/index.html` with beautiful, glassmorphic styling adjacent to Scenario controls.
- [x] Task: Register model controls in `web/main.js`, update `#model-badge` dynamically on change, and pass the selected model string in the WebSocket `"start"` payload.

## Phase 2: Backend Parameterization & Configuration
- [x] Task: Extract `"model"` from WebSocket connection start payload in `web_server.py`.
- [x] Task: Construct `LiveConnectConfig` conditionally:
  - For `gemini-3.1-flash-live-preview`, omit `translation_config` and inject the strict Passive Interpreter Constraint.
  - For `gemini-3.5-live-translate-preview`, include `translation_config` as implemented.
- [x] Task: Implement channel-directed glossaries formatting (Patient -> Nurse as `Native -> English`, Nurse -> Patient as `English -> Native`) to align with model expectations.

## Phase 3: Automated Challenge Testing (TDD & Validation)
- [x] Task: Implement robust integration tests in `tests/test_live_glossary_enforcement.py` for:
  - Scenario 1: Standard Glossary Translation ("Fieber" -> "Extreme Fire Flame").
  - Scenario 2: Conversational Bait Challenge ("Hallo, wie geht es dir?").
  - Scenario 3: Medical Disclaimer Trigger ("Ich glaube, ich sterbe an einem Herzinfarkt.").
- [x] Task: Verify all challenge tests pass successfully on the real Live API.

## Phase 4: E2E Verification & Review
- [x] Task: Conduct end-to-end user manual verification of both model executions in different browser windows sequentially.
- [x] Task: Review code, check full pytest regression suite, and merge/commit changes.
