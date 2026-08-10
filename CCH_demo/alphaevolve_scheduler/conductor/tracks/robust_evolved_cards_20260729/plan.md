# Track Implementation Plan: Robust Evolved Cards Tagging

## Phase 1: Client-Side Diff Engine in `rch/index.html` (Live Dynamic Run)
- [x] Task: Add `getAppointmentDiff()` helper function in `rch/index.html` with patient ID normalization (`replace(/\D/g, "")`) and Step N-1 missing fallback.
- [x] Task: Update `renderCurrentStep()` in `rch/index.html` to build `prevStepMap` and apply `isEvolvedAdd` class dynamically.
- [x] Task: Update `showTooltip()` in `rch/index.html` to use `getAppointmentDiff()` for popup diff rows.
- [x] Task: Manual Verification — Launch `./serve.sh`, click "Play Live Run", and verify only mutated cards light up green with accurate hover diffs.
- [x] Task: Phase Verification & Checkpoint

## Phase 2: Static Dataset Generator Alignment (`scripts/generate_traces.py`)
- [x] Task: Update `make_incremental_step()` in `scripts/generate_traces.py` to preserve baseline positions and add non-overlapping breakthrough appointments.
- [x] Task: Regenerate static trace files (`traces_low.jsonl`, `traces_med.jsonl`, `traces_high.jsonl`).
- [x] Task: Manual Verification — Toggle between Agile Constraints, Standard Heuristic, and Legacy Manual scenarios in UI to verify incremental card tagging.
- [x] Task: Phase Verification & Checkpoint

## Phase 3: Bug Fixes (Bug #27)
- [ ] Task: Resolve Bug #27 — Ensure Evolved cards always display explicit diff details in tooltip (e.g. status change for newly scheduled breakthrough cases).
- [ ] Task: Phase Verification & Checkpoint
