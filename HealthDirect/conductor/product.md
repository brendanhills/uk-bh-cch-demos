# Initial Concept
A high-fidelity real-time transcription and translation simulator, extending the original Capita transcription project with translation demo applications to showcase speaker-attributed real-time translation.

# Vision
Provide a high-fidelity development and evaluation environment for real-time transcription and translation, enabling developers to build and demonstrate production-ready applications for contact centers and live dashboards with speaker-attributed real-time translation.

# Target Users
- **Developers / Engineers:** Building multi-language real-time transcription and translation tools.
- **Support & Translation Agents:** Needing real-time bilingual support capabilities in transcription contexts.
- **Speech-to-Text & Translation Engineers:** Tuning and comparing different translation and STT APIs.

# Core Goals
1. **Real-time Translation:** Translate live transcripts into target languages in real-time.
2. **Speaker Attribution Alignment:** Map translated sentences to the correct speakers (e.g. Caller vs. Agent) to maintain flow and attribution.
3. **Interactive Selection:** Use interactive prompts to select target languages and configure translation models.
4. **File-based Configuration:** Support settings configuration using JSON/YAML/TOML files.
5. **Interactive Demonstrations:** Provide high-fidelity demo scripts/applications to show transcription and translation side-by-side or in sequence.

# Key Features
- **Real-Time Translation Engine:** An extensible translation layer integrating translation services (like Gemini or Google Cloud Translation) with the live transcription stream.
- **High-Fidelity Demo Apps:** Command-line and terminal-based demo scripts (e.g., `parallel_translate.py`) showing real-time transcription and translation in action.
- **Interactive Console UI:** Colored ANSI logs showing transcription and translation in real-time.
- **Dual-Mode Processing:** Low Latency and Readability modes for transcription.
- **Configuration Management:** Read options (target language, APIs) from a configuration file.
- **Automated Clinical Terminology Ingestion:** Active crawler/pipeline scraping HealthDirect Australia clinical directories to compile multi-lingual medical glossaries, register them with GCP Cloud Translation V3, and dynamically prime Gemini Live sessions.
