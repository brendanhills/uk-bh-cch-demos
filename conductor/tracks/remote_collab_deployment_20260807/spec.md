# Specification: Remote Collaborative Deployment & AI Studio Workflow (FTE & xWF Compatible)

## 1. Overview & Objectives
This track establishes the production deployment architecture and collaborative development workflows for the **Project Dashboard** (React 18 + TypeScript + Vite). It resolves the constraint of local-only execution by providing persistent, remote internal hosting (mirroring AI Studio's cloud deployment architecture) and establishes a frictionless co-development workflow for colleagues (including Extended Workforce / xWF) modifying the dashboard via Google AI Studio, Git, and Google Cloud.

---

## 2. Architecture & How AI Studio Deploys
- **How AI Studio Works:** Google AI Studio operates by generating client-side single-page applications (SPAs) or lightweight servers and deploying them to serverless container runtimes (like Google Cloud Run) via automated Cloud Build pipelines, backed by Google authentication (IAP/OAuth) and managed HTTPS certificates.
- **Project Dashboard Deployment Strategy:** 
  1. **Primary FTE + xWF Compatible Target:** Containerized NGINX static web server on **Google Cloud Run** with Google Identity-Aware Proxy (IAP) / IAM access configured to allow `@google.com`, `@vendor.google.com`, and `@partner.google.com` accounts or designated Google Groups.
  2. **Secondary Internal Target:** Google3 Boq service on Borg behind UberProxy (`*.corp.google.com`) for corp-only environments.
  3. **Google Workspace Site Integration:** Configured HTTP response headers (`Content-Security-Policy: frame-ancestors https://sites.google.com`) to allow embedding the deployed dashboard directly into internal Google Sites (`sites.google.com`).

---

## 3. Functional Requirements

### 3.1. Remote Hosting & Deployment Packaging (FR-1)
- **Docker / Cloud Run Packaging (xWF & FTE Compatible):** Create an optimized, multi-stage `Dockerfile` with NGINX for internal Cloud Run deployment behind IAP with custom frame-ancestor headers.
- **Boq / Borg Configuration (google3):** Create Boq static web application configs and BUILD rules for internal Piper-based deployments.
- **Google Sites Embedding Support:** Configure web server headers (`X-Frame-Options` / CSP `frame-ancestors https://sites.google.com`) allowing seamless `<iframe>` embedding inside Google Workspace Sites.

### 3.2. AI Studio Co-Development & Sync Workflow (FR-2)
- **AI Studio Ingestion Protocol:** Standardize the file structure (`src/components/`, `src/data/`, `src/types.ts`) so UI components or prompt-driven features drafted by xWF colleagues in Google AI Studio can be imported cleanly.
- **Sync & Verification Tooling:** Provide clear documentation (`AI_STUDIO_WORKFLOW.md`) and validation scripts (`npm run build`, `npm run typecheck`) to verify AI Studio exports integrate without breaking existing dashboard routes or TypeScript types.

### 3.3. xWF-Friendly Multi-Developer Code Sharing & Access (FR-3)
- **GitHub / Git Collaboration Workflow:** Primary repository workflow supporting both FTE and xWF collaborators via GitHub PRs, feature branches, and code reviews.
- **GCP IAM & Tool Access Matrix:** Step-by-step instructions for granting xWF team members necessary GCP IAM permissions (`Cloud Run Viewer/Developer`, `IAP Web App User`, `Artifact Registry Reader`).
- **Google3 / CitC Alternative:** Document Piper/CitC onboarding for team members with full internal codebase access.

### 3.4. Security & Access Control (FR-4)
- Enforce Google IAP / Corp SSO to ensure only authorized internal users and xWF collaborators access the remote dashboard.
- Protect Gemini API keys and backend service account tokens using Secret Manager / runtime environment variables.

---

## 4. Acceptance Criteria
- [ ] Multi-stage `Dockerfile` & NGINX configuration optimized for Cloud Run and Google Sites iframe embedding.
- [ ] Boq/Borg deployment target configurations for Google3 Piper monorepo.
- [ ] Working CSP/frame-ancestor configuration enabling Google Sites iframe embedding.
- [ ] Step-by-step AI Studio collaboration and export/import guide (`AI_STUDIO_WORKFLOW.md`).
- [ ] Developer onboarding and code sharing guide for FTE & xWF (`COLLABORATION_GUIDE.md`).
- [ ] Clean build verification (`npm run build` succeeds without errors).
