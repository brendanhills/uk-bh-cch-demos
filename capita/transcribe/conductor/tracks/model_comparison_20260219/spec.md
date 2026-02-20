# Specification: Model Comparison Framework

## Objective
The Model Comparison Framework allows developers to run the same audio stream through multiple Google Cloud Speech-to-Text (STT) models simultaneously (e.g., Telephony vs. Chirp) and compare their performance (latency, accuracy, attribution) in real-time.

## User Stories
- **As a developer**, I want to compare different STT models side-by-side to determine which one is most accurate for my use case.
- **As a developer**, I want to see the real-time interim results from both models at the same time to compare their "typing" speed and stability.
- **As a developer**, I want to use a single CLI command to run a comparison against a GCS file.

## Requirements
- **Simultaneous Streaming:** Ability to open multiple STT streaming requests for the same audio source.
- **Synchronized Throttling:** The audio streaming logic in `simulate_audio.py` must push chunks to all active transcription services at the same real-time rate.
- **Comparison UI:** A columnar terminal UI that displays two models side-by-side or stacked, with distinct colors for each.
- **Model Support:** Explicit support for `telephony` and `chirp_3` models.
- **Dynamic Endpoints:** Support for switching between regional (e.g., `us-central1`) and global (e.g., `us`) endpoints based on model requirements (Chirp-3 requires global).
- **Configuration:** Support configuring the models (e.g., `telephony`, `chirp_3`) via CLI arguments or a configuration file.

## Architecture
- **Engine:** Extend `BaseTranscriptionService` to allow for multiple instances or a coordinated manager.
- **UI:** A new `ComparisonUI` class that manages multiple column displays.
- **Driver:** A new entry point script `compare_models.py`.

## Success Criteria
- [ ] A single CLI command can launch a comparison between two different STT V2 models.
- [ ] Both models receive the same audio data in the same 250ms chunks.
- [ ] Transcription results are rendered clearly in the terminal.
