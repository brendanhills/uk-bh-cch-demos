# Specification: Gemini Live API - Real-Time Australian Medical Interpreter

## 1. Overview
This track introduces a specialized standalone application demonstrating real-time, bidirectional medical translation/interpretation. It is designed to act as an on-call medical interpreter for phone conversations (e.g., between a non-English speaking patient/parent and an English-speaking nurse), translating speech instantly in both directions.

## 2. Functional Requirements
- **Dynamic Bidirectional Translation (Interpreter Role):**
  - Configure the Gemini Live session with a robust, production-ready system instruction to act as a **Professional Medical Interpreter**.
  - **Behavior:**
    - Listen to both English (e.g., from the nurse) and a selected target language (e.g., Spanish, Cantonese, Vietnamese, Arabic, etc., from the patient/parent).
    - If English is spoken, translate it accurately to the target language and speak it.
    - If the target language is spoken, translate it accurately to English and speak it.
    - Keep translations strictly objective and direct. The interpreter does *not* participate in the conversation, give medical advice, or summarize unless requested; it translates exactly what is said.
- **Medical Terminology Precision:**
  - Prompt instructions must specifically enforce high-fidelity translation for medical vocabulary (e.g., symptoms, anatomical terms, medication names, dosages, and instructions).
- **Australian Medical Localization:**
  - Ensure all translations and terminology prioritize Australian spelling and medical standards.
  - **Vocabulary alignment examples:**
    - Use *paracetamol* instead of *acetaminophen* or *tylenol*.
    - Use *Emergency Department* or *A&E* instead of *Emergency Room* or *ER*.
    - Use *general practitioner* or *GP* instead of *primary care physician*.
    - Use *paediatrician* instead of *pediatrician*, *diarrhoea* instead of *diarrhea*, *hospitalisation* instead of *hospitalization*.
- **Custom Glossary System (`glossary.json`):**
  - Read dynamic custom client terminology mappings from a local `glossary.json` file.
  - Inject these customer-specific rules directly into Gemini's Live system instructions at session startup.
- **Dual Interaction Modes:**
  1. **Live Web Interpreter:** Run a secure web interface (HTTPS/SSL) where two users can talk, with Gemini speaking and displaying translations in real-time.
  2. **Simulated File Stream (Bilingual):** Load a simulated bilingual audio file from `samples/` and stream it to the Live API, rendering the real-time transcription and translation side-by-side to demonstrate accuracy and speed.
- **Authentication:**
  - Primary authentication uses the **Google AI Studio API Key** (standard in `google-genai`).
  - *Future Phase:* Integration with Google Cloud Vertex AI and Application Default Credentials (ADC).

## 3. Non-Functional Requirements
- **Low Latency:** Under 1 second response time for translation/TTS output to ensure natural conversational flow.
- **Voice Clarity:** Choose a clear, distinct, professional voice (e.g., `Puck`, `Charon`, or `Aoede`) for speech rendering.
- **Secure Web Context:** Serve the web interface over HTTPS/SSL locally to allow hassle-free microphone access in the browser.

## 4. Acceptance Criteria
- [ ] A dedicated demo app can be run with a single command (e.g., `uv run main.py`).
- [ ] The app acts as a zero-latency bidirectional translator between English and a target language (e.g., Spanish).
- [ ] The system instruction specifically addresses medical translation rules and Australian localization rules (symptoms, medications, spelling).
- [ ] A simulation script can feed a pre-recorded bilingual audio file and custom dictionary terms to the API, displaying side-by-side results in the console.

## 5. Out of Scope for This Track
- Multi-channel phone routing or actual Twilio billing (this track focuses on local web and file simulation, although it leverages the underlying Twilio-compatible backend logic).
- Native Google Cloud IAM/ADC integration (moved to Phase 2).
