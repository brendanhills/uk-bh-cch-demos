# Implementation Plan - Live Speaker-Attributed Real-Time Translation

## Phase 0: Sample Audio Preparation & Language Selection

- [~] Task: Prepare Bilingual German-English Test Audios (Multiple Voices & Topics)
    - [x] Generate 1 initial bilingual German-English stereo audio file to prove it works
    - [ ] Establish remaining multi-voice/topic suite files
    - [ ] Set up German STT recognizer configuration (`de-DE`) for Channel 1 (German Caller) and the specialized Speech-to-Text V2 **`medical_conversation`** recognizer (`medical-nurse-recognizer` located in `us` with automatic punctuation) for Channel 2 (English Nurse).
    - [ ] Update `.env` or configuration parameters to support switching between different test files and recognizers easily.
- [ ] Task: Conductor - User Manual Verification 'Phase 0' (Protocol in workflow.md)

## Phase 1: Rapid Prototype & Mock translation (Minimal Viable Pipeline)

- [ ] Task: Define Translation Interface and Mock Provider with Medical Map
    - [ ] Create `core/translation.py` defining the base abstract class `TranslationProvider` with an asynchronous `translate()` method.
    - [ ] Implement `MockTranslationProvider` with a fast, static dictionary of German/English medical terms (e.g., "Kopfschmerzen" -> "headache", "Fieber" -> "fever") to simulate live translation offline.
    - [ ] Add unit tests in `tests/test_translation.py` (>80% coverage).
- [ ] Task: Quick-and-Dirty Demo Script Integration
    - [ ] Create a lightweight version of `parallel_translate.py` that streams dual-channel audio, runs transcription, runs mock translations, and prints basic inline logs to prove pipelining works.
    - [ ] Verify the entire end-to-end pipelining works without any external API calls or complex layout requirements.
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Dual-Column Bilingual UI & Live RTT

- [ ] Task: Side-by-Side Dual-Column UI Sink
    - [ ] Create `TerminalTranslationSink` (or extend `TerminalSink` in `core/sinks.py`) supporting dynamic column wrapping.
    - [ ] Left Column: Live Transcription (renders German script for Caller, English for Nurse).
    - [ ] Right Column: Live Translation.
- [ ] Task: Live Bidirectional Routing and Segment-level RTT
    - [ ] Update `core/engine.py` to route German $\leftrightarrow$ English per channel.
    - [ ] Implement Live RTT (Round-Trip Translation) for Channel 2: translates English -> German -> English, displaying it in brackets `[RTT: ...]` so the nurse can verify the translation's safety in real-time.
    - [ ] Implement RTT caching to minimize repeated translation calls.
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Production Translation Providers (Gemini & Cloud Translation V3)

- [ ] Task: Integrate Production Translation APIs
    - [ ] Implement `GeminiTranslationProvider` in `core/providers.py` utilizing the Gemini API with a specialized clinical translation expert system prompt to ensure high-fidelity German $\leftrightarrow$ English translation.
    - [ ] Implement `CloudTranslationV3Provider` with support for Google Cloud Translation V3 custom glossaries to map medical/anatomical terminology.
    - [ ] Implement `CloudTranslationV2Provider` as basic machine translation comparison baseline.
    - [ ] Write mock-based unit tests for all production APIs to maintain >80% coverage.
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Batch Contextual Post-Call Evaluation

- [ ] Task: Batch Contextual Back-Translation & Quality Assessor
    - [ ] Implement a batch post-call evaluation module (`core/evaluator.py`) that processes the entire completed conversation transcript at the end of the call.
    - [ ] Support block-based contextual translation back to English to leverage LLM dialog context and eliminate sentence-level ambiguities.
    - [ ] Generate an automated LLM clinical quality report utilizing Gemini as an independent medical evaluator, grading translation safety, accuracy, and highlighting clinical mismatches.
    - [ ] Write unit tests for post-call batch evaluation.
- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)

## Phase 5: High-Fidelity Demo, Benchmarking, & Polish

- [ ] Task: Integrate and Polish Demo Application
    - [ ] Finalize the full features of `parallel_translate.py` CLI script, adding flags for `--target-lang`, `--provider`, `--mode`, and `--eval` (runs Phase 4 post-call evaluation).
    - [ ] Measure and log performance metrics (STT delay vs. Translation delay).
    - [ ] Run comparative benchmarks and document the results.
- [ ] Task: Conductor - User Manual Verification 'Phase 5' (Protocol in workflow.md)
