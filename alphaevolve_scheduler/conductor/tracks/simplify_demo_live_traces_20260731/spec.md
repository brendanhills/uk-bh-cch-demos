# Specification: 3-Phase Executive Storytelling & Simplified Trace Modes (`simplify_demo_live_traces`)

## 1. Overview
In this demo, the concepts of "Before" and "After" represent an interactive operational comparison rather than static software snapshots. Presenters need to guide audiences through a clear 3-Phase story:
- **Phase 1 (Before — Traditional Algorithm)**: Demonstrate how a traditional heuristic schedules surgeries over multiple weeks and struggles when responding to unplanned emergency disruptions.
- **Phase 2 (The AI Optimization — AlphaEvolve Evolution)**: Really use the AlphaEvolve API to progressively mutate and evolve the scheduling algorithm in real time (~45–60 seconds estimated duration), showing live candidate improvements.
- **Phase 3 (After — Evolved Algorithm)**: Reset the schedule to the initial conditions using the newly Evolved Algorithm, add weeks, and inject disruptions to prove the superior outcome.

Currently, `cch/index.html` mixes static historical trace datasets (`traces_med.jsonl`, `traces_high.jsonl`, `traces_low.jsonl`) and dynamic execution modes (`traces_dynamic.jsonl`, `mock_trace_replan.jsonl`) inside a single `Scenario:` dropdown, confusing presenters and audiences. Furthermore, the baseline First-Come-First-Served algorithm front-loads surgeries into Monday–Thursday, leaving Friday unrealistically sparse.

This track simplifies the demo by organizing the UI around the **3-Phase Executive Narrative**, making **Live AlphaEvolve Run** the default execution mode, consolidating pre-recorded traces into a single canonical showcase (`traces_low.jsonl`), archiving non-canonical traces, and updating the baseline heuristic so Friday has a realistic surgical caseload.

## 2. Functional Requirements
- **FR1: Interactive Presenter Changes in Phase 1 & Phase 3 (`cch/index.html`) — PRIMARY REQUIREMENT**
  - Enable presenters to make interactive changes (e.g., scheduling future weeks, stepping one week at a time, and injecting unplanned emergency disruptions) in both Phase 1 (Before) and Phase 3 (After) to directly demonstrate how the algorithm responds to them.
  - While labelling the 3 phases in the demo UI is helpful, ensuring responsive, interactive presenter controls in Phase 1 and Phase 3 is the core objective.
- **FR2: Real AlphaEvolve API Execution in Phase 2**
  - Phase 2 must really use the AlphaEvolve API (`/run-optimization` -> `experiment/run_evolution.py`), progressively evolving a better algorithm and streaming live candidates to the UI (~45–60s estimated API duration).
- **FR3: Clean Execution Mode Selector with Live Default (`cch/index.html`)**
  - Replace the confusing `Scenario:` dropdown with a clean **2-option Execution Mode Toggle**:
    - ⚡ **Live AlphaEvolve Run (DEFAULT)** — calls `/run-optimization` and streams live candidate updates from the AlphaEvolve API.
    - 🎬 **Demo Mode (Instant/Paced Replay)** — uses the canonical pre-recorded trace (`traces_low.jsonl`) as a backup for presentations without cloud access.
  - Hide `mock_trace_replan.jsonl` ("🧪 Fixture Mode") from main header controls, accessible only via a URL parameter (`?debug=1`) or debug toggle.
- **FR4: Canonical Trace Consolidation & Archiving**
  - Establish `traces_low.jsonl` ("Agile Constraints", `120 ➔ 125 patients`) as the single canonical pre-recorded demo trace.
  - Move non-canonical historical trace files (`traces_high.jsonl`, `traces_med.jsonl`) from `data/` into `data/archive/`.
- **FR5: Realistic Friday Baseline Caseload (`experiment/program.py`)**
  - Refine the baseline greedy scheduling heuristic in `experiment/program.py` so that patient surgeries are distributed evenly across Monday through Friday (avoiding empty Fridays).
  - Regenerate the canonical demo trace (`data/traces_low.jsonl`) so that Step 0 shows a realistic Friday caseload.
- **FR6: Documentation & Presenter Script Alignment**
  - Update `demo_script.md` and `README.md` to document the 3-Phase Executive Narrative, the default Live execution mode, and the interactive comparison of Phase 1 vs. Phase 3.

## 3. Non-Functional Requirements
- **NFR1: Responsive Interactive Demonstration**: In Phase 1 and Phase 3, injecting disruptions and stepping through weeks must reflect schedule changes immediately and clearly in the UI.

## 4. Acceptance Criteria
- [ ] Presenters can make interactive changes (adding weeks, injecting emergency disruptions) in Phase 1 and Phase 3 to show how the algorithm responds to them.
- [ ] Phase 2 really uses the AlphaEvolve API (`/run-optimization`), progressively improving over ~45–60s.
- [ ] A clean 2-option Execution Mode selector replaces the dropdown, with **Live AlphaEvolve Run** set as the **default**.
- [ ] The baseline schedule in the canonical trace shows a realistic Friday surgical caseload.
- [ ] `data/traces_high.jsonl` and `data/traces_med.jsonl` are moved to `data/archive/`.
- [ ] `demo_script.md` and `README.md` clearly document the 3-Phase Executive Narrative.

## 5. Out of Scope
- Changes to the underlying AlphaEvolve multi-objective scoring formula in `evaluator.py`.
- Modifications to the Google Cloud ADC authentication mechanism or `vendor/alphaevolve/` SDK.
