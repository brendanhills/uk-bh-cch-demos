# Gemini Context: Real-Time Transcription Simulator

This project is a high-fidelity simulator for real-time audio transcription using the Google Cloud Speech-to-Text (STT) API. It streams audio from Google Cloud Storage (GCS) at real-time speeds to demonstrate "live" transcription experiences with polished CLI output and accurate speaker attribution.

## Project Overview

- **Core Technology:** Python 3.13+, Google Cloud Speech-to-Text V1/V2, Google Cloud Storage.
- **Purpose:** To provide a robust foundation for testing and demonstrating real-time transcription logic, specifically focusing on handling speaker diarization and multi-channel audio with minimal latency or maximum readability.
- **Architecture:**
  - **`simulate_audio.py`**: Handles real-time audio streaming from GCS. It downloads the file, normalizes it to Linear16 PCM, and streams it in 250ms chunks.
  - **`transcribe_common.py`**: Contains the engine logic (`BaseTranscriptionService` and `TranscriptionService`). It manages stability buffers, active-speech tracking, and the columnar terminal UI.
  - **Frontends**:
    - `two_channel_transcribe_v2.py`: The primary demo script supporting `low_latency` and `readability` modes.
    - `mono_transcribe_v1.py`: Legacy support for single-channel files using V1 Diarization.
    - `transcribe.py`: A baseline implementation for customer comparison.

## Building and Running

### Prerequisites
- **Python 3.13+** (managed via `uv` or `pip`).
- **Google Cloud SDK**: Authenticated via `gcloud auth application-default login`.
- **Environment Variables**: Managed via a `.env` file (see `env.example`).
  - `PROJECT_ID`: Your GCP Project ID.
  - `LOCATION`: GCP region (default: `us-central1`).
  - `GCP_RECOGNIZER_ID`: The ID for the STT V2 Recognizer.

### Key Commands
- **Run Stereo Demo (V2)**:
  ```bash
  uv run two_channel_transcribe_v2.py gs://your-bucket/stereo-file.wav --mode readability
  ```
- **Run Mono Demo (V1)**:
  ```bash
  uv run mono_transcribe_v1.py gs://your-bucket/mono-file.mp3
  ```
- **Run Integration Tests**:
  ```bash
  uv run pytest test_transcribe_integration.py -s
  ```

## Development Conventions

- **Modular Design**: Keep audio streaming logic in `simulate_audio.py` and transcription/UI logic in `transcribe_common.py`.
- **UI & Formatting**:
  - Use ANSI colors for speaker distinction: Green (Caller), Yellow (Agent), Grey (Interims).
  - Use the `_print_in_column` method for real-time draft overwriting to ensure a "typing" effect.
- **Stability Logic**:
  - **Stability Threshold**: Holds finalized chunks to ensure chronological order.
  - **Gap-Based Splitting**: Detects silence between words to break long monologues into turns.
  - **Active Blocking**: Prevents short interruptions from appearing before longer ongoing speech finishes.
- **Error Handling**: Implement automatic reconnection for streaming requests in `TranscriptionService.run`.

## Key Files

- `transcribe_common.py`: The core engine for handling STT responses and terminal rendering.
- `simulate_audio.py`: The infrastructure for throttling GCS audio to real-time speeds.
- `two_channel_transcribe_v2.py`: The main entry point for the modern V2 multi-channel demo.
- `pyproject.toml`: Defines dependencies including `google-cloud-speech`, `pydub`, and `ffmpeg-python`.
- `test_transcribe_integration.py`: Integration tests that mock playback delays for fast verification.
