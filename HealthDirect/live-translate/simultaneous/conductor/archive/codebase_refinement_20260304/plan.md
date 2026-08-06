# Implementation Plan: Codebase Consolidation and Refinement

Consolidate shared logic and simplify the architecture across the `core/` package.

## Phase 1: Shared Logic and Data Models
Unify duplicated utility logic and improve the standard data schema.

- [x] Task: Extract `TranscriptionEvent.estimate_word_timings()` 592c27b
- [x] Task: Extract `TranscriptionEvent.split_on_gaps(threshold)` 592c27b
- [x] Task: Create `tests/test_models.py` 592c27b
- [x] Task: Update `to_dict()` 592c27b
- [x] Task: Conductor - User Manual Verification 'Phase 1: Model Refinement'

## Phase 2: Provider Consolidation
Simplify the V2 API path.

- [x] Task: Refactor `V2Provider` to accept config profiles. 7de3bb7
- [x] Task: Language Simplification c370180
- [x] Task: Consolidate `Chirp3Provider` into `V2Provider`. c370180
- [x] Task: Update `tests/test_chirp3_provider.py` 7de3bb7
- [x] Task: Conductor - User Manual Verification 'Phase 2: Provider Refactor'

## Phase 3: Technical Debt and Cleanup
- [x] Task: Centralize `.env` loading. d072eb6
- [x] Task: Create `tests/test_refactoring_integration.py` afaeaf2
- [x] Task: Final Regression Testing across all Demos. f7e7ecf
- [x] Task: Conductor - User Manual Verification 'Phase 3: Final Validation' f7e7ecf

## Phase 4: Attribution & Timing Fidelity (The Fix)
Ensure correct sequence and attribution for high-latency models.

- [x] Task: Leverage VAD metadata for pinning. f7e7ecf
- [x] Task: Default to Single-Stream V2 for better stability. f7e7ecf
- [x] Task: Adaptive Stability Window (5.0s for Chirp). f7e7ecf

## Phase 5: The "Live" Feel (UI Optimization) [checkpoint: EDU_FINAL]
- [x] Task: Enhanced Interim Display f7e7ecf
    - Ensure Chirp-3 draft results are rendered immediately to provide a 'live' feeling despite slow finalization.
- [x] Task: Fix UI repetition fa22920
    - Resolved race condition between heartbeats and interim clearing.
- [x] Task: Conductor - User Manual Verification 'Final Refinement' fa22920

