# Track Implementation Plan: RCH UI Visual & State Integrity Bug Fixes (#16, #21, #22, #23)

## Phase 1: Adaptive Tiered UI Bug Fixes (`/fix_bug` Protocol)
- [x] Task: Fix Bug #16 — Hospital Name Neutralization ("Cymbal Children's Hospital") in `<title>` and `<header>` with reproduction unit test.
- [x] Task: Fix Bug #21 — Reset `isEvolvedMode = false` and toggle button states when selecting a new scenario with reproduction unit test.
- [x] Task: Fix Bug #22 — Style `#active-day-label` as centered header badge without `"(Showing: ...)"` formatting with reproduction unit test.
- [x] Task: Fix Bug #23 — Change `.staff-grid` CSS to `max-height: none; overflow-y: visible;` so details are never hidden with reproduction unit test.
- [x] Task: Verify 29/29 regression and reproduction tests pass cleanly.
- [x] Task: Phase Verification & Checkpoint

## Phase: Review Fixes
- [x] Task: Apply review suggestions aea3aaf
