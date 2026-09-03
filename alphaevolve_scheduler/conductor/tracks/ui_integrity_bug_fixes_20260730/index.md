# Specification: RCH UI Visual & State Integrity Bug Fixes (#16, #21, #22, #23)

## 1. Overview
Dedicated maintenance track resolving UI visual, state-management, and layout clipping bugs reported in the RCH demo dashboard (`rch/index.html`) using the Adaptive Tiered Verification protocol (`/fix_bug`).

## 2. Scope of Fixes
- **Bug #16 (P3):** Neutralize hospital name to "Cymbal Children's Hospital" across `<title>` and `<header>`.
- **Bug #21 (P2):** Ensure switching scenarios resets `isEvolvedMode = false` and restores Baseline toggle button states.
- **Bug #22 (P2):** Style `#active-day-label` as a centered header badge without `"(Showing: ...)"` formatting.
- **Bug #23 (P2):** Expand `.staff-grid` CSS (`max-height: none; overflow-y: visible;`) to eliminate vertical scrolling and prevent clipping staff cards.

## 3. Success Criteria
- 100% automated reproduction unittests passing (`experiment/test_rch_html.py`).
- No regressions across existing 25 UI and heuristic regression tests.
