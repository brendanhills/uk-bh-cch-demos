# Gemini Context: Real-Time Transcription Simulator

This project is a high-fidelity simulator for real-time audio transcription. It demonstrates a robust Producer-Consumer architecture for handling multi-channel audio with perfect speaker attribution.

## Project Overview

- **Core Technology:** Python 3.13+, Google Cloud Speech-to-Text V1/V2, Google Cloud Storage.
- **Architecture:**
  - **`core/` package**: High-level abstractions for API providers, stabilization logic, and UI sinks.
  - **`simulate_audio.py`**: Infrastructure for throttling audio to real-time speeds.
  - **Demos**: Refactored scripts (`two_channel_transcribe_v2.py`, `parallel_transcribe.py`) showcasing different scaling strategies.

## Building and Running

### Key Commands
- **Run Stereo Demo (V2)**:
  ```bash
  uv run two_channel_transcribe_v2.py gs://your-bucket/stereo-file.wav --mode readability
  ```
- **Run Model Comparison**:
  ```bash
  uv run compare_models.py gs://your-bucket/stereo-file.wav --model1 telephony --model2 chirp_3
  ```
- **Evaluate Results**:
  ```bash
  uv run diff_transcripts.py -b output/golden.json -s output/live.json
  ```

## Development Conventions

- **Modular Design**: Maintain strict separation between:
    - **Audio Source**: `simulate_audio.py`
    - **API Provider**: `core/providers.py`
    - **Stabilization Engine**: `core/engine.py`
    - **UI/Log Sink**: `core/sinks.py`
- **UI & Formatting**:
  - Use ANSI colors for speaker distinction (Green/Yellow).
  - Leverage `TerminalSink` for real-time "typing" effects and dynamic reflow.
- **Stability Logic**:
  - **End-Based Stability**: Chunks are held until the playhead progresses past their `end_sec`.
  - **Gap Splitting**: Large API results are surgicaly split into turns based on word-level silence.
  - **Active Blocking**: Holds short interjections until long ongoing speech finishes to ensure chronological flow.

## Project Structure

```text
core/
├── models.py    # Standardized TranscriptionEvent
├── providers.py # API Wrappers (V1/V2)
├── engine.py    # Chronological stabilization and splitting
├── sinks.py      # Terminal UI and JSON logging
└── utils.py     # Pipeline orchestration
```
