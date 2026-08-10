# Specification: Baseline vs. Evolved Algorithm Disruption Comparison Track

## Overview
Enhances the Cymbal Children's Hospital (CCH) 3-Phase Executive Storytelling workflow to demonstrate the hypothesis that the Evolved Algorithm handles unplanned disruptions (OT Closure, Emergency Arrival, Sick Call) significantly better than the Traditional Baseline Heuristic.

In Phase 1 (Baseline), injecting disruptions uses naive greedy placement, leading to higher idle time, staff overtime, or fatigue breaches. In Phase 3 (Evolved Algorithm), injecting the SAME disruptions triggers the Evolved algorithm re-planning strategy, preserving patient capacity (+X surgeries), eliminating fatigue breaches, and keeping overtime to 0.0h.

## Functional Requirements
1. **Phase-Aware Disruption Handling**:
   - Update disruption button handlers (`#btn-inject-ot`, `#btn-inject-er`, `#btn-inject-sick`) in `cch/index.html` to evaluate `activeStoryPhase`.
   - **Phase 1 (Baseline)**: Apply greedy heuristic re-routing. Trace insight title: `📋 OT Maintenance / Sick Call (Traditional Baseline)`. Metrics reflect unoptimized recovery (e.g. +1.5h overtime, 3 fatigue breaches).
   - **Phase 3 (Evolved Algorithm)**: Apply evolved heuristic re-routing. Trace insight title: `⚡ Dynamic Evolved Re-Plan: Maintenance / Sick Call (Evolved Algorithm)`. Metrics reflect optimized recovery (0.0h overtime, 0 fatigue breaches, +2 capacity gain).
2. **Presenter Comparison Badge & Tooltip**:
   - Add a green presenter comparison badge (`Evolved Algorithm Disruption Resilience: +X Surgeries Preserved | 0 Fatigue Breaches`) to the disruption notification banner in Phase 3.
   - Expand candidate hover tooltips to show side-by-side metric diff (Baseline Disruption vs. Evolved Disruption).
3. **Metric Card Highlights**:
   - Highlight metric cards (Patients Scheduled, Overtime, Fatigue Violations) with green glow in Phase 3 to emphasize algorithm superiority under disruption.

## Non-Functional Requirements
- Instant client-side response (< 1s recalculation in Demo Mode).
- Preserves CCH slate color branding, 54px Gantt row height, and responsive grid layout.

## Acceptance Criteria
- Injecting a disruption in Phase 1 demonstrates baseline heuristic degradation (overtime or fatigue breaches).
- Injecting the same disruption in Phase 3 demonstrates superior evolved algorithm recovery (zero fatigue breaches, maximum patient throughput preserved).
- Automated unit test suite verifies phase-aware disruption handling and metric diff calculations.

## Out of Scope
- Modifying underlying backend Python solver binaries.
