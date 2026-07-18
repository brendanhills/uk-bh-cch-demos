# Specification: Customer Integration Blueprint & Architecture Pseudocode

## 1. Overview
The goal of this track is to design and produce a comprehensive, high-fidelity customer integration guide (`docs/customer_integration_blueprint.md`) that documents and explains the core architectural patterns of the Real-Time Translation Simulator. This document will include high-level, simplified Python (async/await) pseudocode blocks representing the key logic of our implementation. It will allow customers and external developers to understand and reproduce the solution in their own systems without needing to parse the entire codebase.

## 2. Scope & Target Areas
The cookbook and pseudocode will focus on four primary technical areas:
1. **Model Differences & Architectural Approaches:**
   - Detailed comparison of standard live speech-to-speech models (Gemini 3.1 Live) vs. specialized live translation models (Gemini 3.5 Live Translate).
   - **Dedicated Section for Gemini 3.1 Live:** Detailing its specific setup, configuration parameters, voice/audio output options, and flow.
   - **Dedicated Section for Gemini 3.5 Live Translate:** Detailing its specialized translation config, bilingual output handling, and system constraint configurations.
   - Highlight critical API compatibility nuances (e.g., omitting `system_instruction` when using `translation_config` on `gemini-3.5-live-translate-preview` to prevent WebSocket 1011 crashes).
2. **Gemini Live API WebSocket Connection & Bidirectional Streaming:**
   - Establishing WebSocket connection.
   - Streaming raw audio input in chunks (real-time simulation).
   - Receiving real-time bilingual text translation events.
3. **Clinical Glossary Priming & System Instructions:**
   - Parsing the robust multi-format Australian Medical Glossary schema (flat strings, arrays of strings, and dictionaries with `.formal`/`.informal` keys) recursively.
   - Dynamic injection of the parsed dictionary into the Gemini Live session parameters or system instructions.
4. **Chronological Stabilization & VAD Pinning (Alignment Engine):**
   - Central chronological interleaving of independent speaker streams.
   - Handling end-based stability (playhead progression past `end_sec`).
   - Voice Activity Detection (VAD) pinning to anchor wordless segments.

## 3. Format Requirements
- **Output File:** A single, beautifully formatted Markdown file: `docs/customer_integration_blueprint.md`.
- **Style:** Clean, descriptive prose combined with simplified, asynchronous Python 3.13+ code blocks.
- **Complexity:** Conceptual yet practical, serving as a clean implementation blueprint for integration engineers.

## 4. Acceptance Criteria
- [ ] A dedicated integration guide `docs/customer_integration_blueprint.md` is created.
- [ ] Includes clear diagrams or structural layouts of the Producer-Consumer architecture.
- [ ] Compares Gemini 3.1 Live and Gemini 3.5 Live Translate in dedicated, separate sections, highlighting structural and configuration differences (including `system_instruction` compatibility).
- [ ] Provides high-level async Python pseudocode for Gemini Live WebSocket session setup and data streaming.
- [ ] Provides pseudocode demonstrating robust glossary schema parsing (joining flat strings, arrays, and `.formal`/`.informal` dicts) and injection into `LiveConnectConfig`.
- [ ] Provides pseudocode detailing the central stabilization engine and chronological interleaving logic.
- [ ] High-level explanations accompany all pseudocode sections.
- [ ] The document contains zero placeholders and uses correct Markdown styling (including alerts).

## 5. Out of Scope
- Creating actual executable scripts (this track is strictly for pseudocode reference and documentation).
- Implementing web frontend elements or persistent database storage.
