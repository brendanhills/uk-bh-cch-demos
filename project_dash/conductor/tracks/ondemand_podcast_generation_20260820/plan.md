# Implementation Plan: On-Demand Backend Podcast Generation

## Phase 1: Backend Endpoint & Multi-Speaker Audio Synthesis
- [ ] Task: Author unit tests for `POST /api/generate-podcast` endpoint in `tests/test_server.py`
  - [ ] Test endpoint request validation (missing project/week parameters)
  - [ ] Test successful response structure (`audioUrl`, `script`, `duration`)
  - [ ] Test snapshot update in `snapshots.json`
- [ ] Task: Implement `handle_generate_podcast` in `server.py`
  - [ ] Route `POST /api/generate-podcast`
  - [ ] Integrate with `scripts.gemini_generator.generate_multispeaker_podcast`
  - [ ] Persist generated audio assets and update `snapshots.json`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Frontend On-Demand Generation UX & Player Synchronization
- [ ] Task: Build interactive loading & generation state in `index.html`
  - [ ] Show `⏳ Generating high-fidelity podcast briefing for Week X...` banner in player
  - [ ] Add explicit "Regenerate Podcast 🎙️" button to transcript modal
- [ ] Task: Connect frontend player to `POST /api/generate-podcast`
  - [ ] Trigger on-demand generation when audio is missing
  - [ ] Seamlessly bind the newly generated audio source, update transcript, and begin playback
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Verification & Regression Testing
- [ ] Task: Run automated test suite (`pytest`) and verify 100% pass rate
- [ ] Task: Perform end-to-end verification across multiple reporting weeks
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
