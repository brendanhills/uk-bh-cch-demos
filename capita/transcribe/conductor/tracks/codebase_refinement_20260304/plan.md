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
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Model Refinement'

## Phase 2: Provider Consolidation
Simplify the V2 API path.

- [ ] Task: Refactor `V2Provider` to accept config profiles.
    - Allow Chirp-specific settings (location routing) to be passed in.
- [ ] Task: Language Simplification
    - Hardcode/Default all providers to `en-US`. Remove "auto" detection and redundant language code logic to keep the demo clean.
- [ ] Task: Consolidate `Chirp3Provider` into `V2Provider`.
    - Remove the redundant class if possible, or reduce it to a simple factory function.
- [ ] Task: Update `tests/test_chirp3_provider.py`
    - Ensure existing tests pass against the refactored unified provider.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Provider Refactor'

## Phase 3: Technical Debt and Cleanup
- [ ] Task: Centralize `.env` loading.
- [ ] Task: Create `tests/test_refactoring_integration.py`
    - Add a high-level integration test that runs a simulated stream through the new unified pipeline.
- [ ] Task: Final Regression Testing across all Demos.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Validation'
