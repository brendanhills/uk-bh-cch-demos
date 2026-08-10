# Cymbal Children's Hospital (CCH) Co-Scheduling × AlphaEvolve Demo

A self-contained, interactive enterprise prototype demonstrating how **Google AlphaEvolve** (the evolutionary coding agent on Gemini Enterprise) autonomously optimizes complex hospital resource and surgical staff co-scheduling.

**The story in one line:** We gave AlphaEvolve a baseline heuristic algorithm for **Cymbal Children's Hospital** (5 Operating Theatres, 16 clinical staff, 130+ patient surgery demands) — AlphaEvolve's Gemini ensemble (`gemini-3.5-flash`) mutated the Python algorithm live, increasing patient surgery throughput from **122 to 152 patients**, eliminating idle gap time, and minimizing staff fatigue breaches.

---

## 🚀 Running the Demo

### 1. Prerequisites & Quick Start
- **Python 3.10+** and **`uv`** package manager.
- **Install dependencies:**
  ```bash
  uv sync
  ```
- **Launch local server:**
  ```bash
  ./serve.sh 9000
  ```
  *(Optionally set port or model, e.g., `./serve.sh 9000 gemini-3.5-flash`)*
- **Open Dashboard:** Navigate to **`http://localhost:9000/cch/`** in your browser.

---

### 2. Execution Modes
Select the mode via the dashboard header **Mode Selector**:

- **🎬 Demo Mode (Default Paced Replay):**
  - Streams a pre-recorded canonical evolutionary trace (`data/traces_low.jsonl`) over ~45 seconds.
  - **No API key or Google Cloud setup required.** Ideal for presentations and offline walkthroughs.
- **⚡ Live AlphaEvolve Run:**
  - Connects to Google Cloud AlphaEvolve (`experiment/run_evolution.py`) to mutate Python code and evaluate candidates live via Gemini (`gemini-3.5-flash`).
  - Requires Google Cloud authentication (`gcloud auth login` or credentials/API key configured in `.env`).

---

### 3. 🎬 3-Phase Presentation Workflow

#### **Phase 1: Traditional Algorithm (Before)**
1. Ensure **`1️⃣ Phase 1: Traditional Before`** is selected.
2. Inspect the baseline weekly schedule across 5 Operating Theatres and 16 clinicians—noticing fragmented idle room gaps and greedy heuristic bottlenecks.
3. Click **`+ Advance Week`** to step through future weekly workload variations.
4. Click **`Simulate Emergency Arrival`** or **`Simulate OT Disruption`** to demonstrate how traditional rules trigger fatigue breaches and surgical bottlenecks under unplanned disruptions.

#### **Phase 2: AlphaEvolve Algorithm Evolution**
1. Click **`2️⃣ Phase 2: Evolve Algorithm ▶`**.
2. Watch AlphaEvolve's Gemini ensemble mutate and evaluate candidate Python scheduling algorithms in real time (or replayed stream).
3. Observe live candidate metrics jump from **122 to 152 surgeries** as the algorithm optimizes patient urgency, room utilization, overtime, and fatigue rules.

#### **Phase 3: Evolved Algorithm (After)**
1. Click **`3️⃣ Phase 3: Evolved After`**.
2. The schedule resets to Week 1 running under the winning Evolved Algorithm—showing zero idle gaps and packed surgical capacity.
3. Click **`+ Advance Week`** and inject the exact same emergency/disruption events used in Phase 1 to prove operational resilience (**152 surgeries**, zero cancellations, zero fatigue violations).

---

## 📁 Repository Structure

| Path | Purpose |
|---|---|
| `cch/index.html` | Interactive CCH dashboard featuring 3-Phase Storytelling controls, Mode selector, Schedule Grid, and Candidate Feed |
| `experiment/program.py` | Seed program; only code between `# EVOLVE-BLOCK-START` and `# EVOLVE-BLOCK-END` is mutated by AlphaEvolve |
| `experiment/evaluator.py` | Multi-objective evaluator measuring patient throughput, OT idle time, overtime, and staff rest break violations |
| `experiment/instructions.md` | Problem description and domain constraints sent to AlphaEvolve |
| `experiment/run_evolution.py` | Drives the live evolutionary search loop via the Discovery Engine client (`gemini-3.5-flash`) |
| `experiment/config.py` | Hospital data model loader (resources, clinical staff, patient demands, heuristics) |
| `fixtures/mock_trace_replan.jsonl` | Canonical evaluated trace JSONL feed for presentation Demo Mode |
| `fixtures/mock_candidates_feed.jsonl` | Canonical candidate feed JSONL records for presentation Demo Mode |

