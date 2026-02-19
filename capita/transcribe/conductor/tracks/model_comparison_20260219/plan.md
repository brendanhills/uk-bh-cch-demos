# Implementation Plan: Model Comparison Framework

## Phase 1: Core Comparison Engine
Implement the logic to handle multiple transcription services from a single audio source.

- [ ] Task: Create `ComparisonManager` to coordinate multiple `TranscriptionService` instances.
    - [ ] Write unit tests for `ComparisonManager` initialization and stream handling.
    - [ ] Implement `ComparisonManager` to distribute audio chunks to multiple services.
- [ ] Task: Update `simulate_audio.py` to support multi-consumer streaming.
    - [ ] Write tests for multi-consumer audio streaming.
    - [ ] Modify `simulate_audio.py` to accept multiple callback listeners.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Core Comparison Engine' (Protocol in workflow.md)

## Phase 2: Multi-Model CLI & UI
Create the entry point and the side-by-side terminal rendering.

- [ ] Task: Implement `ComparisonUI` for side-by-side terminal output.
    - [ ] Write tests for columnar rendering of multiple model outputs.
    - [ ] Implement side-by-side rendering logic in `transcribe_common.py`.
- [ ] Task: Create `compare_models.py` CLI script.
    - [ ] Write integration tests for the CLI script.
    - [ ] Implement CLI argument parsing for multiple recognizers/models.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Multi-Model CLI & UI' (Protocol in workflow.md)

## Phase 3: Validation & Refinement
Ensure robustness and documentation.

- [ ] Task: Add performance logging for latency comparison between models.
    - [ ] Write tests for latency tracking.
    - [ ] Implement simple timing metrics in the `ComparisonManager`.
- [ ] Task: Update documentation and README for the new feature.
    - [ ] Add usage examples to `README.md`.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Validation & Refinement' (Protocol in workflow.md)
