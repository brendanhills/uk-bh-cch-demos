# Implementation Plan: Baseline vs. Evolved Algorithm Disruption Comparison Track

## Phase 1: Test Suite & Disruption Engine Decoupling
- [ ] Task: Add reproduction & validation unit tests in `experiment/test_cch_html.py`
  - [ ] Add `test_phase1_vs_phase3_disruption_handling` to assert Phase 1 uses baseline re-routing and Phase 3 uses evolved re-routing
  - [ ] Add `test_phase3_disruption_comparison_badge` to verify Phase 3 presenter comparison badge text
- [ ] Task: Phase 1 Verification & Checkpoint

## Phase 2: Phase-Aware Disruption Engine & Visual Comparison UI
- [ ] Task: Update `btnInjectOt`, `btnInjectEr`, and `btnInjectSick` handlers in `cch/index.html` to branch on `activeStoryPhase`
  - [ ] Phase 1 logic: generate naive baseline re-plan trace step
  - [ ] Phase 3 logic: generate optimized evolved re-plan trace step
- [ ] Task: Add green presenter comparison badge and metric card highlights in `cch/index.html`
- [ ] Task: Update candidate hover tooltips to display side-by-side metric diff (Baseline vs. Evolved disruption handling)
- [ ] Task: Phase 2 Verification & Checkpoint

## Phase 3: Integration & Final Verification
- [ ] Task: Run full unit test suite (`PYTHONPATH=experiment:. uv run python -m unittest discover -s experiment -p "test_*.py"`)
- [ ] Task: Phase 3 Verification & Checkpoint
