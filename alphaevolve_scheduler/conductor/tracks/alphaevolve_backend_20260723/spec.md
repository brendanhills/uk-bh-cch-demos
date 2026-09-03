# Track Specification: AlphaEvolve Optimization Backend (Phase 2)

## 1. Overview
Implement the AlphaEvolve evolutionary optimization backend for the RCH Co-Scheduling project. This track focuses on integrating the `vendor/alphaevolve` submodule, defining the hospital-specific constraints and heuristics, processing the static configuration, and generating real-time evolution traces that the frontend UI will consume to drive animations.

## 2. Functional Requirements

### 2.1 Dependency Setup
- Install the `alphaevolve` framework directly from its Git repository.
- Configure the environment using `uv` to manage backend dependencies (`numpy`, `python-dotenv`, `nest_asyncio`).

### 2.2 Centralized Data Configuration & Loading
- Define a JSON schema for the complete Phase 1 scenario in a new `data/config.json` file.
- This configuration MUST centralize **all customer-specific settings**, including:
  - **Static Data:** Resources, Staff pools with skills, and Appointment/Surgery demands.
  - **Heuristic Parameters:** Thresholds (e.g., minimum 10h rest for fatigue), budget rules (overtime multipliers), and scheduling horizon.
  - **Objective Weights:** Priorities for patient throughput vs. idle time vs. overtime costs.
- Implement a data loader that reads this configuration and parses it into internal data structures, maintaining strict separation of scenario settings and core logic.

### 2.3 AlphaEvolve Engine & Evaluator Logic
- Adapt the standard AlphaEvolve evolutionary loop for the co-scheduling domain.
- Implement constraints and heuristics in Python, reading parameters directly from the configuration layer:
  - **Resource Co-scheduling:** Ensure Staff, Room/Equipment, and Patient are all available and assigned simultaneously.
  - **Skill & Role Matching:** Match specific surgical skills to tasks.
  - **Fatigue Management:** Enforce configured rest thresholds.
  - **Budget Control:** Calculate costs based on configured rates.
- Ensure all evolutionary program templates and evaluator logic are clearly documented and grouped in a dedicated module (e.g., `evaluators/`) to facilitate easy adaptation.

### 2.4 Execution & Trace Generation
- Implement an asynchronous Python loop that runs the optimization.
- During evolution, capture traces (snapshots of the best candidate schedules at key intervals).
- Append these traces in real-time to `data/traces.jsonl` in the format expected by the frontend replay engine.

### 2.5 Serving Integration
- Upgrade `serve.sh` from a static server to a lightweight Python HTTP handler.
- Support a `/run-optimization` trigger endpoint that starts the asynchronous optimization loop without blocking the UI.

## 3. Non-Functional Requirements

### 3.1 Performance & Reliability
- The optimization loop must run asynchronously to prevent blocking the HTTP server or UI.
- File I/O for `traces.jsonl` must be handled safely to avoid race conditions or corruption while appending.

### 3.2 Algorithmic Clarity
- The evaluator logic and constraints must be clearly structured and documented, prioritizing algorithmic clarity over extreme micro-optimizations, to serve as a clear demonstration of AlphaEvolve.

### 3.3 Modularity & Re-purposability
- **Strict Decoupling:** The core backend logic must be strictly decoupled from the RCH scenario. Swapping the hospital scenario for a truck-routing or manufacturing scenario should only require modifying the `data/config.json` file and adapting the internal data classes, without rewriting the core optimization loop or serving logic.

## 4. Acceptance Criteria
- The `vendor/alphaevolve` submodule is successfully initialized and dependencies are installed.
- Centralized `data/config.json` successfully drives both the data loading and the constraint evaluations.
- Running the `/run-optimization` trigger starts the Python loop and successfully generates valid JSONL traces in `data/traces.jsonl`.
- The generated traces accurately reflect the Baseline vs. Optimized schedule improvements.
- Constraints (Resource matching, Fatigue baseline) read from configuration are demonstrably enforced.
- `serve.sh` continues to serve the static UI files flawlessly alongside the new API endpoint.

## 5. Out of Scope for this Track
- Real-time WebSocket communication (polling via HTTP or direct file reading is sufficient).
- Complex, production-grade advanced fairness rules.
- Multi-site management or additional equipment types beyond Phase 1.
- Full automated integration test suite for the UI.
