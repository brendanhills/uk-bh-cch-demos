# Implementation Plan: AlphaEvolve Optimization Backend (Phase 2)

## Phase 1: Environment & Centralized Configuration
- [x] Task: Environment Setup
  - [x] Install AlphaEvolve via Git URL and remove submodule artifacts (`uv pip install git+https://github.com/Google-Cloud-AI/alphaevolve-on-googlecloud.git`)
  - [x] Configure `uv` virtual environment and install backend dependencies (`numpy`, `python-dotenv`, `nest_asyncio`)
- [x] Task: Centralized Scenario Definition
  - [x] Define the JSON schema for the complete Phase 1 scenario
  - [x] Create `data/config.json` populated with RCH resources, staff, demands, and baseline heuristics (e.g., fatigue thresholds, overtime multipliers, objective weights)
- [x] Task: Data Loader Implementation
  - [x] Implement a Python module/script to load and parse `data/config.json`
  - [x] Validate that all required fields and heuristic thresholds are present
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Evaluator Logic & Modularity
- [x] Task: Integration Research
  - [x] Explore the installed `alpha_evolve` package to identify core classes and API patterns
- [x] Task: Core Domain Models
  - [x] Create decoupled internal data models representing Staff, Resources, and Schedules, strictly separate from scenario-specific settings
- [x] Task: Refactor Directory Structure
  - [x] Move backend logic and .env to experiment/ and remove legacy Kmart files
- [x] Task: Heuristics & Evaluator Constraints
  - [x] Implement Resource Co-scheduling constraints (Staff + Room + Patient availability)
  - [x] Implement Skill & Role Matching rules
  - [x] Implement Fatigue Management and Budget Control logic reading thresholds directly from the configuration
- [x] Task: Best Effort Unit Tests
  - [x] Implement optional basic unit tests for the complex constraint and mathematical logic in the evaluator
- [x] Task: Objective Function
  - [x] Implement the weighted objective function balancing patient throughput vs. idle/overtime costs
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Execution Loop & Trace Generation
- [x] Task: Evolutionary Loop Adaptation
  - [x] Implement the asynchronous optimization loop invoking the AlphaEvolve engine
- [x] Task: Trace Exporter
  - [x] Capture snapshots of candidate schedules at key intervals
  - [x] Generate and append traces to `data/traces.jsonl` matching the exact frontend replay engine format
- [x] Task: Execution Verification
  - [x] Run the loop locally via a test script to ensure `traces.jsonl` is correctly populated and formatted
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Serving & Integration
- [~] Task: HTTP Server Upgrade
  - [x] Replace the built-in static file server in `serve.sh` with a Python HTTP handler
  - [x] Ensure absolute backward compatibility so that all static UI assets continue to serve flawlessly
- [~] Task: API Trigger Endpoint
  - [x] Implement the `/run-optimization` route
  - [x] Connect the endpoint to start the asynchronous evolutionary loop in a background thread or process
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 5: Demonstration & Polish
- [ ] Task: End-to-End Verification
  - [ ] Trigger optimization from the UI and verify that real-time traces drive the replay animations successfully
- [ ] Task: Scenario Re-purposability Documentation
  - [ ] Clearly document the schema of `data/config.json` and provide guidelines on how to modify it to adapt the demo for other domains (e.g., manufacturing, logistics)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase: Review Fixes
- [x] Task: Apply review suggestions a3fea12
