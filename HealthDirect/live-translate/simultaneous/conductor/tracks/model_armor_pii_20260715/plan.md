# Implementation Plan - ModelArmor PII & Safety Guardrails (`model_armor_pii_20260715`)

This plan details the design, configuration, and integration phases required to introduce ModelArmor safety filters and interactive Web UI selectors.

## Phase 1: Configuration Schema and UI Toggles
- [ ] Task: Integrate Config Variables
    - [ ] Add `"enable_model_armor": true` and `"model_armor_categories": ["pii", "profanity"]` defaults to `demo/interpreter_config.json`.
    - [ ] Implement UI checkbox controls in `demo/web/nurse.html` sidebar to allow clinicians to toggle PII, Profanity, and Financial filters.
    - [ ] Add state syncing handlers in `simultaneous_client.js` to propagate safety toggles through `/ws/nurse` and broadcast to patient.
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Create Red-Phase Unit Tests (TDD)
- [ ] Task: Write Failing Safety Tests
    - [ ] Create `tests/test_model_armor_safety.py` asserting that PII (e.g. John Doe, 12 Smith St) is redacted inline when PII filter is enabled.
    - [ ] Assert that abusive strings are censored inline when Profanity filter is enabled.
    - [ ] Assert that mock fallbacks are used when the standard cloud client is unauthorized.
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Implement ModelArmor Engine & Filters (Green Phase)
- [ ] Task: Implement ModelArmor Engine
    - [ ] Create a helper class `ModelArmorEngine` inside `utils/` or `core/` to connect to Google Cloud ModelArmor.
    - [ ] Implement the local regex/dictionary-based fallback logic to support offline/local execution.
    - [ ] Inject the filter check into the web server stream loops before forwarding patient and clinician text.
    - [ ] Confirm all safety unit tests pass green.
- [ ] Task: Verify Clean Rendering
    - [ ] Assert that redacted strings (e.g., `[REDACTED_NAME]`) render cleanly inside speech bubbles in the frontend without breaking any glossary highlight tooltips.
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
