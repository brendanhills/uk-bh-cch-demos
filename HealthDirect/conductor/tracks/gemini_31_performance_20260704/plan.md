# Implementation Plan: Improving Gemini 3.1 Flash Live Performance

This plan outlines the specific tasks to improve the quality of standard Gemini 3.1 Flash Live sessions, focusing on dynamic voice gender selection, real-time streamed text segments, enhanced tone preservation, and pacing freeze mitigations.

## Phase 1: Voice Gender Selection & Real-Time Transcription
- [x] Task: Implement Dynamic Voice Gender Selection
    - [x] Extract patient speaker gender from preset settings in `web_server.py`.
    - [x] Update config builder to conditionally inject `speech_config.voice_config.prebuilt_voice_config` into `LiveConnectConfig`.
    - [x] Match translated patient speech to patient gender (e.g. Puck/Charon for male) and translated nurse speech to female voice (Kore).
- [x] Task: Stream Real-Time Translation Text Segments
    - [x] Modify `receive_p_to_n` and `receive_n_to_p` receivers to listen for `server_content.model_turn.parts` containing text.
    - [x] Immediately forward text segments via client WebSocket with `type: "transcript"`, matching current speaker turn.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Voice Gender Selection & Real-Time Transcription' (Protocol in workflow.md)

## Phase 2: Tone Preservation & Pacing Resilience
- [ ] Task: Enhance Tone Preservation in System Instructions
    - [ ] Update `assemble_system_instructions` passive constraint prompt to demand standard model match the tone, urgency, clinical empathy, and pace of the speaker.
- [ ] Task: Resolve Pacing Machine Hangs & Freezes
    - [ ] Investigate standard model's `turn_complete` signals.
    - [ ] Implement fallback timeout boundaries or audio power envelope monitoring to guarantee playhead progression if standard model `turn_complete` is delayed.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Tone Preservation & Pacing Resilience' (Protocol in workflow.md)

## Phase 3: Automated Testing & Polishing
- [ ] Task: Add Automated Tests for 3.1 Refinements
    - [ ] Add unit and mock tests in `tests/test_live_glossary_enforcement.py` (or a new test file) for voice matching, real-time chunk forwarding, and non-blocking pacing.
- [ ] Task: Review code, check full pytest regression suite, and finalize track.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Automated Testing & Polishing' (Protocol in workflow.md)
