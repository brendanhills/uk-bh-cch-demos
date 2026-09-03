# Track Implementation Plan: Contract-First UX/Logic Decoupling & Candidate Exploration Feed

## Phase 1: Contract Schemas & Mock Fixtures (UX Decoupling)
- [x] Task: Create `data/config.schema.json` supporting staff `specialty` & `skills`, demand `requiredTeam`, and `disruptions`.
- [x] Task: Create `data/trace.schema.json` supporting unified step traces (`step`, `metrics`, `schedules`, `code`, `insight`, `initialSchedule`, and `replannedSchedule`).
- [x] Task: Create static fixtures (`fixtures/mock_config_specialists.json`, `fixtures/mock_trace_replan.jsonl`, `fixtures/mock_candidates_feed.jsonl`).
- [x] Task: Update `rch/index.html` to support `🧪 Fixture Mode (Mock Re-Plan)` without running the backend.
- [x] Task: Write automated contract schema verification test suite (`experiment/test_contract_schemas.py`).
- [x] Task: Phase Verification & Checkpoint

## Phase 2: Candidate Exploration Feed (3 Logging Destinations)
- [x] Task: Create live manual validation runner `scripts/simulate_live_backend_update.py` emitting candidate steps to STDOUT, `data/candidates_feed.jsonl`, and `data/traces_dynamic.jsonl`.
- [x] Task: Add interactive **Candidate Feed** tab in `rch/index.html` displaying mutation title, generation, status badge, score, metrics, and AlphaEvolve "Why Better / Worse" summary.
- [x] Task: Add comprehensive **Detailed Operational Scenario & Clinical Co-Scheduling Scope Panel** to the **Scenario Breakdown** tab in `rch/index.html`.
- [x] Task: Display explicit backlog ratio (`122 / 160 Patients`) on the main KPI metric card.
- [x] Task: Phase Verification & Checkpoint

## Phase: Review Fixes
- [x] Task: Apply review suggestions aea3aaf
