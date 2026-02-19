# Specification: Decoupled Multi-Channel Transcription Architecture

## Overview
Refactor the transcription engine to a Producer-Consumer pattern to solve the "Monologue vs. Interjection" race condition and enable sequential interleaving. This architecture ensures that conversations are rendered in their true sequential order by splitting long monologues around interjections from other channels based on high-precision timestamps. It also provides a configurable stabilization engine to compare centralized vs. distributed synchronization strategies.

## Functional Requirements
1. **Independent Channel Workers (Producers):**
    - Separate `asyncio` tasks for each channel to ensure independent API streaming.
    - Optimized to push data to the queue with minimal overhead.
2. **Configurable Stabilization Engine:**
    - **Mode A: Consumer-Side (Global Interleaving):** Producers send raw interims and VAD events immediately. The Consumer uses word-level timestamps to **split monologues** around interjections from other channels, reconstructing the global timeline in true chronological order.
    - **Mode B: Producer-Side (Local Stabilization):** Each worker manages its own stability buffer and gap-splitting. Only "stable" results are sent to the queue. The Consumer renders results immediately upon arrival.
3. **Sequential Interleaving Logic (Active in Mode A):**
    - **Intra-Utterance Splitting:** Use word-level timestamps (or punctuation fallbacks) to split long monologues into sub-segments if an interjection occurred during its timeframe.
    - **Timeline Reconstruction:** Maintain a global timeline and interleave micro-segments from all channels.
4. **Advanced Concurrent UI:**
    - Use ANSI cursor management to allow both speakers to "type" their interims simultaneously.
    - **Dynamic Reflow:** Ensure that when a monologue is split by an interjection, the terminal reflects the "turn-taking" flow accurately.
5. **Standardized Message Schema:**
    - `channel_id`, `start_sec`, `end_sec`, `text`, `is_final`, `event_type`, and `words`.

## Acceptance Criteria
- [ ] A CLI flag toggles between "Consumer" and "Producer" stabilization modes.
- [ ] **Mode A Success:** If Speaker B says "Mhm" mid-way through Speaker A's sentence, the "Mhm" appears *between* the split parts of Speaker A's sentence.
- [ ] **Mode B Success:** Utterances are printed as they are finalized by the independent workers, without consumer-side re-ordering.
- [ ] Simultaneous Interims: The UI shows "typing" feedback for both speakers concurrently in both modes.

## Out of Scope
- External message brokers (Pub/Sub).
- Multi-processing (OS processes).
