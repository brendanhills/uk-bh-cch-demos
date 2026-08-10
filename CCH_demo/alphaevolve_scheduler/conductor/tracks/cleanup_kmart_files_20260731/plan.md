# Implementation Plan - Cleanup Legacy Kmart Files

This plan outlines the step-by-step tasks to clean up legacy Kmart retail supply-chain files from active project paths while ensuring full CCH demo integrity and preserving legacy Kmart files in `legacy_kmart/`.

## Phase 1: Pre-Removal Integrity Check
- [ ] Task: Run Baseline Test Suite & Verify Initial State
  - [ ] Execute `PYTHONPATH=. uv run python -m unittest discover -s experiment -p "test_*.py"` to confirm baseline test suite passes.
  - [ ] Verify existence of legacy copies in `legacy_kmart/data/`, `legacy_kmart/scripts/`, and `legacy_kmart/traces/`.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: File Removal & Git Untracking
- [ ] Task: Remove Redundant Kmart Files from `data/`
  - [ ] `git rm data/make_network.py`
  - [ ] `git rm data/network.json`
- [ ] Task: Remove Redundant Kmart Files from `scripts/`
  - [ ] `git rm scripts/reconstruct_candidate_routes.py`
  - [ ] `git rm scripts/setup_engine.sh`
  - [ ] `git rm scripts/simulate_trace.py`
- [ ] Task: Remove Redundant Kmart `traces/` Directory
  - [ ] `git rm -r traces/`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Post-Cleanup Verification & Validation
- [ ] Task: Verify CCH Demo Integrity & Test Suite
  - [ ] Re-run full test suite (`PYTHONPATH=. uv run python -m unittest discover -s experiment -p "test_*.py"`) to confirm 100% test pass.
  - [ ] Confirm no broken references or missing data files in active CCH dataset paths (`data/config.json`, `data/candidates_feed.jsonl`, etc.).
  - [ ] Verify `legacy_kmart/` directory contents remain intact.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
