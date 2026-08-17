# Project Monaro / F-DSE Strict Access Control Guardrails

- **Mandatory Allowlisted Access Invariant**:
  - The F-DSE / Project Monaro Risk Dashboard and related governance tools MUST ONLY be accessible to explicitly allowlisted users or Ganpati/Google groups (e.g., `monaro-risk-prod`, `monaro-risk-dev`, `monaro-risk-admin`).
  - No project data, UI, or artifacts may be exposed to the general corporate population.

- **Prohibited Hosting & Sharing Recommendations (STRICT NEGATIVE CONSTRAINT)**:
  - **NEVER** recommend, suggest, or deploy to **C4A Starter (Porcupette)**, public App Engine, or any shared hosting platform that defaults to granting access to all `@google.com` corporate accounts without granular group ACL enforcement.
  - **NEVER** propose sharing mechanisms that bypass user/group allowlists.

- **Permitted Access-Restricted Deployment Patterns**:
  1. **Private Google Cloud Run (TwoSync IAM)**: Cloud Run deployed with `--no-allow-unauthenticated` and IAM `roles/run.invoker` bound strictly to `group:monaro-risk-prod@twosync.google.com` (using an approved 1P GCP project from C4A IDP / Nexus).
  2. **Google Drive Shared Folder (Data-Layer ACL)**: Static assets and snapshots stored in a restricted Google Drive Shared Folder whose membership is synchronized with the Ganpati team roster.
  3. **Internal Google3 / Borg Service (UberProxy ACL)**: Dedicated Borg/x20web service fronted by an `.acls` file strictly enforcing `allow: %monaro-risk-prod.prod`.
