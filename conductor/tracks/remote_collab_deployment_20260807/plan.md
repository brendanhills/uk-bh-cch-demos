# Implementation Plan: Remote Collaborative Deployment & AI Studio Workflow

## Phase 1: Deployment Infrastructure & Packaging (Cloud Run + Boq + Google Sites)
- [ ] Task: Create Multi-Stage Dockerfile and NGINX Configuration
  - [ ] Write `Dockerfile` with multi-stage build (Node 20 build stage -> NGINX Alpine runtime stage)
  - [ ] Write `nginx.conf` with Single Page Application routing (`try_files $uri $uri/ /index.html;`), gzip compression, and caching
  - [ ] Configure `Content-Security-Policy: frame-ancestors https://sites.google.com https://*.google.com;` and `X-Frame-Options` to allow embedding in Google Workspace Sites
- [ ] Task: Create Cloud Run Deployment Automation & IAP Access Scripts
  - [ ] Write `scripts/deploy_cloud_run.sh` script automating `gcloud builds submit` and `gcloud run deploy` with configurable GCP project, region, and service name
  - [ ] Document IAP / IAM access control configuration commands for granting access to `@google.com`, `@vendor.google.com`, and `@partner.google.com`
- [ ] Task: Create Google3 Boq Static Web Target Configuration
  - [ ] Write Boq server configuration / BUILD rules for serving static Vite bundle in internal Piper environments
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
  - [ ] Verify local Docker build and NGINX configuration headers

## Phase 2: AI Studio Collaboration Workflow & Sync Tooling
- [ ] Task: Author AI Studio Collaboration Guide (`AI_STUDIO_WORKFLOW.md`)
  - [ ] Document the AI Studio prototyping workflow (prompt design, web app preview, component iteration)
  - [ ] Document the step-by-step export process from AI Studio (Get Code / React export)
  - [ ] Define the component ingestion mapping (`src/components/`, `src/data/`, `src/types.ts`)
- [ ] Task: Implement Build and Ingestion Validation Tooling
  - [ ] Ensure npm validation scripts (`npm run build`, `npm run typecheck`) verify imported AI Studio components adhere to project TypeScript definitions
  - [ ] Test build and type-checking across existing components
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
  - [ ] Run full build verification test suite

## Phase 3: xWF & Multi-Developer Onboarding & Governance
- [ ] Task: Author Comprehensive Collaboration Guide (`COLLABORATION_GUIDE.md`)
  - [ ] Document repository access, centralized `dev` branch push policy (always push directly to `origin dev`, never push feature branches to remote), and team onboarding for FTE and xWF members
  - [ ] Document GCP IAM role assignment matrix for xWF colleagues (`roles/run.viewer`, `roles/run.developer`, `roles/iap.httpsResourceAccessor`)
  - [ ] Document Google Workspace Site embedding instructions (step-by-step Google Sites iframe embed guide)
  - [ ] Document Google3 / CitC alternative workflow for team members with Piper access
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
  - [ ] Review all documentation for completeness, clarity, and ease of onboarding
