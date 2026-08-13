# Implementation Plan: Production Deployment, Drive-Native Storage & Turnkey Handover

## Phase 1: Google Drive Storage & Ingestion Pipeline
- [ ] Task: Enhance `server.py` for Google Drive-Native Storage & Snapshots
  - [ ] Support loading and saving `weekly_snapshots.json` to Google Drive folder / local cache
  - [ ] Ensure API endpoints (`/api/sync-sheet`, `/api/ingest-report`, `/api/check-drive-sync`, `/api/sync-notebook`) respond reliably to user-triggered UI actions
- [ ] Task: Connect Interactive Ingestion in UI (`index.html`)
  - [ ] Verify UI buttons ("Sync with Drive", "Ingest Weekly Report") trigger backend APIs with visual progress feedback
- [ ] Task: Phase 1 Verification & Checkpoint (Verify interactive ingestion and snapshot persistence)

## Phase 2: Deployment & Operations Tooling
- [ ] Task: Finalize Deployment & Lifecycle Scripts
  - [ ] Verify `run_server.sh` 1-command tmux lifecycle (start, attach, restart, kill)
  - [ ] Verify `deploy/deploy_gcp.sh` and `deploy/shutdown.sh`
  - [ ] Update `.env.example` with Google Drive and Ganpati TwoSync configurations
- [ ] Task: Phase 2 Verification & Checkpoint

## Phase 3: Turnkey Handover Package & Tech Specs Update
- [ ] Task: Update Project Tech Specs
  - [ ] Update `conductor/tech-stack.md` with Drive-native storage and Ganpati/TwoSync architecture
  - [ ] Update `conductor/product.md` with F-DSE platform definition and handover context
- [ ] Task: Create Turnkey Handover Package (`HANDOVER_GUIDE.md`)
  - [ ] Architecture overview and Google Drive folder structure
  - [ ] Daily user operations and live ingestion guide
  - [ ] Access management guide for `monaro-risk-admin`, `monaro-risk-dev`, `monaro-risk-prod`
  - [ ] 1-command startup, deployment, and emergency shutdown procedures
- [ ] Task: Update `README.md` and commit all assets to remote repository
- [ ] Task: Phase 3 Verification & Checkpoint
