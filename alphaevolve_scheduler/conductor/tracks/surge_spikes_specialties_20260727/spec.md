# Specification: Daily Surge Spikes, Specialized OT Room Constraints & 5-Day Live Demo

## Overview
Enhances the RCH AlphaEvolve co-scheduling demonstration with:
1. **Monday Morning ER Trauma Surge Spikes** (Priority 0 cases) and specialized equipment room constraints (`OT_1` Hybrid Cardiac Suite, `OT_2` Robotic Suite).
2. **5-Day Multi-Day Horizon (Mon–Fri, 160 patients)** across all 5 operating theatres with day-by-day tab navigation (`Mon` | `Tue` | `Wed` | `Thu` | `Fri`).
3. **Cumulative 5-Day Executive Metrics** aggregating fatigue violations, scheduled patients, room utilization, and fitness score across the full week.
4. **Real-Time Code Mutation & Candidate Visualization** displaying an animated status banner (`⚡ AlphaEvolve Evolving: Candidate #N`) and code diffs in the lower drawer.
5. **Dual-Level Hover-Over Popup on Surgery Cards** tracking step-over-step evolution deltas (`Step N-1 ➔ Step N`) and unoptimized baseline comparisons (`vs. Step 0`), along with optimization rationale.
6. **Accelerated Replay Speed Controls** (`1x`, `2x`, `5x`, `Instant`) for streaming trace replays.

## Functional Requirements
1. **Scenario Generator (`generate_scenario.py`)**:
   - Injects 4 Emergency (Priority 0) trauma cases arriving between 08:00 and 11:00 on Monday.
   - Assigns room suitability requirements to Cardiac procedures (`OT_1` Hybrid Cardiac Suite) and Robotic procedures (`OT_2` Robotic Surgery Suite).
   - Verifies full 5-day patient and staff scheduling (160 patients, Mon–Fri).
2. **Evaluator (`experiment/evaluator.py`) & Traces (`scripts/generate_traces.py`)**:
   - Treats room suitability as a strict hard constraint.
   - Embeds original baseline coordinates (`orig_day`, `orig_room`, `orig_time`, `orig_staff`) in Candidate Step 0.
   - Embeds step-over-step movement metadata (`prev_day`, `prev_room`, `prev_time`, `mutation_reason`) in Candidate Step $N$.
3. **Baseline Solver (`experiment/program.py`) & Backend (`server.py`)**:
   - Updates heuristic to respect room suitability constraints while prioritizing trauma surge cases.
   - Supports `/run-optimization` streaming across the 5-day horizon and speed multiplier replay.
4. **UI Dashboard (`rch/index.html`)**:
   - Renders 5-Day Day Navigation Tabs (`Mon` | `Tue` | `Wed` | `Thu` | `Fri`).
   - Updates Executive Metrics Header to cumulative 5-day totals.
   - Renders dual-level hover tooltips showing baseline vs. latest candidate deltas and rationale.
   - Applies 1.5s CSS green pulse glow on reassigned surgery cards when a new candidate loads.
   - Highlights heuristic code mutations in the Active Logic drawer.

## Acceptance Criteria
- Evaluator rejects schedules assigning robotic or cardiac surgeries to standard OTs.
- Baseline solver successfully schedules Monday trauma surge without causing overtime or room conflicts.
- Trace datasets (`traces_low.jsonl`, `traces_med.jsonl`, `traces_high.jsonl`) updated and verified across the 5-day horizon with origin and step-delta metadata.
- UI allows seamless tab switching between Mon–Fri, displaying cumulative metrics, pulse animations, and dual-level hover tooltips.
