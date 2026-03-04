# Implementation Plan: Codebase Consolidation and Refinement

Consolidate shared logic and simplify the architecture across the `core/` package.

## Phase 1: Shared Logic and Data Models
Unify duplicated utility logic and improve the standard data schema.

- [x] Task: Extract `TranscriptionEvent.estimate_word_timings()` 592c27b
    - Move logic from `engine.py` and `chirp3_provider.py` into a single method on the model.
- [x] Task: Extract `TranscriptionEvent.split_on_gaps(threshold)` 592c27b
    - Move duplicated logic from `engine.py` and `workers.py` into the model.
- [x] Task: Create `tests/test_models.py` 592c27b
    - Add unit tests for the new `estimate_word_timings` and `split_on_gaps` methods.
- [x] Task: Update `to_dict()` 592c27b
    - Include `metadata` in the dictionary output for better downstream analysis.
- [~] Task: Conductor - User Manual Verification 'Phase 1: Model Refinement'

## Phase 2: Provider Consolidation
Simplify the V2 API path.

- [x] Task: Refactor `V2Provider` to accept config profiles. 7de3bb7
    - Allow Chirp-specific settings (location routing) to be passed in.
- [x] Task: Language Simplification c370180
    - Hardcode/Default all providers to `en-US`. Remove "auto" detection and redundant language code logic to keep the demo clean.
- [x] Task: Consolidate `Chirp3Provider` into `V2Provider`. c370180
    - Remove the redundant class if possible, or reduce it to a simple factory function.
- [x] Task: Update `tests/test_chirp3_provider.py` 7de3bb7
    - Ensure existing tests pass against the refactored unified provider.
- [~] Task: Conductor - User Manual Verification 'Phase 2: Provider Refactor'

## Phase 3: Technical Debt and Cleanup
- [~] Task: Centralize `.env` loading.
- [~] Task: Create `tests/test_refactoring_integration.py`
    - Add a high-level integration test that runs a simulated stream through the new unified pipeline.
- [~] Task: Final Regression Testing across all Demos.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Validation'
