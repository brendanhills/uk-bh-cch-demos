# Sandbox Handoff: RESUME.md

This document summarizes the outstanding validation tracks, untested hypotheses, and proposed future automation scripts to quickly pick up this sandbox environment.

---

## 🚀 Priority Hand-off Tasks

### 1. 🔬 Untested Hypothesis Validation: Cloud Audit Logging
* **Objective**: Verify if Google Cloud Audit Logging captures events for `discoveryengine.googleapis.com` (such as `CreateNotebook` or `GetNotebook`).
* **Why it matters**: Discovery Engine has no project-wide `list` endpoint (only user-scoped recency lists). Cloud Audit Logging is the primary proposed channel to discover hidden or orphaned notebooks.
* **Handoff Steps**:
  1. Set up a logging sink or log bucket to capture Google Cloud Audit Logs.
  2. Perform notebook creation and read operations in the active playground.
  3. Validate that logs record `CreateNotebook` or `GetNotebook` transactions and extract the JSON payload.
  4. Confirm that the log entries include the unique **Notebook ID (GUID)** and the **Creator's Email Address**.

### 2. 🤖 Propose Custom Admin Script / Gemini Engine (GE) Agent
* **Objective**: Build an administrative crawler script or a Gemini Engine (GE) Agent to catalog organizational notebooks.
* **Why it matters**: Automates the discovery of resources created by departed employees so administrators don't have to manually ask for GUIDs.
* **Handoff Steps**:
  1. Once the Audit Logs hypothesis (above) is verified, write a Python crawler script (`scripts/audit_notebooks.py`) using the `google-cloud-logging` SDK.
  2. Parse active GUIDs and creators to compile a live corporate registry.
  3. Integrate the script with the cloning engine to auto-alert admins when a notebook is orphaned (i.e. its creator is suspended or deleted in Google Workspace).

### 3. 👥 Manual Admin Cloning Walkthrough
* **Objective**: Walk through a live CLI clone test using the `admin@` account to verify cross-account recovery.
* **Why it matters**: Validates standard administrative recovery without running inside automated test rigs.
* **Handoff Steps**:
  1. Log in as an administrator:
     ```bash
     uv run setup_env.py admin
     ```
  2. Run the clone command on one of Brendan's notebooks (since the admin possesses project-level permissions to read other users' notebooks):
     ```bash
     uv run nblm_api.py clone <BRENDANS_NOTEBOOK_ID> --title "Admin Recovered Blueprint"
     ```
  3. Verify that:
     * Webpage sources are programmatically re-ingested.
     * The admin is the sole primary owner of the new notebook.
     * Non-replicable text or binary sources are cleanly flagged in the terminal.

---

## 🛠️ Sandbox Reference Commands

### Switch Active Terminal Identity
```bash
# Switch to Brendan
uv run setup_env.py brendan

# Switch to Admin
uv run setup_env.py admin

# Switch to Alice (suspension test user)
uv run setup_env.py alicenb
```

### Run Self-Test Suite
```bash
# Run complete programmatic scenario integration tests (Mock mode)
uv run nblm_api.py self-test
```
