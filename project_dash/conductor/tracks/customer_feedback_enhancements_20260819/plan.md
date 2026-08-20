# Implementation Plan: Customer Feedback & Strategic Advisory Enhancements

## Phase 1: Terminology & Core Configuration Updates
- [ ] Task: Update Heading & Program Branding
  - [ ] Update `data/f-dse/config.json` title to "Future Defence Secret Environment"
  - [ ] Verify header rendering, tab titles, and export configurations reflect "Future Defence Secret Environment"
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Risk Register Separation & Tab Architecture Clarification
- [x] Task: Create Unit Tests for Multi-Register Tab Isolation
  - [x] Add unit test verifying Internal Risks tab displays strictly the 107 primary risks
  - [x] Add unit test verifying Team Google Risks tab displays strictly the 12 TG risks with distinct badges and provenance
- [x] Task: Implement Clear Separate Tabs UI & Badging
  - [x] Update Tab 2 label to "Internal Risks" with count badge (107) and descriptive subtitle/tooltip
  - [x] Update Tab 3 label to "Team Google Risks" with count badge (12) and Google security shield icon
  - [x] Update Risk Explorer and Matrix headers in each tab to avoid cross-register confusion
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: CD1 Driver Tree Direct Risk Modal Deep-Linking
- [ ] Task: Write Tests for Driver Tree Risk Link Actions
  - [ ] Add test for single linked risk click triggering `openRiskModal(riskId)`
  - [ ] Add test for multi-risk deliverable rendering individual clickable chips
- [ ] Task: Implement Enhanced Driver Tree Risk Interactions
  - [ ] Update `renderDriverTree()` to evaluate `linkedRisks`
  - [ ] If 1 risk linked: attach direct `openRiskModal(linkedRisks[0].id)` handler
  - [ ] If multiple risks linked: render discrete risk pill chips (`#ID`) with `openRiskModal(id)` plus an "Explore All" button
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Persistent Global "Google Need-to-Know" Header Module
- [x] Task: Write Tests for Persistent "Google Need-to-Know" Rendering
  - [x] Verify presence of global `#googleNeedToKnowContainer` across all tab states
  - [x] Test dynamic population of high-priority Google briefing items and dismiss/collapse behavior
- [x] Task: Implement Global "Google Need-to-Know" UI & Logic
  - [x] Add persistent top-level notification bar / accordion card above main navigation
  - [x] Populate with dynamic Google-specific escalations, upcoming milestone alerts, and key decision deadlines
  - [x] Add collapse/expand toggle and state persistence
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 5: "Looking Around the Corner" Predictive Insights Module
- [x] Task: Write Tests for Executive Summary Horizon Advisory
  - [x] Test computation of forward-looking signals (lead times, unassigned critical risks, upcoming contractual milestones)
  - [x] Test rendering of the "Looking Around the Corner" advisory card in `#view-exec-briefing`
- [x] Task: Implement "Looking Around the Corner" UI & Dynamic Synthesis
  - [x] Add "Looking Around the Corner: 30-60 Day Horizon & Preemptive Actions" component to Executive Summary tab
  - [x] Wire dynamic signal generators highlighting impending roadblocks, gate risks, and strategic advice
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 6: End-to-End Verification & Documentation
- [x] Task: Full System Audit & Regression Testing
  - [x] Run Pytest test suite and ensure all tests pass
  - [x] Manually verify UI across desktop and mobile views
- [x] Task: Update README.md and Documentation
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
