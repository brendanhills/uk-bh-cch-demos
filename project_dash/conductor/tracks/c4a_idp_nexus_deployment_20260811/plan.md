# Implementation Plan: Cloud-Native IDP Deployment with TwoSync Google SSO

## Phase 1: Nexus Scaffolding & Access Control Setup
- [ ] Task: Group Registration & Pre-flight Setup
  - [ ] Identify/Create Team Ganpati MDB group
  - [ ] Register Ganpati group with TwoSync (`/google/src/head/depot/google3/security/twosync/tools/register.sh --group <group_name>`)
- [ ] Task: Nexus Application Provisioning
  - [ ] Open Nexus UI (`go/idp` / `https://nexus.corp.google.com/create/idp`)
  - [ ] Select Static Website template and enter Application ID & Team parameters
  - [ ] Complete automated resource provisioning (GCP Project & GHES Repo)
- [ ] Task: Phase 1 Verification & Checkpoint (Verify repository and project links)

## Phase 2: Codebase Packaging & Initial Rollout
- [ ] Task: Repository Synchronization
  - [ ] Clone newly provisioned GHES repo into `deploy/.repo`
  - [ ] Sync `index.html` and `assets/` into repository
- [ ] Task: Initial PR & Automated Deployment
  - [ ] Commit and push initial deployment branch to GitHub Enterprise
  - [ ] Open Pull Request and merge to `main`
  - [ ] Verify GitHub Actions builds container and deploys to Cloud Run
- [ ] Task: Phase 2 Verification & Checkpoint (Verify live Cloud Run URL with Google SSO)

## Phase 3: Operations Tooling & Access Verification
- [ ] Task: Update Deployment & Shutdown Scripts
  - [ ] Update `deploy/deploy.sh` with the new GHES repo target
  - [ ] Update `deploy/shutdown.sh` to target the dedicated IDP Cloud Run service
- [ ] Task: Verification & Security Audit
  - [ ] Verify Google SSO authentication enforces TwoSync group access
  - [ ] Test immediate service shutdown via `./deploy/shutdown.sh`
  - [ ] Document URLs and workflow in `README.md`
- [ ] Task: Phase 3 Verification & Checkpoint
