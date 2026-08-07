# Implementation Plan: Simplify Dashboard (Single Unified View with URL-Driven A/B Testing)

## Phase 1: Immediate UI, Navigation & URL-Driven A/B Testing
- [x] Task: Make header title and logo clickable to return to Executive Summary home (FR #10) d43d892
- [x] Task: Update ATO-C Security Gate status text styling from emerald to amber (Bug #5) d43d892
- [x] Task: Implement URL query parameter detection (?view=pm / ?ledger=true) to dynamically reveal 5th Ledger tab for PM A/B testing without adding UI buttons d43d892
- [x] Task: Consolidate navigation bar: default to 4 core views in clean Executive Mode, dynamically expose Tab 5 when ?view=pm is present in URL d43d892
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Risk & Issue Cockpit Harmonization
- [ ] Task: Unify 5x5 Risk Heatmap and Issue Status into side-by-side cockpit overview (FR #14)
- [ ] Task: Reconcile 5x5 heatmap click-through with active visual focus ring and filter scroll (Bug #7)
- [ ] Task: Build unified Exception Explorer with 3-preset filter (All, Score ≥ 18, Eventuated) and progressive disclosure cap
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Dynamic Trends, Analytics & Time Travel
- [ ] Task: Fix Performance Trends burndown canvas sizing and multi-granularity dataset binding (Bug #8)
- [ ] Task: Parse multi-week Drive snapshots (W22–W26) for dynamic net risk velocity and burndown trajectories (FR #13)
- [ ] Task: Embed horizontal weekly scrubbing track in Time Machine banner (FR #9)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Enterprise Settings, Drive Management & Export Polish
- [ ] Task: Build human-readable Sheet & Drive Folder switcher with live connection validation (FR #16)
- [ ] Task: Add in-dashboard Gemini prompt editor tab with live token estimator in Settings modal (FR #6)
- [ ] Task: Implement client-side PDF export (jspdf/print) and structured slide generator (Bug #1)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 5: Verification & Delivery
- [ ] Task: Run end-to-end verification across both default (4-tab) and ?view=pm (5-tab) modes on localhost:9000
- [ ] Task: Update README.md and Resume.md with URL parameter documentation
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
