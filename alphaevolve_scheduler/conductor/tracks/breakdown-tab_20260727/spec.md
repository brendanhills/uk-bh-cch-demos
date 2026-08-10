# Track Specification: Before/After Operational Comparison Tab

## 1. Overview
A new "Scenario Breakdown" Toggle/Tab will be seamlessly added to the RCH Resource & Staff Co-Scheduling UI exactly right next to the Operational Scenario dropdown. It will instantly present exactly the mathematical combinatorial challenge of the scenario (Before) and exactly how AlphaEvolve broke through it (After) using beautiful data visualizations and rich narrative summaries to deliver exactly that "Wow" factor for hospital executives.

## 2. Functional Requirements
- **UI Tab Toggle:** Add a beautifully styled "Breakdown" Tab next to exactly the Scenario dropdown at the top of the dashboard.
- **Content Injection:** When exactly clicked, gracefully hide the Gantt chart and dynamically show the Comparison Tab content instantly.
- **Static & Instant Data Loading:** Read exactly the total Demands, Resources, Staff, and baseline vs optimal step metrics statically on page load directly from exactly `data/config.json` and exactly `data/traces_low.jsonl`.
- **Rich Data Visualizations:**
 - **Supply vs Demand Chart:** A beautiful Bar Chart comparing exactly the **60hr total room supply vs exactly the 92hr total surgery demand** perfectly.
 - **Throughput Comparison:** A Big Metric Card and Bar exactly comparing Step 0 (**27 patients**) vs Step 1 (**29 patients**).
- **Narrative Stat-List:** A bulleted, beautifully explained text section outlining exactly the 10-hour rest constraints, staffing bottlenecks, and exactly how the AI achieved the breakthrough.

## 3. Non-Functional Requirements
- **Performance:** Instant, zero-lag tab transitions (Static & Instant execution).
- **Responsiveness:** Maintain exactly absolute UI fidelity on both laptop and exactly standard demo screen resolutions.
- **Design System:** Use exactly exactly the same Tailwind/HTML aesthetic as exactly exactly the existing RCH dashboard.

## 4. Acceptance Criteria
- [ ] Operational Scenario dropdown remains functional and properly updates exactly exactly the loaded data in the Tab on exactly change.
- [ ] Toggling to "Breakdown" Tab hides the Gantt chart and exactly shows the comparison metrics seamlessly.
- [ ] Supply vs Demand bar exactly renders 60 vs 92 correctly perfectly.
- [ ] Throughput metrics correctly read and precisely render exactly 27 vs 29 perfectly.
- [ ] Toggling back to "Gantt" perfectly restores exactly the original metrics and charts instantly exactly.

## 5. Out of Scope
- Real-time websocket streaming updates exactly on the Breakdown tab; exactly exactly exactly strictly static and instant exactly exactly for this fast-forward demo!
