# Specification: Bilingual Medical Call Sample Audio Library

## 1. Overview
This track introduces an automated system to generate and manage a high-fidelity library of bilingual medical phone call audio files. These assets are critical for benchmarking, testing, and demonstrating the Real-Time Translation and Gemini Live API systems. The audios will be dynamically synthesized using clear, high-quality Text-to-Speech (TTS) voices.

## 2. Functional Requirements
- **Automated Synthesis Script (`generate_bilingual_audio.py`):**
  - Create a python script that reads structured JSON/YAML dialogue definitions and synthesizes them into stereo WAV files.
  - Support Google Cloud Text-to-Speech (or equivalent) to leverage clear, high-quality native voices.
- **Stereo Dual-Channel WAV Structure:**
  - **Left Channel (Channel 1):** Patient/Parent speaking their native language (e.g., Mandarin, Arabic, Vietnamese).
  - **Right Channel (Channel 2):** Nurse speaking English (with an Australian English accent, e.g., `en-AU`).
  - **Conversational Pacing:** The script must handle speech timing and silences to ensure natural turn-taking (nurse and patient do not talk over each other).
- **Audio Asset Library Contents:**
  - **Short Unit-Test Files (10-30s):** Short, single-exchange medical questions for rapid local unit testing and continuous integration.
  - **Longer Demonstration Conversations (1-3 mins):** Fully realized bilingual medical advice scenarios spanning the following:
    1. **Paediatric:** Parent calling about a child with high fever and respiratory issues.
    2. **Cardiac/Acute:** Patient describing chest pain or severe acute headache.
    3. **Chronic Care:** Elderly patient calling with confusion about medication dosages and scheduling.
    4. **Injury/Wound:** Post-operative patient seeking guidance on wound care and pain management.
    5. **General Triage (German/English):** Caller speaking German presenting with influenza or gastrointestinal symptoms.
- **Metadata Output:**
  - Along with each audio file, generate a matching `.json` transcript metadata file containing the ground-truth bilingual transcript and speaker timeline for validation.

## 3. Non-Functional Requirements
- **Audio Quality:** Output 16kHz or 8kHz linear PCM WAV files (standard clinical telecom quality).
- **Purity of Separation:** 100% separation of channels (no crosstalk between Left and Right channels).

## 4. Acceptance Criteria
- [ ] Running a single script (e.g., `uv run generate_bilingual_audio.py`) synthesizes and organizes all short and long audios in the `samples/` directory.
- [ ] The generated WAV files are verified as dual-channel stereo (Left = Patient, Right = Nurse).
- [ ] Ground-truth transcript JSON files are created for each audio file.
- [ ] Verification tests confirm the synthesized files can be parsed and transcribed by the existing simulator engine.

## 5. Out of Scope for This Track
- Recording live human voices (entirely synthesized using professional TTS engines).
