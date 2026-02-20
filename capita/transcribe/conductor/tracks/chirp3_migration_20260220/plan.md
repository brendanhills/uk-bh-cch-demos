# Implementation Plan: Chirp 3 Migration

Migrate the system to use Chirp 3 as the default STT model and ensure robustness against missing word-level timestamps.

## Phase 1: Configuration and Defaults
Update the project configuration to use Chirp 3 and the appropriate GCP region.

- [ ] Task: Update `core/utils.py` to set Chirp 3 as default
    - [ ] Change `--model` default to `chirp-3`
- [ ] Task: Update Regional Endpoint Logic
    - [ ] Modify `two_channel_transcribe_v2.py` and `parallel_transcribe.py` to use `us` location for all Chirp models.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Configuration' (Protocol in workflow.md)

## Phase 2: Engine Resilience
Ensure the `TranscriptionEngine` handles Chirp 3 results that may lack word-level timestamps.

- [ ] Task: Write Tests for Wordless Transcripts
    - [ ] Create a test case in `tests/test_engine.py` simulating a transcript event with an empty `words` list.
    - [ ] Verify that interleaving/splitting still functions using the fallback estimation logic.
- [ ] Task: Refine Engine Fallback Logic
    - [ ] Ensure `_interleave_and_split` in `core/engine.py` correctly populates estimated word timings if missing.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Engine Resilience' (Protocol in workflow.md)

## Phase 3: Integration and Baseline
Validate the migration across the primary demos and comparison tools.

- [ ] Task: Update `compare_models.py`
    - [ ] Update default comparison models to include Chirp 3.
- [ ] Task: End-to-End Verification
    - [ ] Run `two_channel_transcribe_v2.py` with `samples/0638.mp3` using Chirp 3.
    - [ ] Verify UI labels and chronological stability.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Integration' (Protocol in workflow.md)
