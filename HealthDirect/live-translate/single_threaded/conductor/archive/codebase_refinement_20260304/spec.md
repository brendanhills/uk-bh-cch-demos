# Specification: Codebase Consolidation and Refinement

## Overview
As new features (Chirp-3, Parallel Workers, Model Comparison) were added, some logic was duplicated or became fragmented. This track aims to consolidate shared logic, simplify state management, and ensure consistent behavior across all transcription paths.

## Key Refactorings

### 1. Logic Consolidation
- **Gap Splitting:** Unify the `_split_on_gaps` logic currently duplicated in `core/engine.py` and `core/workers.py` into a shared utility or a method on `TranscriptionEvent`.
- **Timing Estimation:** Unify the "linear word distribution" logic currently present in `core/engine.py` and `core/chirp3_provider.py`.

### 2. Provider Inheritance
- **V2 vs Chirp-3:** Consolidate `V2Provider` and `Chirp3Provider`. Since they both use the V2 API, `Chirp3Provider` should primarily be a configuration profile for `V2Provider` rather than a full override of the `stream` method.

### 3. Data Model Improvements
- **Metadata in Dict:** Update `TranscriptionEvent.to_dict()` to include the `metadata` (e.g., model name) so that evaluation tools can distinguish results without parsing filenames.

### 4. Technical Debt
- **Env Loading:** Centralize `load_dotenv()` to avoid redundant calls in every utility and worker.
- **Audio Operations:** Prepare for the deprecation of `audioop` in Python 3.13 by ensuring we use `audioop-lts` consistently or extracting it to a single wrapper.

## Non-Functional Goals
- **Zero Behavioral Change:** All existing demos and integration tests MUST pass exactly as they do today.
- **Improved Readability:** Reduce the line count of the `core/` package by removing redundant logic.

## Architectural Constraints
- **Simulator Isolation:** The `AudioStreamSimulator` (`simulate_audio.py`) MUST remain strictly independent of the `core/` transcription package. It should continue to handle raw audio bytes and timing without knowledge of transcription data models or API providers.
- **Queue-Based Boundary:** The communication between the simulator/broadcaster and the transcription workers MUST remain via `asyncio.Queue` to preserve the decoupled producer-consumer architecture.
- **Language Simplification:** The system is restricted to **English only** for this demo. Redundant language detection or multi-language routing logic should be removed or simplified to default to `en-US`.

## Acceptance Criteria
- `uv run pytest` passes 100%.
- All three demos (`two_channel`, `parallel`, `compare`) run without errors.
- Code coverage remains >80% for core modules.
