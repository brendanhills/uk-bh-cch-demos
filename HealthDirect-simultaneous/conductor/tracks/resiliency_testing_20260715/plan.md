# Implementation Plan - Passive Interpreter Resiliency & End-to-End Testing (`resiliency_testing_20260715`)

This plan details the design and testing phases required to implement stateful connection drop resiliency, immediate error bubbling, and future E2E dependency scaffolding.

## Phase 1: Chaos Test Writing (TDD Red Phase)
- [ ] Task: Create Failing Chaos Test Case
    - [ ] Create `tests/test_chaos_recovery.py` simulating a WebSocket abnormal disconnect.
    - [ ] Mock the Live Client connection context so that `send` or `receive` raises a connection drop error mid-stream.
    - [ ] Assert that the error propagates as an error type event to clinician and patient clients.
    - [ ] Verify the test fails because error-catching isn't yet fully bubbling or tearing down.

## Phase 2: Implement Exception Catching & Bubbling (Green Phase)
- [ ] Task: Implement Active Catch & Bubble
    - [ ] Update `run_simultaneous_stream` and `execute_streaming_loop` to actively catch connection drops (`ConnectionResetError`, `ConnectionAbnormalClosure`, `ConnectionClosedError`).
    - [ ] Set `self.is_active = False` inside the exception handler and broadcast a clean disconnect event to both clinician and patient ws clients.
    - [ ] Run `pytest tests/test_chaos_recovery.py` and verify it passes green.
    - [ ] Run the complete 100-test suite to confirm zero regressions.
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Scaffold Future E2E Testing Dependencies
- [ ] Task: Scaffold Playwright in pyproject.toml
    - [ ] Add `playwright` and `pytest-playwright` dependencies to `pyproject.toml` using `uv`.
    - [ ] Run `uv pip compile` or sync dependencies to verify environment safety.
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
