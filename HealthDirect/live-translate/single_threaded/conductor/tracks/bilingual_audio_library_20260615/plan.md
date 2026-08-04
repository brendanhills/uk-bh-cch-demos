# Implementation Plan: Bilingual Medical Call Sample Audio Library

## Phase 1: Dialogue Schema & Script Definitions [checkpoint: 8be3db0]
- [x] Task: Scaffolding and Dialogue Schema Definition (f2b8ae3)
    - [x] Create folder structure for sample definitions under `samples/definitions/`.
    - [x] Define the JSON schema for dialogue scripts (specifying speaker, language, voice, text, and pauses).
    - [x] Draft 4 realistic bilingual script definitions (Paediatric in Vietnamese, Cardiac in Arabic, Chronic in Mandarin, and Wound in Spanish/English) + 1 German/English triage script.
    - [x] Write schema validation tests to ensure all definitions conform to the script format.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Dialogue Schema & Script Definitions' (Protocol in workflow.md) (manual)

## Phase 2: TTS Synthesis & Stereo Panning Engine
- [x] Task: Dual-Channel Synthesis Engine (5aeef01, 0b7cde1)
    - [x] Write failing unit tests verifying mono-to-stereo panning, silence padding, and audio-stitching logic.
    - [x] Implement the backend Text-to-Speech synthesis service (integrating Google Cloud TTS or a high-quality local fallback).
    - [x] Implement the stereo panning engine to place Channel 1 (Patient/Left) and Channel 2 (Nurse/Right) with precise timeline alignment.
    - [x] Implement verification tests confirming 100% channel separation and correct sampling rates.
- [x] Task: Conductor - User Manual Verification 'Phase 2: TTS Synthesis & Stereo Panning Engine' (Protocol in workflow.md)

## Phase 3: CLI Scripter & Integration Tests
- [ ] Task: Generation CLI Scripter (`generate_bilingual_audio.py`)
    - [ ] Implement the CLI script (`generate_bilingual_audio.py`) to automate generating all short and long audios with a single command.
    - [ ] Write integration tests verifying that all generated files have the correct format (16kHz Stereo WAV) and matching ground-truth JSON files.
    - [ ] Run the generated files through the existing transcription simulator to verify that the speech-to-text engines successfully parse and attribute speakers.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: CLI Scripter & Integration Tests' (Protocol in workflow.md)
