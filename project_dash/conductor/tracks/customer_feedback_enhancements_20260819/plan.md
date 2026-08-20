# Implementation Plan: Customer Feedback & Strategic Advisory Enhancements

## Phase 1: Terminology & Core Configuration Updates
- [x] Task: Update Heading & Program Branding
  - [x] Update `data/f-dse/config.json` title to "Monaro" / "Project Monaro"
  - [x] Verify header rendering, tab titles, and export configurations reflect branding
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Risk Register Separation & Tab Architecture Clarification
- [x] Task: Create Unit Tests for Multi-Register Tab Isolation
  - [x] Add unit test verifying Internal Risks tab displays strictly the 107 primary risks
  - [x] Add unit test verifying Team Google Risks tab displays strictly the 12 TG risks with distinct badges and provenance
- [x] Task: Implement Clear Separate Tabs UI & Badging
  - [x] Update Tab 2 label to "Internal Risks" with count badge (107) and descriptive subtitle/tooltip
  - [x] Update Tab 3 label to "Issue Register" with count badge (25) positioned next to Internal Risks
  - [x] Update Tab 4 label to "Team Google Risks" with count badge (12) and Google security shield icon
  - [x] Standardize pill count badges across all tabs
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: CD1 Driver Tree Direct Risk Modal Deep-Linking
- [x] Task: Write Tests for Driver Tree Risk Link Actions
  - [x] Add test for single linked risk click triggering `openRiskModal(riskId)`
  - [x] Add test for multi-risk deliverable rendering individual clickable chips
- [x] Task: Implement Enhanced Driver Tree Risk Interactions
  - [x] Update `renderDriverTree()` to evaluate `linkedRisks`
  - [x] If 1 risk linked: attach direct `openRiskModal(linkedRisks[0].id)` handler
  - [x] If multiple risks linked: render discrete risk pill chips (`#ID`) with `openRiskModal(id)` plus an "Explore All" button
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Google Need to Know (NTK) Security Classification Banner
- [x] Task: Write Tests for Title Banner NTK Classification Badge
  - [x] Verify presence of header `#ntkClassificationBadge` with "Google Need to Know (NTK)"
- [x] Task: Implement Title Banner NTK Badge & Clean Up Blue Box
  - [x] Add `Google Need to Know (NTK)` classification badge to top title banner
  - [x] Remove bulky blue notification container
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 5: "Looking Around the Corner" Predictive Insights Module (Deferred to Later Phase)
- [ ] Task: Write Tests for Executive Summary Horizon Advisory (Deferred)
  - [ ] Test computation of forward-looking signals (lead times, unassigned critical risks, upcoming contractual milestones)
  - [ ] Test rendering of the "Looking Around the Corner" advisory card in `#view-exec-briefing`
- [ ] Task: Implement "Looking Around the Corner" UI & Dynamic Synthesis (Deferred)
  - [ ] Add "Looking Around the Corner: 30-60 Day Horizon & Preemptive Actions" component to Executive Summary tab
  - [ ] Wire dynamic signal generators highlighting impending roadblocks, gate risks, and strategic advice
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 6: End-to-End Verification & Documentation
- [x] Task: Full System Audit & Regression Testing
  - [x] Run Pytest test suite and ensure all 102 tests pass
  - [x] Verify zero uncommitted data leaks to GitHub
- [x] Task: Update README.md and Documentation
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
