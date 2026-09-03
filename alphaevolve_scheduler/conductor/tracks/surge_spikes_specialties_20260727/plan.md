# Implementation Plan: Daily Surge Spikes, Specialized OT Room Constraints & 5-Day Live Demo

## Phase 1: 5-Day Data Model, Room Constraints & Trace Exporter Enhancements
- [x] Task: Add room suitability attributes and Monday trauma surge demands to generate_scenario.py across the 5-day horizon (160 patients, Mon–Fri)
- [x] Task: Add room suitability validation to experiment/evaluator.py
- [x] Task: Update scripts/generate_traces.py and experiment/program.py to embed baseline origin coordinates (`orig_day`, `orig_room`, `orig_time`, `orig_staff`) in Candidate Step 0
- [x] Task: Implement step-over-step delta tracking (`prev_day`, `prev_room`, `prev_time`, `mutation_reason`) in Candidate Step $N$ JSONL records
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Solver Heuristic, Backend Streaming & Dataset Regeneration
- [x] Task: Update experiment/program.py seed solver to handle room suitability and surge packing
- [x] Task: Regenerate config.json and recorded traces (`traces_low.jsonl`, `traces_med.jsonl`, `traces_high.jsonl`) with 5-day tracking and delta metadata
- [x] Task: Update `/run-optimization` endpoint in server.py and experiment/run_evolution.py to stream 5-day trace steps with speed multiplier controls (`1x`, `2x`, `5x`, `Instant`)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Interactive UI Dashboard & Dual-Level Hover Popup (`rch/index.html`)
- [x] Task: Add 5-Day Day Navigation Tabs (`Mon` | `Tue` | `Wed` | `Thu` | `Fri`) above the Gantt schedule grid, defaulting to Monday
- [x] Task: Update Executive Metrics Header (*Fatigue Violations*, *Patients Scheduled*, *Room Utilization*, *Overall Score*) to display cumulative 5-day totals
- [x] Task: Implement Dual-Level Hover-Over Popup on surgery cards (Baseline Step 0 vs. Latest Step $N$ delta + optimization rationale)
- [x] Task: Add 1.5s CSS Green Pulse Glow animation to surgery cards mutated in a newly loaded candidate step
- [x] Task: Add live code diff highlighting (green/red lines) and animated status banner (`⚡ AlphaEvolve Evolving: Candidate #N`) in the Active Logic drawer
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Automated Testing & End-to-End Verification
- [x] Task: Expand experiment/test_rch_html.py with unit tests for 5-day tab rendering, dual-level hover popup DOM structure, and trace metadata schema
- [x] Task: Run full test suite (`PYTHONPATH=. uv run python -m unittest discover experiment`) and verify 100% green pass rate
- [x] Task: Launch local web server (`./serve.sh 9000`) and verify interactive playback across all scenarios
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 5: Missing Feature Implementation & Bug Fixes (Bug #31)
- [ ] Task: Implement speed multiplier replay controls (`1x`, `2x`, `5x`, `Instant`) in `rch/index.html` and backend streaming.
- [ ] Task: Add 1.5s CSS Green Pulse Glow animation to surgery cards mutated in a newly loaded candidate step.
- [ ] Task: Ensure room suitability constraints (`OT_1` Hybrid Cardiac Suite, `OT_2` Robotic Suite) are strictly enforced in solver and evaluator.
- [ ] Task: Phase Verification & Checkpoint
