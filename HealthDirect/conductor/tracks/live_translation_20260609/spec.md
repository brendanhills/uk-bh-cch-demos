# Specification - Live Speaker-Attributed Real-Time Translation

## Overview
This track introduces real-time speaker-attributed translation tailored for the **HealthDirect** scenario. A citizen calls a health helpline to consult a nurse about medical symptoms. 
- **Channel 1 (Caller/Citizen):** Speaks **German** (or Arabic) -> Transcribed in German -> Translated to **English** for the nurse.
- **Channel 2 (Agent/Nurse):** Speaks **English** -> Transcribed in English -> Translated to **German** (or Arabic) for the citizen.

Because accuracy of medical terminology is critical and the developer/operator may not speak both languages fluently, the system includes dual-mode translation verification:
1. **Live, Real-Time RTT (Round-Trip Translation):** Shows immediate bracketed back-translation segment-by-segment during the call for demo and immediate visual check.
2. **Contextual Batch Back-Translation (Post-Call Evaluation):** Performs block-based back-translation of the entire conversation transcript or large sections at the end of the call. Translating with complete dialog context leverages the LLM's understanding of the full conversation flow, correcting sentence-level ambiguities and generating highly accurate clinical accuracy and safety scorecards.

To ensure fast development cycles, we follow a **Rapid Iteration Strategy**:
- **Phase 0 (Sample Audio Preparation):** Prepare multiple bilingual German-English stereo audio files simulating clinical helpline calls, covering varied voices (male, female, different age/pitch ranges) and clinical topics (e.g., chest pain, fever, pediatric cough). Configure the German STT recognizers and the English `medical_conversation` recognizer.
- **Phase 1 (Rapid Prototype):** Build an offline mock-based translation pipeline. This gets the entire end-to-end multi-threaded architecture working without API dependencies or layout complexities.
- **Phase 2 (Dual-Column UI & Live RTT):** Create the side-by-side terminal UI and integrate the real-time live RTT back-translation logic.
- **Phase 3 (Production APIs):** Integrate Google Cloud Translation V3 (with custom medical glossaries) and Gemini (with clinical-expert prompts).
- **Phase 4 (Batch Evaluation):** Add context-aware post-call evaluation and clinical safety scorecards.
- **Phase 5 (Polish & Benchmarks):** Connect all systems, add control flags, and run final benchmarks.

## Scope & Objectives
1. **Bidirectional Multilingual Stream Integration:**
   - Configure channel-specific source and target languages (Channel 1: German -> English; Channel 2: English -> German).
   - Easily swap to other language pairs (such as Arabic) via configuration.
2. **Specialized Multi-Model STT Architecture:**
   - **Caller (Channel 1, German):** Processed using a standard `telephony` model or standard recognizer configured for `de-DE`.
   - **Nurse (Channel 2, English):** Processed using the specialized GCP Speech-to-Text V2 **`medical_conversation`** model (e.g., via `medical-nurse-recognizer` located in `us` with `--enable-automatic-punctuation`), ensuring maximum vocabulary recognition and accuracy for anatomical terms, diagnoses, and treatments.
3. **Medical Translation Accuracy & Optimization:**
   - **Gemini API / Vertex AI Provider:** Prime the model with dedicated clinical/medical translation system prompts.
   - **Cloud Translation API V3 Provider:** Support custom medical glossaries.
4. **Dual-Mode Translation Accuracy Verification:**
   - **Live RTT:** Translate English -> German -> English (RTT) immediately during the call.
   - **Batch Contextual RTT:** Post-call batch utility that takes the complete transcript, translates the full dialog context back to English, and evaluates translation faithfulness and clinical safety.
5. **Bilingual Terminal Translation Sink:**
   - Dual-column terminal rendering:
     - **Left Column:** Live Transcription (German text for Channel 1 in Green, English text for Channel 2 in Yellow).
     - **Right Column:** Live Translation (English translation for Channel 1 in Green, German translation + English RTT back-translation in brackets `[...]` for Channel 2 in Yellow).

## Verification Criteria
- Correct bidirectional routing (German -> English, English -> German) in tests.
- High translation accuracy on medical terms, validated via automatic evaluation metrics, live RTT, and batch post-call contextual RTT across different voices and clinical topics.
- Over 80% unit test coverage for the RTT verification, evaluation, and translation caching layers.
