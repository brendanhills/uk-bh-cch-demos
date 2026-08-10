# Implementation Plan: Staff Unavailable Disruption Track

## Phase 1: Test Suite & Disruption Logic
- [ ] Task: Add reproduction & validation unit tests in `experiment/test_cch_html.py`
  - [ ] Add `test_bug_staff_unavailable_disruption_button` to assert `#btn-inject-sick` exists in UI
  - [ ] Add `test_staff_unavailable_recalculation` to verify sick staff call handling, specialist skill matching, and surgery re-routing
- [ ] Task: Phase 1 Verification & Checkpoint

## Phase 2: UI Button & Disruption Engine Implementation
- [ ] Task: Add `#btn-inject-sick` button to the executive toolbar in `cch/index.html`
- [ ] Task: Implement `injectStaffUnavailableDisruption()` logic in `cch/index.html`
  - [ ] Select random working staff member on `activeDay`
  - [ ] Re-assign qualified staff with matching specialist skill or re-route affected surgeries
  - [ ] Append new trace step and render updated Gantt grid and staff roster
- [ ] Task: Phase 2 Verification & Checkpoint

## Phase 3: Integration & Final Verification
- [ ] Task: Run full unit test suite (`PYTHONPATH=experiment:. uv run python -m unittest discover -s experiment -p "test_*.py"`)
- [ ] Task: Phase 3 Verification & Checkpoint
