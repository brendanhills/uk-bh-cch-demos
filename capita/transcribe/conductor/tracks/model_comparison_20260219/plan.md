# Implementation Plan: Model Comparison Framework

## Phase 1: Core Comparison Engine
Implement the logic to handle multiple transcription services from a single audio source.

- [x] Task: Create `ComparisonManager` to coordinate multiple `TranscriptionService` instances. f69a391
    - [x] Write unit tests for `ComparisonManager` initialization and stream handling. f69a391
    - [x] Update `TranscriptionService` to support dynamic API endpoint selection (e.g., `us-speech` for Chirp). f69a391
    - [x] Implement `ComparisonManager` to distribute audio chunks to multiple services. f69a391
- [x] Task: Update `simulate_audio.py` to support multi-consumer streaming. f69a391
    - [x] Write tests for multi-consumer audio streaming. f69a391
    - [x] Modify `simulate_audio.py` to accept multiple callback listeners. f69a391 (Note: Distribution is handled by `ComparisonManager` via queues)
- [x] Task: Conductor - User Manual Verification 'Phase 1: Core Comparison Engine' (Protocol in workflow.md)

## Phase 2: Multi-Model CLI & UI
Create the entry point and the side-by-side terminal rendering.

- [x] Task: Implement `ComparisonUI` for side-by-side terminal output. f69a391
    - [x] Write tests for columnar rendering of multiple model outputs. f69a391
    - [x] Implement side-by-side rendering logic in `transcribe_common.py`. f69a391
- [x] Task: Create `compare_models.py` CLI script. f69a391
    - [x] Write integration tests for the CLI script. f69a391
    - [x] Implement CLI argument parsing for multiple recognizers/models. f69a391
- [x] Task: Conductor - User Manual Verification 'Phase 2: Multi-Model CLI & UI' (Protocol in workflow.md)

## Phase 3: Validation & Refinement
Ensure robustness and documentation.

- [ ] Task: Add performance logging for latency comparison between models.
    - [ ] Write tests for latency tracking.
    - [ ] Implement simple timing metrics in the `ComparisonManager`.
- [ ] Task: Update documentation and README for the new feature.
    - [ ] Add usage examples to `README.md`.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Validation & Refinement' (Protocol in workflow.md)
