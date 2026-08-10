# Implementation Plan: Before/After Operational Comparison Tab

## Phase 1: Backend Data Loading & Stat Preparation
- [x] Task: Extend the HTTP server to serve baseline and dynamic metrics
 - [x] Add static reading for Step 0 and Step 1 from `data/traces_low.jsonl` exactly on server init.
 - [x] Dynamically parse exactly `config.json` to calculate supply and demands.
 - [x] Expose an executive scenario breakdown payload in `rch/index.html`.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
 - [x] Visually verify endpoint responses via browser and unit tests.

## Phase 2: UI Tab Layout & State Management
- [x] Task: Implement the "Breakdown" Tab Toggle UI
 - [x] Add styled `<button>` tabs right next to the Operational Scenario dropdown in `rch/index.html`.
 - [x] Add styling matching the RCH design system.
- [x] Task: Implement Content Toggle Logic
 - [x] Wire vanilla JS state to toggle main dashboard grid and breakdown panel cleanly.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
 - [x] Manually click and verify perfect visual tab switching.

## Phase 3: Data Visualizations & Storytelling
- [x] Task: Supply vs Demand Chart
 - [x] Integrate capacity vs demand visualization comparing 300h vs 255h.
- [x] Task: Throughput Metric Cards & Narrative Text
 - [x] Add Big Stats comparing Step 0 vs Step 1 patient throughput and rest gap compliance.
 - [x] Add executive priority cards and collapsible formula drawer.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
 - [x] Final visual UI demonstration and checkpoint commit.
