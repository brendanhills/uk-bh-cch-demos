# Implementation Plan: Simplify Dashboard (Single Unified View)

## Phase 1: Immediate UI & Navigation Consolidation
- [ ] Task: Make header title and logo clickable to return to Executive Summary home (FR #10)
- [ ] Task: Update ATO-C Security Gate status text styling from emerald to amber (Bug #5)
- [ ] Task: Consolidate top navigation bar from 6 tabs down to 4 streamlined core tabs (Executive Summary, Risk & Issue Cockpit, Trends, Driver Tree)
- [ ] Task: Remove standalone Ledger tab and embed direct Google Sheet deep links
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
- [ ] Task: Run end-to-end verification across all 4 unified tabs on localhost:9000
- [ ] Task: Update README.md and Resume.md with simplified architecture
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
