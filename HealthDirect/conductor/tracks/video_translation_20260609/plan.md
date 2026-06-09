# Implementation Plan - Live Video Transcription and Translation

## Phase 1: Video Demuxing, Audio Extraction, and Real-Time Streaming Throttler

- [ ] Task: Create `video_source.py` and real-time audio extraction pipeline
    - [ ] Implement an ffmpeg-python utility to extract high-quality audio streams from local video files (MP4/MKV) and GCS video URIs.
    - [ ] Create a real-time audio throttling engine (extending or mirroring `simulate_audio.py`) that streams extracted audio to the STT provider at real-time playhead speeds.
    - [ ] Write unit tests verifying successful audio extraction, format conversions, and precise timing throttling.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Video Demuxing, Audio Extraction, and Real-Time Streaming Throttler' (Protocol in workflow.md)

## Phase 2: High-Fidelity STT Speaker Diarization Integration

- [ ] Task: Integrate Google Cloud STT V2 Speaker Diarization and Dynamic Role Mapping
    - [ ] Configure `V2Provider` to support speaker diarization with configurable speaker counts and limits.
    - [ ] Implement a dynamic mapping layer to translate speaker tags (e.g., `Speaker 1`, `Speaker 2`) to friendly semantic labels (e.g., `Doctor`, `Patient`) based on the timeline.
    - [ ] Write rigorous integration tests using multi-speaker audio to verify over 95% speaker-attribution alignment against a ground-truth golden transcript.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: High-Fidelity STT Speaker Diarization Integration' (Protocol in workflow.md)

## Phase 3: Multi-Modal Visual Context Extraction (Gemini Vision)

- [ ] Task: Implement keyframe extraction and Gemini visual priming
    - [ ] Create a utility to periodically extract video keyframes (e.g., every 5-10 seconds) during playback.
    - [ ] Integrate Gemini Multimodal/Vision to analyze keyframes for slide text, charts, diagrams, or visual cues.
    - [ ] Create a context injector that passes the extracted visual context as dynamic priming context to the translation providers (reusing the translation layers from the Live Translation track).
    - [ ] Write tests ensuring OCR content and visual context are successfully extracted and appended to translation prompts.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Multi-Modal Visual Context Extraction (Gemini Vision)' (Protocol in workflow.md)

## Phase 4: Side-by-Side Video-Aware Terminal UI

- [ ] Task: Build Dual-Column Video Sink with Visual and Speaker Annotations
    - [ ] Extend `TerminalSink` to support video playback time, speaker roles, and visual context indicators (e.g., `[Visual: Slide on Symptoms]`) in the Left Column.
    - [ ] Render synchronized, real-time translations with correct speaker roles in the Right Column.
    - [ ] Verify beautiful formatting and column wrapping on various screen sizes.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Side-by-Side Video-Aware Terminal UI' (Protocol in workflow.md)

## Phase 5: High-Fidelity Video Translation Demo & E2E Verification

- [ ] Task: Implement `video_translate.py` and run benchmark evaluations
    - [ ] Create `video_translate.py` CLI supporting video paths, target languages, and translation providers.
    - [ ] Collect a sample medical video and benchmark transcription, diarization, and translation latency.
    - [ ] Capture terminal results and finalize documentation.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: High-Fidelity Video Translation Demo & E2E Verification' (Protocol in workflow.md)
