# Implementation Plan: Gemini Live API - Real-Time Australian Medical Interpreter

## Phase 1: Environment & Medical Prompt Scaffolding [checkpoint: 994cf40]
- [x] Task: Project Scaffolding and Environment Setup
    - [x] Create folder structure for the new standalone demo.
    - [x] Configure `.env` with variables for model name, Australian prompt, and default target language.
    - [x] Write initial test assertions for the system instruction to ensure it matches the medical and Australian localization requirements.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Scaffolding' (Protocol in workflow.md) (994cf40)

## Phase 2: Medical Translation & Glossary Engine (Backend)
- [x] Task: Backend System Instruction & Session Manager (695e99b)
    - [x] Write failing unit tests verifying that the prompt translator replaces Americanisms with Australian medical terminology.
    - [x] Implement the dynamic system prompt with strict rules for Australian spelling and medications.
    - [x] Implement robust error and session connection handlers.
- [x] Task: Custom Glossary System (`glossary.json`) (e336aa2)
    - [x] Design a simple JSON schema for customer-specific terms (`glossary.json`).
    - [x] Write a backend utility that reads `glossary.json` and injects it into Gemini's system instructions.
    - [x] Write unit tests verifying that customer-specific vocabulary is correctly formatted and injected into the Live session config.
- [x] Task: Simulated File Streaming Handler (40c02f0)
    - [x] Write unit tests for audio-file segment chunking and streaming.
    - [x] Implement the backend chunking logic to feed local audio files to the Gemini Live session to simulate a phone call.
- [~] Task: Conductor - User Manual Verification 'Phase 2: Backend Translation Engine' (Protocol in workflow.md)

## Phase 3: Interactive Frontend (Live Mode)
- [ ] Task: Build Responsive Side-by-Side Web UI
    - [ ] Design a premium browser interface with side-by-side dual columns: Patient/Parent (Target Language) vs. Nurse (English).
    - [ ] Implement custom styles matching premium modern web aesthetics.
    - [ ] Write frontend unit tests for WebSocket client connectivity.
- [ ] Task: Integration of Microphone & Web Audio Out
    - [ ] Integrate local microphone capture and secure WebSocket streaming.
    - [ ] Implement low-latency audio playback of Gemini's TTS translations.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Frontend Web App' (Protocol in workflow.md)

## Phase 4: Verification and Evaluation (Simulation Mode)
- [ ] Task: Simulation Evaluation Script
    - [ ] Create a simulation script (`simulate_medical_call.py`) that reads a pre-recorded nurse-patient bilingual audio dialogue.
    - [ ] Feed dialogue to the Live API and render the output side-by-side in the console.
    - [ ] Verify that Australian terminology and custom glossary terms are correctly chosen in real-time outputs.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Evaluation & Handoff' (Protocol in workflow.md)
