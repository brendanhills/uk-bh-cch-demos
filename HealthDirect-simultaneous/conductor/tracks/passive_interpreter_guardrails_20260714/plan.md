# Implementation Plan: Passive Interpreter Guardrails & Translation Auditing

This track outlines the specific tasks to implement real-time safety guardrails and translation auditing for Gemini 3.1 Flash Live.

## Proposed Tasks

### 1. Develop Live Unit & Integration Tests
- [ ] Task: Create `tests/test_passive_guardrails.py` containing:
  - Unit tests to verify character-set leakage detection for Arabic and other native script inputs.
  - Regex keyword auditing tests for conversational and medical disclaimer markers.
  - Live mock/integration tests verifying that a conversational detour by the model triggers a compliance alert.

### 2. Implement Backend Real-Time Guardrail Logic
- [ ] Task: In `demo/web_server.py`, add helper functions:
  - `detect_language_leakage(text, expected_lang="en") -> bool`: Checks for unexpected non-English characters (e.g. Arabic script `\u0600-\u06FF`) in English outputs.
  - `audit_conversational_markers(text) -> list[str]`: Evaluates regular expressions for forbidden comforting, agentic, and medical disclaimer statements.
- [ ] Task: Integrate these checks into the WebSocket message handling loop in `demo/web_server.py`. When a violation is detected, send a compliance warning WebSocket message (`type: "compliance_warning"`) containing the details.

### 3. Add Asynchronous Semantic Audit Engine
- [ ] Task: Implement a background task in `demo/web_server.py` that asynchronously invokes `client.models.generate_content` (or `generate_content_stream`) using a fast model to verify semantic alignment (original statement vs. translated output).
- [ ] Task: Broadcast any detected semantic alignment failures to the clinician/nurse UI as a warning.

### 4. Enhance Web Client UI to Display Safety Alerts
- [ ] Task: In `demo/web/main.js` (and simultaneous counterparts), listen for `"compliance_warning"` events.
- [ ] Task: Style and render premium, high-visibility visual warnings (e.g., a subtle yellow outline around speech bubbles or warning icons) to notify the clinician when the interpreter is talking directly to the patient or adding disclaimers.

## Verification & Testing
- Run pytest suite:
  ```bash
  uv run pytest tests/test_passive_guardrails.py
  ```
- Run the full suite to verify zero regressions.
