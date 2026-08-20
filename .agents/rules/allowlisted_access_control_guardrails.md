# Project Monaro / F-DSE Strict Access Control Guardrails

- **Mandatory Allowlisted Access Invariant**:
  - The F-DSE / Project Monaro Risk Dashboard and related governance tools MUST ONLY be accessible to explicitly allowlisted users or Ganpati/Google groups (e.g., `monaro-risk-prod`, `monaro-risk-dev`, `monaro-risk-admin`).
  - No project data, UI, or artifacts may be exposed to the general corporate population.

- **Dual-Environment (Dev & Prod) Architecture Invariant**:
  - The system maintains strict separation between **Development** and **Production** environments:
    1. **Development Environment**:
       - **GCP Project**: `monaro-risk-dev`
       - **Region**: `australia-southeast1` (Sydney)
       - **Git Branch**: `dev` (Push trigger on `project_dash/**`)
       - **Cloud Run Service**: `monaro-risk-dash-dev`
       - **Cloud Build Trigger**: `deploy-monaro-risk-dash-dev`
       - **Access Group**: `monaro-risk-dev@google.com` (Google Group) / `monaro-risk-dev@twosync.google.com`
    2. **Production Environment**:
       - **GCP Project**: `monaro-risk-prod`
       - **Region**: `australia-southeast1` (Sydney)
       - **Git Trigger**: Tags on `dev` branch matching `^project_dash/prod-.*$` (e.g. `project_dash/prod-v1.0.0`)
       - **Cloud Run Service**: `monaro-risk-dash-prod`
       - **Cloud Build Trigger**: `deploy-monaro-risk-dash-prod`
       - **Access Group**: `monaro-risk-prod@google.com` (Google Group) / `monaro-risk-prod@twosync.google.com`
  - All deployments must be automated through Cloud Build triggers in `australia-southeast1`.
  - Cloud Build deployments run asynchronously in the background. Do not block or poll after pushes. Use `scripts/check_build_status.py` for on-demand diagnostics.

- **Prohibited Hosting & Sharing Recommendations (STRICT NEGATIVE CONSTRAINT)**:
  - **NEVER** recommend, suggest, or deploy to **C4A Starter (Porcupette)**, public App Engine, or any shared hosting platform that defaults to granting access to all `@google.com` corporate accounts without granular group ACL enforcement.
  - **NEVER** propose sharing mechanisms that bypass user/group allowlists.

- **Permitted Access-Restricted Deployment Patterns**:
  1. **Private Google Cloud Run (TwoSync IAM)**: Cloud Run deployed with `--no-allow-unauthenticated` and IAM `roles/run.invoker` bound strictly to the corresponding environment group (`monaro-risk-dev@twosync.google.com` for Dev, `monaro-risk-prod@twosync.google.com` for Prod).
  2. **Google Drive Shared Folder (Data-Layer ACL)**: Static assets and snapshots stored in a restricted Google Drive Shared Folder whose membership is synchronized with the Ganpati team roster.
  3. **Internal Google3 / Borg Service (UberProxy ACL)**: Dedicated Borg/x20web service fronted by an `.acls` file strictly enforcing `allow: %monaro-risk-prod.prod` or `%monaro-risk-dev.prod`.
