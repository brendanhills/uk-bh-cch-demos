# Implementation Plan: Specialized Chirp-3 Module

Implement a dedicated `Chirp3Provider` module to handle the unique requirements of the Chirp-3 model, including specialized arguments, missing word-level timestamps, and custom output/interleaving logic.

## Phase 1: Dedicated Chirp-3 Provider [checkpoint: 8d2985c]
Build the foundation for specialized Chirp-3 interaction.

- [x] Task: Create `core/chirp3_provider.py` 0360aa3
    - [ ] Implement `Chirp3Provider` class based on `V2Provider` but with specialized configurations (location, language codes, decoding config).
    - [ ] Ensure it supports streaming and yields `TranscriptionEvent` objects with correctly handled (but empty) `words` lists.
- [x] Task: CLI Integration e3fd074
    - [ ] Update `two_channel_transcribe_v2.py` and `parallel_transcribe.py` to support a `--use-chirp3` flag that selects the new provider.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Dedicated Provider' (Protocol in workflow.md) 8d2985c

## Phase 2: Interleaving Engine Enhancements [checkpoint: 00538b8]
Refine how the `TranscriptionEngine` handles segments that lack word-level timestamps.

- [x] Task: Fallback Interleaving Strategy 00538b8
    - [ ] Update `_interleave_and_split` in `core/engine.py` to robustly handle missing `words` by estimating word boundaries or splitting at mid-segment time points.
- [x] Task: Unit Testing for Wordless Interleaving 00538b8
    - [ ] Expand `tests/test_engine.py` with complex scenarios involving long wordless segments interrupted by short interjections with timestamps.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Engine Enhancements' (Protocol in workflow.md) 00538b8

## Phase 3: Timing Fidelity (Demo Optimized) [checkpoint: VAD_PINNING]
Improve the chronological accuracy of Chirp-3 by leveraging VAD metadata.

- [x] Task: VAD Pinning
    - [x] Update `TranscriptionEngine.process_raw_event` to use `active_starts` to set the `start_sec` of wordless transcripts.
- [x] Task: Comparison Pipeline VAD Support
    - [x] Update `compare_models.py` to allow VAD events to reach the engine (required for pinning).

## Phase 4: Specialized Output and Validation [checkpoint: CHIRP3_COMPLETE]
Optimize the visual and logical output for the Chirp-3 experience.

- [x] Task: Terminal UI Optimization
    - [x] Updated `TerminalSink` to suppress verbose VAD markers and use subtle heartbeat character changes (`+` for speech, `.` for silence).
- [x] Task: Integration and Performance Testing
    - [x] Verified with a 120s full-audio run; confirmed timing accuracy and UI stability.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Final Validation' (Protocol in workflow.md)

