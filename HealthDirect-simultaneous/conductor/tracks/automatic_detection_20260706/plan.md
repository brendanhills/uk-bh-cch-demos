# Implementation Plan: Automatic Language & Gender Detection (`automatic_detection_20260706`)

This plan details the steps to build a real-time language and gender classifier, and integrate it into the dual-stream backend.

---

## Phase 1: Classifier Development & Unit Testing
- [ ] Task: Create TDD unit tests for audio detection in `tests/test_detection.py`
- [ ] Task: Implement `detect_language_and_gender(audio_chunk: bytes) -> tuple[str, str]`
    - Analyze frequency spectrum, pitch, and standard audio properties, or perform a fast Gemini metadata check.
- [ ] Task: Verify Phase 1 unit tests pass cleanly.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Classifier Development' (Protocol in workflow.md)

## Phase 2: Backend Handshake & Dynamic Routing
- [ ] Task: Implement WebSocket "Discovery Mode" handshake
    - Allow WebSocket to start without a predefined preset name.
- [ ] Task: Integrate Classifier into `web_server.py` startup flow
    - Buffer the first 3-5 seconds of incoming patient audio.
    - Run detection and resolve language and gender.
- [ ] Task: Dynamically spawn LiveConnect sessions
    - Replace hardcoded PRESET lookups with resolved configurations.
- [ ] Task: Verify Phase 2 with automated E2E tests.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Dynamic Routing' (Protocol in workflow.md)

## Phase 3: Frontend Integration & Fallbacks
- [ ] Task: Update Frontend dropdown with "Auto-Detect Language" option
- [ ] Task: Implement backend fail-safe defaults and detailed logging
- [ ] Task: Full manual verification and regression testing.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Integration & Fallbacks' (Protocol in workflow.md)
