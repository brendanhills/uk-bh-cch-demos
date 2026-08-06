# Implementation Plan: Server Hold-Loop Silence Frame Pacing

## Phase 1: Configuration & Turn Detection Regression Baseline
- [ ] Task: Add Hold Pacing Settings & Regression Unit Tests
  - [ ] Write regression unit tests in `tests/test_hold_pacing.py` validating that existing turn detection thresholds (`ceased_audio_threshold`, `startup_audio_threshold`) function identically
  - [ ] Add `"hold_silence_interval_ms": 100` and `"enable_hold_pacing": true` under pacing section in `demo/interpreter_config.json`
  - [ ] Run tests to ensure green baseline status
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Server Hold-Loop Pacing Implementation
- [ ] Task: Implement Sparse Keep-Alive Pacing in Server Hold Loops
  - [ ] Write unit tests in `tests/test_hold_pacing.py` verifying sparse keep-alive frame intervals
  - [ ] Update hold wait loops in `demo/web_server.py` to read `hold_silence_interval_ms` and pace keep-alive frames
  - [ ] Add config fallback toggle check (`enable_hold_pacing`)
  - [ ] Run tests to ensure green status
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: End-to-End Verification & Validation
- [ ] Task: End-to-End Turn Taking & Stability Test
  - [ ] Write end-to-end integration test verifying complete turn-taking sequence with hold pacing enabled
  - [ ] Run full test suite and verify >80% coverage
  - [ ] Perform manual session run and verify zero impact on turn responsiveness or audio playback
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
