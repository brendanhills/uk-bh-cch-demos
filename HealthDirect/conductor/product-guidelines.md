# Product Guidelines

These guidelines define the quality standards, architectural principles, and user experience goals for the Real-Time Transcription and Translation Simulator.

## 1. Tone and Voice
- **Highly Technical & Detailed:** Focus on developer-facing clarity, including detailed breakdowns of model mechanics, latency metrics, API behavior, and synchronization timing details.
- **Demo-Oriented:** Emphasize demonstrating concepts, latency comparison, and real-time behavioral differences in the UI rather than production deployment constraints.

## 2. User Experience (UX) and Presentation Standards
- **Side-by-Side Bilingual View:** Render the source transcription on the left, and target translation on the right. Maintain clear visual alignment between speakers (Caller vs. Agent).
- **Comparison Modes:** Allow users to see and compare the performance of:
    - **Real-Time (Interim/Word-by-word) Translation:** Streamed and updated dynamically as speech progresses.
    - **Segment-Based Translation:** Completed and stabilized only when the speaker finishes a logical sentence/segment.
- **Latency Indicators:** Show real-time translation and STT latency metrics in the UI.

## 3. Accuracy, Synchronization, and Translation Logic
- **Chronological Stability:** Ensure translated sentences map to the correct speaker and are synchronized with the audio playhead.
- **Comparison Sandbox:** The system must run both translation paradigms (real-time vs. segment-based) side-by-side or toggled, allowing side-by-side quality and latency evaluation.
- **Inline Error Indicators:** If a translation request fails or experiences latency issues, display inline indicators such as `[Translating...]` or `[Translation Error]` in the UI.

## 4. Architectural Principles
- **Extensible Provider System:** Maintain a modular interface for translation providers (e.g., Gemini Translate, Cloud Translation API V3) similar to the STT provider model.
- **Decoupled Translation Pipeline:** Keep transcription logic separate from translation processing. Translation should hook into the stabilization engine as a downstream event consumer.
- **Demo-First Design:** Focus on simulation fidelity, clean code design, and readability for presentation, prioritizing demo setup ease over production hardening.

## 5. Development and Demo Workflow
- **Dependency Management:** Use `uv` for package management and environment isolation.
- **Simple Setup & Execution:** The demo must be easy to run with straightforward CLI commands (e.g., `uv run parallel_translate.py`).
