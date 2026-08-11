# Specification: Cloud-Native IDP Deployment with TwoSync Google SSO

## 1. Overview
Deploy the F-DSE Program Governance & Risk Intelligence Platform to Google's official Cloud-Native Internal Developer Platform (C4A IDP / Nexus). This establishes dedicated, team-owned Cloud Run infrastructure with automated CI/CD and strict Google SSO access control governed by your TwoSync team group.

## 2. Functional Requirements
- **Nexus Provisioning**: Provision a dedicated Static Website / Web App application via Nexus UI (`go/idp`).
- **Access Control (Google SSO)**: Restrict Cloud Run invocation to the authorized TwoSync Ganpati group (`<team>@twosync.google.com`) and designated team emails.
- **Repository Integration**: Sync local frontend code (`index.html`, `assets/`) to the team's dedicated GitHub Enterprise repository (`depot.code.corp.goog`).
- **Automated CI/CD**: Merging PRs into `main` automatically triggers GitHub Actions to build and deploy container revisions to Cloud Run.
- **Local Deployment & Operations Suite**:
  - `deploy/deploy.sh`: 1-click script to sync local changes, create branch, and open PR.
  - `deploy/shutdown.sh`: 1-click script to immediately take the service offline.
  - `deploy/README.md`: Step-by-step developer guide.

## 3. Security & Non-Functional Requirements
- **Google Corporate SSO**: Enforced at the infrastructure level by Google Cloud IAP / UberProxy.
- **Least Privilege**: Only authorized TwoSync group members and explicit `@google.com` accounts can access the application.
- **Domain Guardrails**: Strict exclusion of non-corporate domains (e.g. `altostrat.com`).
- **Operational Simplicity**: Fully managed cloud-native stack without requiring manual Borg or google3 configuration.

## 4. Acceptance Criteria
- [ ] Application scaffolded in Nexus with dedicated GCP Project and GHES repository.
- [ ] TwoSync team group registered and bound to Cloud Run Invoker IAM policy.
- [ ] Initial deployment verified live on Cloud Run with Google SSO authentication.
- [ ] Deployment scripts in `deploy/` verified with dry-run and live test.
- [ ] Service shutdown script verified to take the service offline immediately.
