# Implementation Plan: Core Diagnostics & Configuration Healing

This plan outlines the implementation steps taken to establish the core troubleshooting suite for Google Antigravity. All tasks have been completed and verified.

---

## Phase 1: Environment Diagnostics and Process Control
- [x] **Task: Implement lightweight active process detection and safe termination**
  - [x] Write script block to search and identify stale `language_server` and `antigravity` processes in bash
  - [x] Exclude current shell PID to prevent terminal disconnects
  - [x] Implement safe process kill signals
- [x] **Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)**

## Phase 2: Configuration Auto-Healing Engine
- [x] **Task: Build Python configuration validation and healing script**
  - [x] Load and parse user's local projects from `~/.gemini/config/projects/`
  - [x] Inspect local workspace SQLite cache database (`state.vscdb`) to auto-discover active paths
  - [x] Scan and auto-detect any files missing correct `"enterpriseGcpProjectId"` parameters
  - [x] Update settings JSON block structurally to target `"uk-bh-experiments-argolis"`
- [x] **Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)**

## Phase 3: Integration and Manual Verification
- [x] **Task: Package tools and perform live validation**
  - [x] Assemble `fix_antigravity.sh` and make executable
  - [x] Test execution on empty project configurations
  - [x] Confirm clean restoration and desktop app startup fallback success
- [x] **Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)**
