# Gemini Context: Real-Time Transcription Simulator

This project is a high-fidelity simulator for real-time audio transcription. It demonstrates a robust Producer-Consumer architecture for handling multi-channel audio with perfect speaker attribution.

## Project Overview

- **Core Technology:** Python 3.13+, Google Cloud Speech-to-Text V2.
- **Architecture:** 
  - **Producer-Consumer**: Stereo audio is split into independent mono streams (Producers) and re-interleaved by a central logic engine (Consumer).
  - **`core/` package**: High-level abstractions for API providers, stabilization logic, and UI sinks.
  - **`parallel_transcribe.py`**: The definitive high-fidelity demo using centralized interleaving.
  - **`simulate_audio.py`**: Infrastructure for throttling audio to real-time speeds.

## Building and Running

### Key Commands
- **Run Stereo Demo (V2)**:
  ```bash
  uv run two_channel_transcribe_v2.py gs://your-bucket/stereo-file.wav --mode readability
  ```
- **Run Parallel High-Fidelity Demo**:
  ```bash
  uv run parallel_transcribe.py gs://your-bucket/stereo-file.wav --model chirp_3
  ```
- **Run Model Comparison**:
  ```bash
  uv run compare_models.py gs://your-bucket/stereo-file.wav --model1 telephony --model2 chirp_3
  ```
- **Evaluate Results**:
  ```bash
  uv run diff_transcripts.py -b output/golden.json -s output/live.json
  ```
- **Incorporate Bilingual Medical Glossary (Scrape & Translate)**:
  ```bash
  # Scrape Medicines Directory
  uv run import_glossary.py --scrape https://www.healthdirect.gov.au/medicines --ground
  # Scrape Conditions Directory
  uv run import_glossary.py --scrape https://www.healthdirect.gov.au/health-topics/conditions --ground
  # Scrape Symptoms Directory
  uv run import_glossary.py --scrape https://www.healthdirect.gov.au/health-topics/symptoms --ground
  # Scrape Procedures Directory
  uv run import_glossary.py --scrape https://www.healthdirect.gov.au/health-topics/procedures --ground
  ```

## Development Conventions

- **Modular Design**: Maintain strict separation between:
    - **Audio Source**: `simulate_audio.py`
    - **API Provider**: `core/providers.py`
    - **Stabilization Engine**: `core/engine.py` (The "Central Brain")
    - **UI/Log Sink**: `core/sinks.py`
- **UI & Formatting**:
  - Use ANSI colors for speaker distinction (Green/Yellow).
  - Leverage `TerminalSink` for real-time "typing" effects and dynamic side-by-side reflow.
- **Stability Logic**:
  - **End-Based Stability**: Chunks are held until the playhead progresses past their `end_sec`.
  - **VAD Pinning**: High-latency models (Chirp-3) use Voice Activity Detection metadata to anchor wordless segments to the correct chronological position.
  - **Active Blocking**: Prevents monologues from being interrupted by future speech, ensuring a natural turn-taking flow.

## Project Structure

```text
core/
├── models.py    # Standardized TranscriptionEvent
├── providers.py # API Wrappers (V2)
├── engine.py    # Chronological stabilization, VAD pinning, and splitting
├── sinks.py      # Terminal UI and JSON logging
└── workers.py   # Independent channel workers for parallel streams
```
