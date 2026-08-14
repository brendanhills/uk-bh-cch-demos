# Implementation Plan: Zero-Server Client-Only Architecture, Drive-Native Storage & Multi-Notebook Registry

## Phase 1: Generalized Multi-Notebook Registry & Sync Engine
- [x] Task: Create Multi-Notebook Registry Structure
  - [x] Create `data/notebooks/registry.json` supporting multiple notebook configurations
  - [x] Migrate existing Monaro Contract Notebook into registry
- [x] Task: Generalize `sync_notebook.py`
  - [x] Support `--notebook-id`, `--title`, `--slug`, and `--category` flags
  - [x] Dynamically generate per-notebook source catalogs and bundle mappings
- [x] Task: Phase 1 Verification & Checkpoint (Verified multi-notebook CLI registration and sync)

## Phase 2: Frontend Multi-Notebook Selector & Client-Side Ingestion
- [x] Task: Add Notebook Selector Dropdown in UI (`index.html`)
  - [x] Render interactive dropdown in Contractual Horizon tab
  - [x] Dynamically swap source catalog table, token metrics, and bundle risk mappings
- [x] Task: Verify Client-Side Drive Sync & Ingestion Flow
  - [x] Ensure browser-direct sync and shared Drive snapshot loading operate smoothly
- [x] Task: Phase 2 Verification & Checkpoint (Verified UI dropdown and dynamic switching)

## Phase 3: Handover Finalization & Documentation Sync
- [x] Task: Finalize `HANDOVER_GUIDE.md` with Multi-Notebook instructions
- [x] Task: Update `conductor/tech-stack.md` and `conductor/product.md`
- [x] Task: Commit, push to remote repository, and verify clean git status
- [x] Task: Phase 3 Verification & Checkpoint
