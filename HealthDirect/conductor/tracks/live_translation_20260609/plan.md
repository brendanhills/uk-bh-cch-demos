# Implementation Plan - Live Real-Time Translation (Gemini Live API)

## Phase 1: Standalone End-to-End Live Translation Demo

- [x] Task: Prepare Bilingual Audio Samples
    - [x] Streamline and verify the existing `de_fever_session.wav` file.
    - [x] Keep Spanish and Vietnamese sessions as future extension files.
- [x] Task: Standalone Live Translate Script (`live_translate_demo.py`)
    - [x] Create a standalone script in the project root connecting directly to the Gemini Live API over WebSockets using the `google-genai` Python SDK.
    - [x] Avoid intermediate local websocket server layers to make the demo self-contained and easy to run.
- [x] Task: Side-by-Side Dual-Column UI
    - [x] Build an elegant, aligned double-column console layout mapping original speech and translations side-by-side per speaker (English nurse vs. foreign patient).

## Phase 2: Terminology Priming & Australian Standardization

- [x] Task: Integrate HealthDirect Clinical Glossary
    - [x] Parse dynamic terms from `dictionary/glossary.json` into the Gemini system prompt instructions to prime translation safety.
    - [x] Enforce Australian medical standards (e.g. mapping "acetaminophen" to "paracetamol") directly in the live system instructions.

## Phase 3: Verification & Elaboration

- [x] Task: Verify with Active Calls
    - [x] Run the translation demo and log the output to verify translation quality and accuracy on clinical terms.
- [x] Task: Elaborate with Additional Features
    - [x] Add support for Spanish and Vietnamese audio sessions.
    - [x] Improve UI layout with color customization and typing indicators.
    - [x] Expand medical glossary term mappings based on feedback.

