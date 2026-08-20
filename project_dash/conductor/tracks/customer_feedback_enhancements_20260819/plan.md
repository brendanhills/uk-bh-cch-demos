# Implementation Plan: Customer Feedback & Strategic Advisory Enhancements

## Phase 1: Terminology & Core Configuration Updates
- [ ] Task: Update Heading & Program Branding
  - [ ] Update `data/f-dse/config.json` title to "Future Defence Secret Environment"
  - [ ] Verify header rendering, tab titles, and export configurations reflect "Future Defence Secret Environment"
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Risk Register Separation & Tab Architecture Clarification
- [ ] Task: Create Unit Tests for Multi-Register Tab Isolation
  - [ ] Add unit test verifying Internal Risks tab displays strictly the 107 primary risks
  - [ ] Add unit test verifying Team Google Risks tab displays strictly the 12 TG risks with distinct badges and provenance
- [ ] Task: Implement Clear Separate Tabs UI & Badging
  - [ ] Update Tab 2 label to "Internal Risks" with count badge (107) and descriptive subtitle/tooltip
  - [ ] Update Tab 3 label to "Team Google Risks" with count badge (12) and Google security shield icon
  - [ ] Update Risk Explorer and Matrix headers in each tab to avoid cross-register confusion
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

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
- [ ] Task: Write Tests for Persistent "Google Need-to-Know" Rendering
  - [ ] Verify presence of global `#googleNeedToKnowContainer` across all tab states
  - [ ] Test dynamic population of high-priority Google briefing items and dismiss/collapse behavior
- [ ] Task: Implement Global "Google Need-to-Know" UI & Logic
  - [ ] Add persistent top-level notification bar / accordion card above main navigation
  - [ ] Populate with dynamic Google-specific escalations, upcoming milestone alerts, and key decision deadlines
  - [ ] Add collapse/expand toggle and state persistence
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 5: "Looking Around the Corner" Predictive Insights Module
- [ ] Task: Write Tests for Executive Summary Horizon Advisory
  - [ ] Test computation of forward-looking signals (lead times, unassigned critical risks, upcoming contractual milestones)
  - [ ] Test rendering of the "Looking Around the Corner" advisory card in `#view-exec-briefing`
- [ ] Task: Implement "Looking Around the Corner" UI & Dynamic Synthesis
  - [ ] Add "Looking Around the Corner: 30-60 Day Horizon & Preemptive Actions" component to Executive Summary tab
  - [ ] Wire dynamic signal generators highlighting impending roadblocks, gate risks, and strategic advice
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 6: End-to-End Verification & Documentation
- [ ] Task: Full System Audit & Regression Testing
  - [ ] Run Pytest test suite and ensure all tests pass
  - [ ] Manually verify UI across desktop and mobile views
- [ ] Task: Update README.md and Documentation
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
