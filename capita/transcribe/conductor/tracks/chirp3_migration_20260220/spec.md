# Specification: Migrate to Chirp 3 as Default Model

## Overview
Google Cloud's Speech-to-Text V2 models are undergoing deprecation. This track migrates the simulator to use **Chirp 3** as the primary default model to ensure long-term compatibility and leverage the latest accuracy improvements.

## Functional Requirements
- **Default Model Transition:** Update the default model configuration from `telephony` to `chirp-3` across all demo scripts.
- **Global Region Support:** Ensure API requests for Chirp 3 are routed through the `us` (global) multi-region endpoint.
- **Robust Timing Logic:** Refine the `TranscriptionEngine` and `TerminalSink` to gracefully handle results without word-level timestamps (common in Chirp 3), utilizing segment-level timing and existing estimation logic.
- **CLI Integration:** Update `compare_models.py` and other utilities to prioritize Chirp 3 as the baseline model.

## Non-Functional Requirements
- **Latency Parity:** Chirp 3 should perform with comparable real-time latency to the current telephony model.
- **Accuracy Parity:** Ensure transcription quality meets or exceeds the current baseline.
- **UI Fidelity:** The terminal UI must correctly identify and label segments originating from Chirp 3.

## Acceptance Criteria
- `two_channel_transcribe_v2.py` runs with Chirp 3 by default without requiring manual flags.
- Real-time transcription, reflow, and multi-channel interleaving function correctly with Chirp 3 data.
- Automated tests pass with Chirp 3 event structures (even when `words` metadata is empty).

## Out of Scope
- Implementing a complex word-alignment algorithm for models without native word-level timestamps.
