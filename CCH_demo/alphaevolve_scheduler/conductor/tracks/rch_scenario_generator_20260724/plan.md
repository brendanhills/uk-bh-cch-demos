# Implementation Plan: Enterprise Scenario Data Generator

## Phase 1: Generator Implementation
- [x] Task: Script Scaffolding & Constants
  - [x] Create `generate_scenario.py` and define the target parameters (5 Rooms, 20 Staff, 40 Demands)
  - [x] Enforce strict determinism with `random.seed(42)` for absolute reproducibility
- [x] Task: Data Generation Logic
  - [x] Implement programmatic generation of Rooms, Staff (Surgeons/Nurses), and Patient Demands (with randomized durations between 60 to 240 mins)
  - [x] Construct and write the final valid `data/config.json` adhering to the exact schema and heuristic thresholds
- [x] Task: Validation & Execution
  - [x] Run the script to generate the massive 40-patient dataset
  - [x] Verify that our existing Backend Data Loader parses the new JSON perfectly without errors
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Scale Testing & UI Verification
- [x] Task: Backend Execution Testing
  - [x] Run `experiment/run_evolution.py` with the new dataset to ensure the engine compiles and evaluates the dense constraints perfectly
  - [x] Monitor trace generation to verify that the `code` transparency feature continues to stream flawlessly
- [x] Task: UI Scaling Verification
  - [x] Open the RCH dashboard to ensure the Gantt chart scales elegantly to display 5 distinct room rows and dozens of packed surgery blocks simultaneously
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
