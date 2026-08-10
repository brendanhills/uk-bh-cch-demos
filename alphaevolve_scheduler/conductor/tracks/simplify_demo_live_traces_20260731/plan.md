# Implementation Plan: 3-Phase Executive Storytelling & Simplified Trace Modes (`simplify_demo_live_traces`)

## Phase 1: Trace Archiving & Canonical Baseline Realism (`program.py` & `data/`)
- [x] Task: Archive non-canonical historical trace files
  - [x] Move `data/traces_high.jsonl` and `data/traces_med.jsonl` to `data/archive/`
  - [x] Verify `data/traces_low.jsonl` remains in `data/` as our single canonical pre-recorded demo trace
- [x] Task: Refine baseline scheduling heuristic for Friday realism (`experiment/program.py`)
  - [x] Modify `build_schedule` in `experiment/program.py` to balance surgical appointments across Monday–Friday rather than front-loading Monday–Thursday
  - [x] Verify that Friday receives a realistic surgical caseload in the baseline (Step 0)
- [x] Task: Regenerate canonical demo trace (`data/traces_low.jsonl`)
  - [x] Re-run the baseline evaluation and verify `patientsScheduled` and day distribution in Step 0
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: 3-Phase Executive Storytelling & UI Controls (`cch/index.html`)
- [x] Task: Implement clean 2-option Execution Mode Toggle with Live default
  - [x] Replace the `Scenario:` dropdown with a segmented toggle: `⚡ Live AlphaEvolve Run (Default)` vs. `🎬 Demo Mode (Paced Replay)`
  - [x] Ensure **Live AlphaEvolve Run** is selected by default on page load
  - [x] Hide `mock_trace_replan.jsonl` ("🧪 Fixture Mode") from main header controls, making it accessible only via URL parameter `?debug=1`
- [x] Task: Enable interactive presenter changes in Phase 1 (Before) and Phase 3 (After) — Primary Focus
  - [x] Ensure presenters can step through weeks and inject unplanned emergency disruptions in Phase 1 (Traditional Algorithm) to demonstrate baseline gaps and failures
  - [x] Ensure presenters can step through weeks and inject unplanned emergency disruptions in Phase 3 (Evolved Algorithm) to demonstrate superior scheduling and resilience
  - [x] Ensure the schedule grid responds immediately and clearly to presenter changes in both phases
- [x] Task: Configure Phase 2 to use the real AlphaEvolve API
  - [x] Wire Phase 2 execution to invoke `/run-optimization` and poll live candidate updates from the AlphaEvolve API (~45–60 seconds estimated duration)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Presenter Documentation Alignment (`demo_script.md` & `README.md`)
- [x] Task: Align executive presentation script (`demo_script.md`)
  - [x] Document the 3-Phase Executive Storytelling workflow (Phase 1 Before -> Phase 2 Evolution -> Phase 3 After)
  - [x] Add explicit presenter talking points for interactive multi-week stepping and emergency disruption comparisons
- [x] Task: Align repository readme (`README.md`)
  - [x] Document the canonical pre-recorded demo trace (`traces_low.jsonl`), archive location, and default Live mode
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
