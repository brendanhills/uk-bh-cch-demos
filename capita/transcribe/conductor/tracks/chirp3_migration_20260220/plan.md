# Implementation Plan: Specialized Chirp-3 Module

Implement a dedicated `Chirp3Provider` module to handle the unique requirements of the Chirp-3 model, including specialized arguments, missing word-level timestamps, and custom output/interleaving logic.

## Phase 1: Dedicated Chirp-3 Provider [checkpoint: 8d2985c]
Build the foundation for specialized Chirp-3 interaction.

- [x] Task: Create `core/chirp3_provider.py` 0360aa3
    - [ ] Implement `Chirp3Provider` class based on `V2Provider` but with specialized configurations (location, language codes, decoding config).
    - [ ] Ensure it supports streaming and yields `TranscriptionEvent` objects with correctly handled (but empty) `words` lists.
- [x] Task: CLI Integration e3fd074
    - [ ] Update `two_channel_transcribe_v2.py` and `parallel_transcribe.py` to support a `--use-chirp3` flag that selects the new provider.
- [~] Task: Conductor - User Manual Verification 'Phase 1: Dedicated Provider' (Protocol in workflow.md)

## Phase 2: Interleaving Engine Enhancements
Refine how the `TranscriptionEngine` handles segments that lack word-level timestamps.

- [ ] Task: Fallback Interleaving Strategy
    - [ ] Update `_interleave_and_split` in `core/engine.py` to robustly handle missing `words` by estimating word boundaries or splitting at mid-segment time points.
- [ ] Task: Unit Testing for Wordless Interleaving
    - [ ] Expand `tests/test_engine.py` with complex scenarios involving long wordless segments interrupted by short interjections with timestamps.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Engine Enhancements' (Protocol in workflow.md)

## Phase 3: Specialized Output and Validation
Optimize the visual and logical output for the Chirp-3 experience.

- [ ] Task: Terminal UI Optimization
    - [ ] Ensure `TerminalSink` correctly labels Chirp-3 results and handles their potentially larger chunk size without UI jitter.
- [ ] Task: Integration and Performance Testing
    - [ ] Run end-to-end tests using `samples/0638.mp3` with the new Chirp-3 module.
    - [ ] Verify chronological integrity and structural validity of the JSON output.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Final Validation' (Protocol in workflow.md)
