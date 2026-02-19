# Implementation Plan: Decoupled Multi-Channel Transcription Architecture

This plan implements a Producer-Consumer architecture to resolve race conditions between channels and enable word-level interleaving of monologues and interjections.

## Phase 1: Shared Infrastructure and Message Schema
Establish the foundation for decoupled communication between channel workers and the UI consumer.

- [ ] Task: Define Standardized Message Schema
    - [ ] Write unit tests for message serialization and validation
    - [ ] Implement `TranscriptionMessage` data class (including words, timestamps, finality, and VAD events)
- [ ] Task: Shared Async Queue Setup
    - [ ] Implement a centralized message broker using `asyncio.Queue`
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Shared Infrastructure' (Protocol in workflow.md)

## Phase 2: Mode A Producers (Raw Workers)
Implement the "Raw" workers that feed the centralized interleaving engine.

- [ ] Task: Implement `RawChannelWorker` Class
    - [ ] Write failing tests for raw streaming (immediate push to queue)
    - [ ] Implement worker to handle independent STT streams and push raw interims/finals/VAD events to the shared queue
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Mode A Producers' (Protocol in workflow.md)

## Phase 3: Mode A Interleaving Engine (Consumer)
Implement the core logic for reconstructing the global timeline and splitting monologues.

- [ ] Task: Global Stability Buffer
    - [ ] Write integration tests for chronological sorting across channels
    - [ ] Implement unified buffer that holds segments until the playhead progresses past them
- [ ] Task: Intra-Utterance Splitting Logic
    - [ ] Write unit tests for splitting a single API result into micro-segments based on external interjections
    - [ ] Implement word-level splitting and interleaving algorithm
- [ ] Task: VAD-Driven Synchronization
    - [ ] Implement refined "Active Blocking" logic with the 2s safety timeout and 0.5s overlap window
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Interleaving Engine' (Protocol in workflow.md)

## Phase 4: Advanced Multi-Column Concurrent UI
Upgrade the terminal interface to support simultaneous rendering of both speakers.

- [ ] Task: Cursor-Aware UI Renderer
    - [ ] Write tests for ANSI cursor management (moving between columns/lines)
    - [ ] Implement renderer that allows simultaneous "typing" drafts in multiple columns
- [ ] Task: Dynamic Reflow for Interleaved Monologues
    - [ ] Implement logic to "break" a previously printed draft or finalized line to insert a chronological interjection
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Multi-Column UI' (Protocol in workflow.md)

## Phase 5: Mode A Integration and Evaluation
Apply the new architecture to the primary demo and validate performance.

- [ ] Task: Update `two_channel_transcribe_v2.py` for Mode A
    - [ ] Refactor the main entry point to orchestrate the new Producer-Consumer components
- [ ] Task: Performance Tuning and Evaluation
    - [ ] Verify fix for "Monologue vs Interjection" race condition using `samples/0638.mp3`
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Mode A Integration' (Protocol in workflow.md)

## Phase 6: Mode B - Producer-Side Stabilization
Implement the alternative distributed logic for comparative evaluation.

- [ ] Task: Stabilized Channel Worker
    - [ ] Implement local stability buffer and gap-splitting within the worker
    - [ ] Ensure only "finalized" or "stable" segments are pushed to the queue
- [ ] Task: Mode Toggle and Final Integration
    - [ ] Add CLI flag to switch between Mode A (Consumer Sort) and Mode B (Producer Sort)
- [ ] Task: Conductor - User Manual Verification 'Phase 6: Mode B' (Protocol in workflow.md)
