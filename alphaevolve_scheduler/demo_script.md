# Executive Demo Script & Talking Points: RCH AlphaEvolve Co-Scheduling

This document provides presenter guidance, executive talking points, and scenario explanations for demonstrating the **AlphaEvolve Operational Theatre (OT) Co-Scheduling System** using the **3-Phase Executive Narrative**.

---

## 1. The 3-Phase Executive Narrative: Why "Before & After" is Different in AlphaEvolve

In this demonstration, the concepts of **"Before"** and **"After"** represent an interactive operational comparison rather than static software screenshots:

1. **Phase 1: Traditional Algorithm (Before)**
   - Demonstrates how a hospital schedules complex weekly procedures and responds to unplanned emergency changes using a traditional First-Come-First-Served heuristic algorithm.
   - Presenters interactively step through future weeks (`+ Advance Week`) and inject unplanned changes (`Simulate Emergency Arrival` / `Simulate OT Disruption`) to highlight fragmented idle gaps, staff fatigue violations, and disruption bottlenecks.
2. **Phase 2: AlphaEvolve Algorithm Evolution**
   - Demonstrates AlphaEvolve progressively mutating and evaluating candidate Python scheduling algorithms in real time (~45–60 seconds estimated duration).
   - Shows live candidate improvements as AlphaEvolve optimizes against all 4 hospital priorities simultaneously.
3. **Phase 3: Evolved Algorithm (After)**
   - Resets the schedule back to Week 1 using the newly Evolved Algorithm.
   - Presenters add weeks and inject the exact same unplanned disruptions as in Phase 1—visually proving that the Evolved Algorithm produces a superior operational outcome (higher throughput, fewer idle gaps, zero cancellations).

---

## 2. The 2 Execution Modes: Live Default vs. Demo Replay

The header controls feature a clean 2-option **Mode Selector**:

* **⚡ Live AlphaEvolve Run (DEFAULT MODE)**:
  - Invokes the Google Cloud AlphaEvolve API (`/run-optimization` -> `experiment/run_evolution.py`) to evolve algorithms and stream candidate steps in real time (~45–60 seconds).
* **🎬 Demo Mode (Paced Replay)**:
  - Replays the canonical pre-recorded trace (`data/traces_low.jsonl`) over ~45 seconds as a reliable backup for presentations without cloud access.
  - *Note: Non-canonical historical traces (`traces_high.jsonl`, `traces_med.jsonl`) are preserved in `data/archive/` for offline reference. Fixture Mode (`mock_trace_replan.jsonl`) is hidden unless the `?debug=1` URL parameter is active.*

---

## 3. Live Demonstration Talking Script (3 Phases)

### Phase 1: Presenting the Traditional Algorithm (Before)
* **Step 1: The Baseline Week 1 Schedule**
  - *Action*: Ensure **1️⃣ Phase 1: Traditional Before** is active.
  - *Script*: *"Here on the main schedule grid, we see our baseline schedule across 5 operating theatres and 16 clinicians. Notice how traditional First-Come-First-Served rules create fragmented idle gaps across rooms."*
* **Step 2: Interactively Stepping Into Future Weeks**
  - *Action*: Click **`+ Advance Week`** once or twice.
  - *Script*: *"As we advance into Week 2 and Week 3, notice how weekly workload variations cause traditional rules to break down, generating overtime warnings and inefficient room packing."*
* **Step 3: Injecting Unplanned Emergency Disruptions**
  - *Action*: Click **`Simulate Emergency Arrival`** or **`Simulate OT Disruption`**.
  - *Script*: *"When an unplanned emergency trauma case arrives, the traditional algorithm struggles to re-route surgeries without triggering staff fatigue violations or cancellations."*

---

### Phase 2: Running AlphaEvolve Algorithm Evolution
* **Step 4: Triggering Real-Time Algorithmic Search**
  - *Action*: Click **`2️⃣ Phase 2: Evolve Algorithm ▶`**.
  - *Script*: *"Now let's trigger Google AlphaEvolve. Over the next ~45 to 60 seconds, AlphaEvolve's Gemini ensemble mutates the underlying Python scheduling code."*
* **Step 5: Explaining Candidate Improvements**
  - *Script*: *"Watch as new candidate algorithms are evaluated live against our 4 hospital priorities: Patient Urgency, Staff Rest, Room Utilization, and Overtime Control. Notice the throughput jumping from 122 to 126 surgeries."*

---

### Phase 3: Presenting the Evolved Algorithm (After)
* **Step 6: Resetting & Proving Superior Baseline Performance**
  - *Action*: Click **`3️⃣ Phase 3: Evolved After`**.
  - *Script*: *"Now in Phase 3, we reset the schedule back to Week 1—but running under AlphaEvolve's Evolved Algorithm. Look at the schedule grid: zero idle gaps and a realistic caseload across all 5 days of the week."*
* **Step 7: Proving Resilience Across Future Weeks & Disruptions**
  - *Action*: Click **`+ Advance Week`** and **`Simulate Emergency Arrival`** / **`Simulate OT Disruption`**.
  - *Script*: *"When we advance weeks and inject the exact same emergency trauma cases that caused bottlenecks in Phase 1, the Evolved Algorithm dynamically re-routes procedures into open slots—maintaining 125+ surgeries with zero staff fatigue violations and zero cancellations."*

---

## 4. Metrics & The Executive Optimization Formula

Every candidate schedule evaluated by AlphaEvolve receives an overall performance score:

$$\text{Overall Score} = \text{Patient Urgency Points} - \text{Fatigue Penalties} - \text{Idle Room Penalties} - \text{Overtime Penalties}$$

* **Patient Urgency Points**: Rewards completing surgeries prioritized by clinical urgency (Emergency Trauma > Urgent Surgery > Routine Elective).
* **Fatigue Penalties**: Subtracts points if clinician shifts exceed 8 hours per day or breach 12-hour overnight rest windows.
* **Idle Room Penalties**: Subtracts points for fragmented, unusable operating theatre time gaps.
* **Overtime Penalties**: Subtracts points for surgeries extending past the 20:00 closing time.
