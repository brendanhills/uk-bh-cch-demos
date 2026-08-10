# Track Specification: Robust Evolved Cards Tagging

## Overview
Ensure surgery cards in the RCH timeline view (`rch/index.html`) are tagged with the green `Evolved` badge pill and pulse border **if and only if** they mutated (position moved, staff reassigned, or newly scheduled breakthrough) between Step N-1 and Step N.

## Functional Requirements
- **Phase 1 (Live Dynamic Run)**:
  - Implement a pure client-side diff engine (`getAppointmentDiff`) in `rch/index.html`.
  - Compare Step N appointments against Step N-1 appointments in memory using patient ID lookup (`normId = String(pid).replace(/\D/g, "")`).
  - Compute 4 core diff attributes: Day, Room (resourceId), Time (startTime), and Staff (staffIds).
  - Tag cards green ONLY when `isEvolved === true`. Default to 0 green cards if Step N-1 is missing.
  - Synchronize floating hover tooltip popup to render exact `Prev` vs `Now` diff rows when `isEvolved === true`.
- **Phase 2 (Static Dataset Generator Alignment)**:
  - Update `scripts/generate_traces.py` to ensure static trace files (`traces_low.jsonl`, `traces_med.jsonl`, `traces_high.jsonl`) generate stable incremental steps without global schedule reshuffling.

## Acceptance Criteria
1. Switching to Step 0 (Baseline) displays 0 green `Evolved` cards.
2. Triggering Live Run / Step 1 displays green `Evolved` badges **only** on appointments that actually mutated or were newly added.
3. Hovering over an `Evolved` card renders exact `Prev` vs `Now` diffs in the popup.
