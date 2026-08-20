# Documentation Editing & Execution Guardrails

- **No Test Execution During Documentation Edits**:
  - When reviewing, creating, or editing markdown documentation, Conductor specs, track plans, or handover guides (where no executable application code or unit tests were modified), DO NOT run unit test suites, build commands, or server lifecycles.
  - Reserve test execution strictly for changes involving application source code (`.py`, `.js`, `.html`), test files (`tests/`), or configuration/build pipelines (`cloudbuild.yaml`, `Dockerfile`).

- **Documentation Organization Standards**:
  - Project operator manuals, maintainer runbooks, deployment guides, and team presentation walkthroughs MUST be organized inside the dedicated `docs/` directory (`docs/HANDOVER_GUIDE.md`, `docs/TEAM_PRESENTATION_GUIDE.md`, `docs/DEPLOYMENT_GUIDE.md`).
  - Root `README.md` and `Resume.md` must clearly index and link to the `docs/` directory.

- **User-Facing Ingestion Flow Description**:
  - In all user-facing documentation, describe data ingestion as primarily triggered directly from the web dashboard UI (**"Sync with Google Drive" / "Workspace Sync"** modal), presenting the CLI (`scripts/ingest_data.py`) as an optional backend automation script.
