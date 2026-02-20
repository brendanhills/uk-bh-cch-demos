# Implementation Plan: Decoupled Multi-Channel Transcription Architecture

This plan implements a Producer-Consumer architecture to resolve race conditions between channels and enable word-level interleaving of monologues and interjections.

## Phase 1: Shared Infrastructure and Message Schema
Establish the foundation for decoupled communication between channel workers and the UI consumer.

- [x] Task: Define Standardized Message Schema
    - [x] Implement `TranscriptionEvent` data class in `core/models.py` (including words, timestamps, finality, and VAD events)
- [x] Task: Shared Async Queue Setup
    - [x] Implement a centralized message broker pattern using `asyncio.Queue` in `core/utils.py`
- [x] Task: Conductor - User Manual Verification 'Phase 1: Shared Infrastructure'

## Phase 2: Mode A Producers (Raw Workers)
Implement the "Raw" workers that feed the centralized interleaving engine.

- [x] Task: Implement `RawChannelWorker` Class
    - [x] Implement `V2Provider` in `core/providers.py` to handle independent STT streams and push events to the engine.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Mode A Producers'

## Phase 3: Mode A Interleaving Engine (Consumer)
Implement the core logic for reconstructing the global timeline and splitting monologues.

- [x] Task: Global Stability Buffer
    - [x] Implement unified buffer in `TranscriptionEngine` (`core/engine.py`) that holds segments until the playhead progresses past them
- [ ] Task: Intra-Utterance Splitting Logic
    - [ ] Write unit tests for splitting a single API result into micro-segments based on external interjections
    - [ ] Implement word-level splitting and interleaving algorithm
- [x] Task: VAD-Driven Synchronization
    - [x] Implement refined "Active Blocking" logic in `TranscriptionEngine` with the 2s safety timeout.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Interleaving Engine'

## Phase 4: Advanced Multi-Column Concurrent UI
Upgrade the terminal interface to support simultaneous rendering of both speakers.

- [x] Task: Cursor-Aware UI Renderer
    - [x] Implement `TerminalSink` in `core/sinks.py` that allows simultaneous "typing" drafts in multiple columns using ANSI escapes.
- [ ] Task: Dynamic Reflow for Interleaved Monologues
    - [ ] Implement logic to "break" a previously printed draft or finalized line to insert a chronological interjection
- [x] Task: Conductor - User Manual Verification 'Phase 4: Multi-Column UI'

## Phase 5: Mode A Integration and Evaluation
Apply the new architecture to the primary demo and validate performance.

- [x] Task: Update `two_channel_transcribe_v2.py` for Mode A
    - [x] Refactor the main entry point to orchestrate the new Producer-Consumer components
- [x] Task: Create `parallel_transcribe.py` for true multi-stream handling.
- [ ] Task: Performance Tuning and Evaluation
    - [ ] Verify fix for "Monologue vs Interjection" race condition using `samples/0638.mp3`
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Mode A Integration'

## Phase 6: Mode B - Producer-Side Stabilization
Implement the alternative distributed logic for comparative evaluation.

- [ ] Task: Stabilized Channel Worker
    - [ ] Implement local stability buffer and gap-splitting within the worker
    - [ ] Ensure only "finalized" or "stable" segments are pushed to the queue
- [ ] Task: Mode Toggle and Final Integration
    - [ ] Add CLI flag to switch between Mode A (Consumer Sort) and Mode B (Producer Sort)
- [ ] Task: Conductor - User Manual Verification 'Phase 6: Mode B' (Protocol in workflow.md)
