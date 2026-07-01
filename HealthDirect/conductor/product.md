# Initial Concept
A high-fidelity real-time bilingual interpreter simulator utilizing Gemini Live API's Live Translate (`https://ai.google.dev/gemini-api/docs/live-api/live-translate`), demonstrating real-time voice-to-voice and voice-to-text translation tailored for clinical interactions.

# Vision
Provide a high-fidelity development and evaluation environment for real-time bilingual medical interpreting, enabling developers to build and demonstrate production-ready live translation applications using Gemini Live API's Live Translate.

# Target Users
- **Developers / Engineers:** Building multi-language real-time translation and interpreting tools.
- **Support & Translation Agents:** Needing real-time bilingual support capabilities in clinical contexts.
- **Speech-to-Text & Translation Engineers:** Tuning and comparing different translation and live models.

# Core Goals
1. **Real-time Bilingual Translation:** Specifically utilize the Gemini Live API's Live Translate (`https://ai.google.dev/gemini-api/docs/live-api/live-translate`) to interpret conversational audio in real-time.
2. **Bilingual Stream Delivery:** Real-time side-by-side bilingual speech translation (German/Spanish/Vietnamese <-> English) to simulate live patient-nurse medical consults.
3. **Australian Medical Glossary Priming:** Dynamically inject HealthDirect clinical glossaries to prime the Gemini Live Translate session, ensuring proper terminology mapping.
4. **Interactive Demonstrations:** Provide high-fidelity standalone demo scripts showing translation in action.

# Key Features
- **Gemini Live Translate Integration:** Real-time bidirectional translation using `https://ai.google.dev/gemini-api/docs/live-api/live-translate` to process speech streams.
- **High-Fidelity Standalone Demo Apps:** Lightweight CLI scripts (e.g., `live_translate_demo.py`) that stream audio files in real-time and translate bidirectionally.
- **Side-by-Side Dual-Column UI:** Clean, aligned console layouts mapping the English nurse's dialogue and the patient's foreign-language dialogue in separate columns.
- **Bilingual Terminology Priming:** Dynamic ingestion of custom glossaries (HealthDirect Australia dictionaries) into the Gemini Live session system instructions, ensuring clinical terms are translated according to local Australian standards.

