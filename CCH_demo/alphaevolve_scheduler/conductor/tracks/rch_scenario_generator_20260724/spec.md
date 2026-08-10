# Track Specification: Enterprise Scenario Data Generator

## 1. Overview
Implement a scalable, randomized, but reproducible Python scenario generator script (`generate_scenario.py`) that outputs a large, enterprise-grade `data/config.json`. This replaces the tiny 4-patient smoke-test scenario with a dense 40-patient problem involving 5 rooms and 20 staff members, giving AlphaEvolve massive degrees of freedom to demonstrate true combinatorial optimization and fatigue elimination.

## 2. Functional Requirements

### 2.1 Generator Script Implementation
- Create `generate_scenario.py` in the project.
- The script MUST accept parameters (or have clear configurable constants) for the number of rooms, staff (Surgeons, Nurses), and Patient demands.
- The script MUST produce a valid `data/config.json` adhering exactly to our established schema.
- Generation MUST be completely reproducible (using a fixed `random.seed`) so the demo scenario runs identically and reliably every single time.

### 2.2 Default Scale Parameters
- Implement the exact parameters agreed upon for the primary enterprise demo:
  - 5 Operating Rooms.
  - 20 Staff Members (10 Surgeons, 10 Nurses).
  - 40 Patient Demands with randomized but realistic surgery durations (e.g., 60 to 240 minutes) and specific role requirements.

### 2.3 Integration & Backward Compatibility
- The generated `data/config.json` MUST continue to use the identical schema, heuristic thresholds, and weights, ensuring our Evaluator and Trace Exporter require **zero code changes**.
- The frontend UI Gantt chart MUST scale gracefully (scrolling if necessary) to accommodate the 5 distinct room rows.

## 3. Non-Functional Requirements

### 3.1 Maintainability
- The generator logic must be cleanly documented and modular so that it serves as an excellent reference for how to build scenarios for other domains (e.g., logistics, manufacturing) in the future.

### 3.2 Deterministic Feasibility
- To ensure AlphaEvolve does not get stuck in deadlocks, the generator should space out the generated demands within the scheduling horizon so that a highly optimal, 0-fatigue schedule is mathematically guaranteed to exist.

## 4. Acceptance Criteria
- Running the generator successfully overwrites `data/config.json` with a perfectly valid 40-patient dataset.
- Running the evolution loop against this new massive dataset compiles, evaluates, and optimizes without errors.
- The real-time traces stream perfectly to the frontend, demonstrating a highly dense, complex real-time optimization.

## 5. Out of Scope for this Track
- A web-based graphical Scenario Builder UI (strictly a CLI generator script).
- Supporting multiple named scenario files simultaneously (overwriting the single `data/config.json` is perfectly sufficient for this phase).
