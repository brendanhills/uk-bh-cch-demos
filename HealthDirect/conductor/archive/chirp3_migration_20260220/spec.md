# Specification: Specialized Chirp-3 Module

## Overview
Implement a dedicated `Chirp3Provider` module within the `core/` package. Unlike standard V2 models, this module will specifically target the unique behavior of Chirp-3: specialized configuration (e.g., auto-language detection), missing word-level timestamps in streaming, and a need for a custom output/interleaving strategy that differs from the existing `telephony` baseline.

## Functional Requirements
- **Dedicated Module:** Create `core/chirp3_provider.py` to encapsulate Chirp-3 specific streaming logic.
- **Specialized Arguments:**
    - Support for `auto` language detection (`language_codes=["auto"]`).
    - Explicit routing to the `us` location for all requests.
    - Configuration for `ExplicitDecodingConfig` tuned for Chirp-3 performance.
- **Wordless Timing Logic:** 
    - Handle results that lack word-level timestamps (which currently causes interleaving logic in `TranscriptionEngine` to fail or behave unexpectedly).
    - Implement a fallback that provides segment-level stability without requiring word data.
- **Custom Output Handling:** 
    - Chirp-3 results often arrive as larger chunks. The system must accommodate these without "buried" interjections or chronological jumps.
    - Provide a toggle for "Chirp-3 Mode" in the CLI to use this specialized pipeline.

## Non-Functional Requirements
- **Extensibility:** The module should be easy to tune for future Chirp-3 updates.
- **UI Integrity:** The `TerminalSink` must clearly label and correctly position Chirp-3 segments even when word-level data is missing.

## Acceptance Criteria
- A standalone `Chirp3Provider` exists and can be invoked separately.
- The `TranscriptionEngine` successfully interleaves Chirp-3 segments with other events without crashing or mis-sorting.
- `two_channel_transcribe_v2.py` can be run with a `--chirp3` flag to enable the specialized behavior.

## Out of Scope
- Modifying the core `V2Provider` to handle every Chirp-3 edge case; the goal is a *dedicated* path.
