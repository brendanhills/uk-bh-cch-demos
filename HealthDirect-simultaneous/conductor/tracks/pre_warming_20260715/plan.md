# Implementation Plan - WebSocket Pre-Warming & Model Preloading (`pre_warming_20260715`)

This plan details the design and testing phases required to implement stateful WebSocket preloading and model prewarming.

## Phase 1: Configuration, CLI Override, and Sandbox Verification (TDD)
- [ ] Task: Pre-warming Sandbox Verification Tool
    - [ ] Create `utils/test_prewarming_sandbox.py` to allow isolated sandbox testing of the sparse digital silence keep-alive loop and latency measurement.
    - [ ] Run the sandbox script and verify that sparse silence keep-alives hold the channel hot for 15 seconds without closing and respond to voice swaps without triggering VAD regressions.
- [ ] Task: Add Config Default & CLI Switch
    - [ ] Add `"enable_prewarming": true` to `demo/interpreter_config.json`.
    - [ ] Implement CLI parser flag `--no-prewarm` inside `demo/web_server.py`.
- [ ] Task: Write Failing Tests for Preloading Logic (Red Phase)
    - [ ] Create `tests/test_prewarming_config.py` verifying that the `--no-prewarm` flag and `"enable_prewarming"` configuration values are parsed and respect precedence.
    - [ ] Write tests to verify that pre-warmed channels are successfully established and held in a hot, standby state.
- [ ] Task: Implement Process-level Prewarming and Handshake Caching (Green Phase)
    - [ ] Update `demo/web_server.py` to pre-initialize the Live Session connectors upon client connect if `enable_prewarming` is active.
    - [ ] Run the new unit tests and confirm all pass green.
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Sparse PCM Keep-Alive & Hot Standby Stream (TDD)
- [ ] Task: Write Failing Tests for Keep-Alive Pings (Red Phase)
    - [ ] Create integration tests inside `tests/test_prewarming_pings.py` to assert that keep-alive silence packets are streamed every 2.5 seconds when the connection is idle.
    - [ ] Assert that incoming microphone stream instantly swaps over and preempts the sparse pings without connection restarts.
- [ ] Task: Implement Sparse Silence Keep-Alive Loop (Green Phase)
    - [ ] Integrate an asynchronous background runner inside both Gemini connection handler loops to write periodic silence chunks (`b'\x00'`) when the input queue is empty.
    - [ ] Implement instant mic-to-warm-socket hot swapping.
    - [ ] Verify that all test cases compile and pass with 100% success.
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Presentation UI Integration and Status Bubbles
- [ ] Task: Write Failing Tests for WebSocket State Broadcast (Red Phase)
    - [ ] Write frontend state assertion tests verifying that connection state transitions (disconnected, connecting, hot) are pushed to the UI.
- [ ] Task: Implement Stateful HTML/JS UI Indicators (Green Phase)
    - [ ] Embed the colored connection state bubble in the HTML layout.
    - [ ] Wire up real-time websocket state-change event broadcasts from the backend server to the single-tab Presentation UI.
    - [ ] Confirm the entire test suite passes perfectly.
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
