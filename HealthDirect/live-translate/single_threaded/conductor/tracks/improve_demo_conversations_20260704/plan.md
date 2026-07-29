# Implementation Plan: Improving Demo Sample Conversations

## Phase 1: Vietnamese Synthesis Implementation & Base Coverage
- [ ] Task: Write Failing Tests for Vietnamese Audio Generation
    - [ ] Create `tests/test_vietnamese_audio.py` to assert correct file output, dual-channel layout, and sample rate.
    - [ ] Run the tests and confirm they fail.
- [ ] Task: Implement `generate_vietnamese_audio.py`
    - [ ] Author a natural, idiomatic, and polite Vietnamese dialogue for a paediatric triage scenario.
    - [ ] Select high-quality Vietnamese TTS voices (e.g., `vi-VN-Wavenet-*`).
    - [ ] Generate the linear16 PCM stereo WAV file and export to `samples/paediatric_vietnamese_demo.wav`.
    - [ ] Run the tests and confirm they now pass.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Vietnamese Synthesis Implementation & Base Coverage' (Protocol in workflow.md)

## Phase 2: Dialogue & Timing Optimizations (DE, ES, AR, VI)
- [ ] Task: Write/Update Timing Validation Tests
    - [ ] Add tests validating that silence gaps are bounded and no overlap markers exist in transcripts.
    - [ ] Run the tests and confirm any failures or areas of improvement.
- [ ] Task: Refine German Dialogue & Timings in `generate_bilingual_audio.py`
    - [ ] Rewrite German parts to use highly authentic medical idioms, warm empathetic tone, and natural phrasing.
    - [ ] Recalibrate start times (`start_ms`) to eliminate dead air gaps and overlap risks.
- [ ] Task: Refine Spanish Dialogue & Timings in `generate_spanish_audio.py`
    - [ ] Rewrite Spanish parts to use natural, polite medical dialogue and concerned parent idioms.
    - [ ] Recalibrate start times (`start_ms`) to optimize pacing and turn-taking.
- [ ] Task: Refine Arabic Dialogue & Timings in `generate_arabic_audio.py`
    - [ ] Rewrite Arabic parts for conversational warmth, appropriate medical jargon, and native flow.
    - [ ] Recalibrate start times (`start_ms`) to resolve the reported long silence gaps.
- [ ] Task: Refine Vietnamese Dialogue & Timings in `generate_vietnamese_audio.py`
    - [ ] Fine-tune Vietnamese timings and word phrasing for optimal rhythm.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Dialogue & Timing Optimizations (DE, ES, AR, VI)' (Protocol in workflow.md)

## Phase 3: Pacing Engine Fine-Tuning & Integration Verification
- [ ] Task: Write Integration Tests for Pacing Verification
    - [ ] Assert that the real-time simulation with the updated presets runs smoothly without overlap.
- [ ] Task: Tune Pacing Configurations in Live Demo
    - [ ] Adjust default parameters or pacing engine config thresholds (e.g., silence threshold, playhead timing) in `live_translate_demo.py` or the core engine.
    - [ ] Verify that real-time side-by-side playback does not overlap.
- [ ] Task: Run Full Regression and Verify Quality Gates
    - [ ] Execute all pytest cases (68+ tests) and ensure they pass.
    - [ ] Verify test coverage is >80% for modified code.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Pacing Engine Fine-Tuning & Integration Verification' (Protocol in workflow.md)
