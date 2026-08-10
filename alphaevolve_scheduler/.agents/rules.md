# Workspace Agent Rules & Protocol Guidelines

## 1. Scope-Aware Testing (UI vs. Backend)
- **UI/CSS Fixes**: For minor UI, CSS, layout, or popup formatting adjustments (such as editing `rch/index.html`):
  - Do **NOT** run full backend simulation or dataset test suites (e.g., `unittest discover experiment`).
  - Limit verification to direct visual/template checks or lightweight checks on the specific HTML file.

## 2. Circuit Breaker on Unrelated Failures & Side-Effects
- If a command or test produces unrelated side-effects (such as modifying `data/config.json`, changing generated traces, or failing due to backend environment mismatches), **STOP IMMEDIATELY**.
- Do **NOT** attempt to troubleshoot, refactor backend test suites, or regenerate data files unless explicitly instructed by the user.

## 4. Ground Truth Baseline Comparison for UI Diffing
- In evolution UI visualizations, candidate step mutations and tooltips must ALWAYS evaluate diffs against **Step 0 Baseline** (`EVOLUTION_DATA.traces[0]`) rather than intermediate search steps, unless explicitly instructed otherwise.
- Never mark a card as `Evolved` if its position, room, time, and staff assignment are identical to Step 0 Baseline.

## 5. Prevent Churn & Direct Root-Cause Focus
- Always inspect user-provided screenshots and exact DOM / data states FIRST before making code edits.
- Avoid multi-step speculative refactoring loops. Validate data structures (`patientId`, `demandId`, `id`) and state transitions directly to ensure fixes are precise, non-breaking, and immediate.

## 6. Minimal Surgical Edit & UI Feature Preservation Rule
- **Surgical Locality**: When fixing a specific UI logic bug (e.g., card tagging or tooltip text), modify ONLY the targeted inline condition. Do NOT attempt wide-ranging refactors of global helper functions, DOM manipulation loops, or event handlers.
- **Preserve Working UI**: Never perform blanket `git checkout` reverts without first preserving recent working UI styling (e.g., Bug #2 muted slate palette, 54px row height, urgency pills, monospace styling).
- **Sanity Check Triad**: Always verify before reporting complete:
  1. Grid cards render (no blank grid).
  2. Professional UI styling intact (muted slate + 54px height).
  3. Floating tooltip popups display complete diff details.

## 7. Gantt Timeline Alignment & Horizon Rule
- **Header Slot Alignment**: Timeline column headers in `.time-slot` must use `text-align: left; padding-left: 6px;` to position hour labels (`08:00`, `09:00`) directly over the left tick boundary line, precisely matching appointment block start percentages (`leftPct = ((startMins - START_MINUTES) / TOTAL_MINUTES) * 100`).
- **Overtime Horizon Extension**: Timeline grid headers and `TOTAL_MINUTES` calculations must extend through `21:00` (780 mins total) to ensure overtime surgeries scheduled past 20:00 fit cleanly within the Gantt grid container without spilling past the right border edge.

## 8. Disruption Re-Routing & Alternate Room Search Invariant
- When dynamically injecting maintenance blocks (`EVOLUTION_DATA.unavailability`), displaced/bumped surgeries must search alternate rooms (`rooms.filter(r => r !== randomRoom)`) for free slots using `findEmptySlot` rather than searching the closed room itself, avoiding overlapping block overlays.

## 9. Status-Aligned Color Coding & Delta Sign Preservation Rule
- **Status Colors**: Data points on evolution sparklines and candidate feed badges must align fill colors with candidate status:
  - Green (`#82C341` / `#10b981`) for `ACCEPTED`, `BASELINE`, `REPLANNED`, `UPDATED`.
  - Orange (`#F26322` / `#f59e0b`) for `DEGRADED`.
  - Red (`#DA1A31` / `#ef4444`) for `REJECTED`.
- **Metric Delta Direction**: Metric delta indicators (e.g., patient throughput gains `+4`) must render the delta direction matching the sign of `patientDiff` (`▲` for positive gains, `▼` for reductions) regardless of whether overall candidate status is `DEGRADED`.

## 10. Demo Mode User-Facing Messaging Standard
- In Demo Replay Mode, status messages must display user-friendly simulation text (`Simulating AlphaEvolve generating candidates... (generated=X, evaluated=Y/10, idle=Zs)`) while preserving live candidate counters and timers, rather than raw backend logger strings (`INFO alpha_evolve.controller...`).
