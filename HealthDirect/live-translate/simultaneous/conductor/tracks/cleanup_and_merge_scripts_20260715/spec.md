# Specification: Cleanup and Merge Codebase Scripts (`cleanup_and_merge_scripts`)

## 1. Overview
This track is a systematic review, merge, and cleanup of codebase files. It focuses on consolidating redundant audio generator scripts, preserving helpful developer utilities (like model listing), organizing isolated components into standard directory structures, and removing dead or obsolete experimental dumps.

## 2. Scope & Consolidation Actions
*   **Keep & Standardize Model Utilities**:
    *   **Decision**: **Preserve `list_vertex_models.py`**. Keep it at the root (or move it to a clean utilities area) so that AI assistants and developers can easily run it to discover active Vertex/Gemini models.
*   **Audio Generators Consolidation**:
    *   **Candidates**: `generate_arabic_audio.py`, `generate_spanish_audio.py`, `generate_bilingual_audio.py`, `generate_simultaneous_audio.py`.
    *   **Action**: Consolidate language-specific parameters into `generate_simultaneous_audio.py` / `generate_bilingual_audio.py`, then delete the redundant, single-language hardcoded audio generation scripts.
*   **Scratch & Utility Assessment**:
    *   **Action**: Review root files like `glossary_highlighter.py` and any logging/diagnostic leftovers. If they serve as production utility code, organize or document them cleanly. If they are dead logs/temp dumps, prune them.

## 3. Verification & Acceptance Criteria
*   **No Broken Imports**: All core demos and scripts run with zero import failures.
*   **Complete Test Passing**: `pytest` passes flawlessly.
