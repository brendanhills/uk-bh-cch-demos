# 📓 NotebookLM Enterprise API Sandbox - Testing Walkthrough

Welcome to the **Interactive Testing Walkthrough**! This document provides complete, step-by-step instructions for running, testing, and verifying both **Mock Mode** (local offline emulation) and **Live Mode** (real Google Cloud Platform transactions).

---

## 🚀 Quick Reference Commands

| Goal | Command | Mode | Expected Result |
| :--- | :--- | :--- | :--- |
| **Install Dependencies** | `uv sync` | Local | Installs packages and sets up virtual env |
| **Initialize Mock Tokens** | `uv run setup_mock_tokens.py` | Local | Generates `mock_tokens.json` |
| **Full Local Self-Test** | `uv run test_api.py self-test --mode mock` | **Mock** | Scenario 1 & 2 pass cleanly (100% offline) |
| **Authorize Live Mode** | `uv run authorize.py` | **Live** | Interactive browser login, prints token, updates `.env` |
| **Run Live Lifecycle** | `INTEGRATION_TEST_MODE=live uv run python -m unittest tests.test_scenarios.TestNotebookLMScenarios.test_01_standard_notebook_lifecycle` | **Live** | Creates, uploads to, and deletes a real notebook on GCP |

---

## 📂 Configuration Files

### 1. `.env` File
This file manages environment variables for Live mode. If it does not exist, running `uv run authorize.py` will automatically create it from `.env.example`.
```env
# Google Cloud Project Details
GCP_PROJECT_NUMBER=376231489344
GCP_LOCATION=global
GCP_ENDPOINT_LOCATION=us

# OAuth2 Access Token (automatically updated by authorize.py)
GCP_ACCESS_TOKEN=your_oauth_access_token_here

# Mode of operation: 'live' or 'mock'
DEFAULT_MODE=live

# Enable verbose HTTP auditing of exact requests, responses, and curl commands
VERBOSE_LOGGING=True
```

### 2. `mock_tokens.json`
This file contains the individual tokens used for Scenario 2 (Admin Recovery) to simulate multiple corporate users (Alice, Bob, Clara, and the Administrator).
*   **In Mock Mode**: These tokens can be dummy strings (e.g. `mock_alice_token`).
*   **In Live Mode**: To run Scenario 2 against real Google Cloud endpoints, these must be populated with **real, separate OAuth2 Access Tokens** for each user. Otherwise, GCP will reject the request with `401 Unauthorized`.

---

## 🎯 Step-by-Step Test Scenarios

### 🛠️ Scenario 1: Standard Notebook Lifecycle
This scenario verifies a single user's notebook management lifecycle:
1.  **Create Notebook**: Generates a blank notebook.
2.  **Batch Add Sources**: Appends text-based guides and web URL references simultaneously.
3.  **Local File Streaming Upload**: Uploads a raw local text file directly using the `/upload/` binary endpoint.
4.  **Get Metadata**: Retrives and asserts notebook structure and user role.
5.  **Share Notebook**: Grants reader and writer permissions to team members.
6.  **Delete Source**: Removes specific documents from the notebook.
7.  **Delete Notebook**: Safely cleans up and removes the notebook.

#### How to Run (Mock Mode - Instant & Offline):
```bash
uv run test_api.py self-test --mode mock
```

#### How to Run (Live Mode - Real GCP Resources):
1.  Run the interactive authorization script:
    ```bash
    uv run authorize.py
    ```
2.  Verify your `.env` contains the correct `GCP_PROJECT_NUMBER`.
3.  Execute the live lifecycle test:
    ```bash
    INTEGRATION_TEST_MODE=live uv run python -m unittest tests.test_scenarios.TestNotebookLMScenarios.test_01_standard_notebook_lifecycle
    ```

---

### 🛡️ Scenario 2: Admin Recovery & Offboarding
This scenario simulates enterprise offboarding and recovery:
1.  **Alice** (departing employee) creates a shared team notebook.
2.  **Bob** (peer writer) works on the notebook.
3.  **Alice** is offboarded and her access is terminated (simulated by deleting her IAM role or credentials). The notebook is now orphaned.
4.  The **Administrator** uses project-level permissions to locate the notebook, transfer **Owner** status to **Clara** (new employee), and remove Alice from the access list.
5.  **Clara** successfully verifies she can manage and delete the notebook.

#### How to Run (Mock Mode - Passes Automatically):
```bash
uv run test_api.py self-test --mode mock
```

> [!NOTE]
> **Why Scenario 2 fails with 401 Unauthorized in Live Mode:**
> Running Scenario 2 in Live Mode requires **4 distinct, real Google Cloud users and active authenticated OAuth2 access tokens** generated simultaneously and populated into `mock_tokens.json`.
> If you run Scenario 2 in Live Mode using the default mock tokens, Google Cloud will return an `UNAUTHENTICATED (ACCESS_TOKEN_TYPE_UNSUPPORTED)` error. This behavior is expected and confirms GCP's robust authentication and security boundary enforcement.

---

## 🌐 Dynamic Endpoint & Region Management
The sandbox SDK has a built-in regional endpoint mapper inside `NotebookLMClient`:
*   If `GCP_LOCATION` is set to `"global"`, requests are automatically sent to the global endpoint:
    `https://discoveryengine.googleapis.com` (no prefix)
*   If `GCP_LOCATION` is set to a region like `"us"` or `"eu"`, requests are automatically sent to the regional endpoint:
    `https://us-discoveryengine.googleapis.com` or `https://eu-discoveryengine.googleapis.com`

This automatic routing prevents `400 INVALID_ARGUMENT (Incorrect API endpoint used)` errors out of the box!