---

## 🧬 AlphaEvolve Architectural Approach & Best Practices

Our implementation follows the official Google Cloud AlphaEvolve Developer Guides to maximize search quality, evaluation speed, and generalization while preventing reward hacking:

### 1. 🎯 Search Space Definition & `EVOLVE-BLOCK` Placement
- **Tight `EVOLVE-BLOCK` Scope:** The `# EVOLVE-BLOCK-START` and `# EVOLVE-BLOCK-END` markers strictly bound the mutable decision algorithm (`build_schedule`). Non-negotiable domain rules (e.g. `is_staff_qualified`, `is_interval_free`, `str_to_mins`) live outside the block as immutable helper functions.
- **No Hardcoded Data:** Zero hospital demands, patient IDs, or staff rosters exist in `program.py`. The program remains concise (<165 lines) so the Gemini ensemble (`gemini-3.5-flash`) focuses 100% of its attention on algorithm heuristic optimization.
- **Immutable Entrypoint Contract:** The immutable `solve(config)` contract receives dynamic hospital configurations and returns deterministic appointment lists.

### 2. 🧮 Multi-Objective Normalized Fitness Function
The evaluator computes a balanced scalar fitness score preventing single-metric domination:
$$\text{Fitness Score} = \text{PriorityScore} - (\text{IdleHours} \times 10.0) - (\text{OvertimeHours} \times 50.0) - (\text{FatigueViolations} \times 75.0)$$
- **Patient Throughput Weighting:** Emergency surgeries (P0: $+1,000$), Urgent (P1: $+300$), Routine (P2: $+100$).
- **Non-Linear Penalty Weighting:** Penalties for rest break breaches and overtime scale non-linearly to prevent greedy metric hacking.

### 3. 🛡️ 4-Pillar Reward Hacking Defense
- **AST Security Pre-Validation (`validate_ast_security`):** Before executing candidate code, the AST is inspected for forbidden primitives (`sys._getframe`, `os`, `subprocess`, `inspect`, `eval`, `exec`). Any attempt to monkey-patch stack frames or tamper with evaluation files is immediately rejected.
- **Multi-Scenario Benchmark Evaluation:** Each mutated candidate algorithm is evaluated across **3 concurrent benchmark scenarios** (Standard Horizon, Staff Shortage where `S1` and `N1` are absent, and `OT_1` Thursday Maintenance). Hardcoded lookup tables fail on Scenarios B and C.
- **Soft Gradient Signals:** Programs with partial constraint violations receive soft penalty signals (`FAIL_SCORE / 2.0`) instead of hard binary dropouts, enabling smooth hill-climbing toward feasibility.
- **Namespace Scope Isolation:** Candidate code executes inside an isolated dictionary scope (`exec(candidate_code, ns)`), keeping evaluator logic and scoring weights hidden.

### 4. 💬 Granular Diagnostic Insights (`insights` Array)
The evaluator returns structured diagnostic feedback arrays (`patients_scheduled`, `fatigue_violations`, `idle_time`, `overtime`) for each benchmark scenario. AlphaEvolve injects these insights directly into the Gemini prompt context for targeted bottleneck resolution in subsequent generations.

### 5. ⚡ Concurrency & Parallel Execution
- **Sweet-Spot Concurrency (`CONCURRENCY=4`):** Configured in the official **3–12 sweet spot** for parallel sampler and worker execution. Runs 4 parallel candidate streams, balancing natural population diversity across MAP-Elites niches with high candidate throughput (~15s latency per step) without hitting API rate limits.

---
*All hospital data and patient figures are synthetic for demonstration purposes.*
