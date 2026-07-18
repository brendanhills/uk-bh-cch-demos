# Specification - Live Video Transcription and Translation

## Overview
This track introduces real-time video transcription and translation with multi-modal enhancements for the **HealthDirect** scenario. A recorded or live-simulated video (such as a recorded telehealth consultation or training video) contains a mixed audio track with multiple speakers.
- **Media Processing:** Audio is extracted dynamically from local video files (e.g., `.mp4`, `.mkv`) using `ffmpeg` and processed in real time.
- **Speaker Attribution:** Uses **Speaker Diarization** (via Google Cloud STT V2) to separate and attribute speakers from a single audio stream, rather than relying on hardware-separated physical channels.
- **Multi-Modal Integration (Gemini):** Uses visual keyframes extracted from the video (such as slides, medical charts, or on-screen text/OCR) to prime and contextualize the translation engine (via Gemini), significantly improving translation accuracy for clinical and situational terms.

## Scope & Objectives
1. **Video Demuxing & Real-Time Audio Extraction:**
   - Integrate an `ffmpeg`-based pipeline to extract high-quality audio streams from local video files (MP4/MKV) and GCS video URIs.
   - Throttle the audio stream to simulate real-time, matching the video playhead speed.
2. **Dynamic Speaker Diarization:**
   - Configure Google Cloud STT V2 with speaker diarization enabled.
   - Map diarization speaker tags (e.g., "Speaker 0", "Speaker 1") to roles (e.g., "Doctor", "Patient") or dynamic labels in the streaming timeline.
3. **Multi-Modal Translation Context (Gemini):**
   - Extract periodic video keyframes (e.g., every 5-10 seconds or upon slide transitions) using ffmpeg.
   - Use Gemini Vision / Multi-modal API to extract text (OCR), slide content, or visual medical cues from keyframes.
   - Inject this visual context dynamically as "session context" or custom instructions into the translation engine to resolve ambiguous speech or translate specialized medical vocabulary.
4. **Side-by-Side Video-Aware Terminal Sink:**
   - Dual-column terminal rendering:
     - **Left Column:** Chronological live transcription with speaker labels (e.g., `[Speaker 1]: ...`) and visual context indicators (e.g., `[Visual: Slide on Hypertension]`).
     - **Right Column:** Real-time translation to the target language with corresponding speaker labels.

## Verification Criteria
- Successful ffmpeg demuxing and synchronized real-time audio playback.
- **High-Fidelity Speaker Diarization:** Over 95% speaker attribution alignment on sample multi-speaker video compared to ground-truth golden transcripts.
- Successful extraction and inclusion of visual context in Gemini translation prompts.
- Dual-column terminal UI showing synchronized video time, transcription, and contextual translations.
