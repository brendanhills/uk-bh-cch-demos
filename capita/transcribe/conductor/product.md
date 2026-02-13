# Initial Concept
To help a developer build the best live transcription app - with correct transcription, accurate timing, and correct attribution. The input will be 2 channel audio of a phone conversation

# Vision
Provide a high-fidelity development and evaluation environment for real-time transcription, enabling developers to build production-ready applications for contact centers and live dashboards with perfect speaker attribution and natural conversational flow.

# Target Users
- **Contact Center AI Developers:** Building tools for agent assistance, real-time analytics, and automated compliance.
- **Frontend Engineers:** Creating real-time transcription dashboards that require polished UI/UX and accurate "typing" feedback.
- **Speech-to-Text Engineers:** Tuning API parameters and comparing different AI models and synchronization strategies.

# Core Goals
1. **Unrivaled Attribution:** Leverage multi-channel audio to provide 100% reliable speaker identification (Caller vs. Agent).
2. **Timing Precision:** Ensure transcripts align perfectly with audio playback, resolving race conditions between asynchronous streams.
3. **Logic Evaluation:** Provide a "sandbox" to compare different transcription strategies (e.g., Low Latency vs. Readability) and STT models (e.g., Telephony, Chirp).
4. **Visual Polish:** Demonstrate best practices for rendering real-time interim results in a columnar CLI interface.

# Key Features
- **Real-Time GCS Streaming:** Simulates a live phone call by throttling audio playback in 250ms chunks.
- **Dual-Mode Processing:**
    - **Low Latency Mode:** Focuses on immediate arrival, ideal for instant feedback.
    - **Readability Mode:** Uses stability buffers and active-speech blocking to ensure strict chronological order and natural turn-taking.
- **Gap-Based Splitting:** Automatically detects silence between words to partition monologues into readable paragraphs.
- **Unified STT V2 Engine:** A modular core that supports easy swapping of models and configuration features.
- **Visual Terminal UI:** Real-time columnar display with ANSI-colored interim and final results.
