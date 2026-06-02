# NotebookLM Enterprise API - Python Investigation Sandbox

Welcome to the **NotebookLM Enterprise API Python Investigation Sandbox**! This project is a pure Python sandbox designed to help you interactively test, investigate, and understand how the underlying REST API of Google NotebookLM Enterprise operates.

It includes a fully developed Python REST SDK client, programmatic scenario-based integration tests, individual educational scripts, and a built-in **Offline Mock database** so you can run the entire test suite immediately without any GCP configuration.

---

## 🚀 Quick Start

### 1. Install Dependencies
Ensure you are in the project workspace, and sync the project dependencies:
```bash
uv sync
```

### 2. Setup Mock Scenario Tokens
On a clean checkout, generate your local simulated scenario tokens using `uv run`:
```bash
uv run setup_mock_tokens.py
```

### 3. Run the Programmatic Integration Tests
Execute the complete scenario-based integration tests in **Mock Mode** (using our built-in offline mock emulator):
```bash
uv run test_api.py self-test
```
*This command runs the `unittest` scenarios, displaying verbose step-by-step console logs, JSON payloads, and copy-pasteable curl equivalents for every API action!*

---

## 📂 Project Structure

- **`notebooklm_client.py`**: The core SDK class (`NotebookLMClient`) wrapping all REST calls using `requests`. Features **Verbose HTTP Auditing** which pretty-prints HTTP headers, requests, JSON payloads, response codes, and copy-pasteable curl commands.
- **`test_api.py`**: An integrated CLI test harness to run single commands or run self-tests on demand.
- **`tests/test_scenarios.py`**: A `unittest` file containing two advanced integration tests:
  1. **Standard Notebook Lifecycle**: Create $\rightarrow$ Add Text/Web Sources $\rightarrow$ Upload local file $\rightarrow$ Read metadata $\rightarrow$ Share $\rightarrow$ Delete Source $\rightarrow$ Delete Notebook.
  2. **Admin Recovery & Re-assignment**: Simulates employee offboarding. A departing employee leaves an orphaned team notebook. An Administrator uses project-level permissions to retrieve the notebook, grant ownership to a new employee, and revoke the departed user's access.
- **`scripts/`**: Individual, bare-metal learning scripts designed for learning the APIs sequentially:
  - `scripts/create_notebook.py`
  - `scripts/add_sources.py`
  - `scripts/upload_file.py`
  - `scripts/share_notebook.py`
  - `scripts/delete_notebook.py`

---

## 📖 Deep-Dive: Understanding the REST API

The NotebookLM Enterprise API resides under Google's **Discovery Engine** platform. All requests follow a specific REST pattern:

### 1. Base URL & Path Patterns
- **Standard API Base URL**: `https://{ENDPOINT_LOCATION}-discoveryengine.googleapis.com/v1alpha`
- **File Upload Base URL**: `https://{ENDPOINT_LOCATION}-discoveryengine.googleapis.com/upload/v1alpha`

Paths are fully scoped by Google Cloud Project and Geographic Location:
`projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks`

*Where `ENDPOINT_LOCATION` is typically `us` or `eu`, `PROJECT_NUMBER` is your numeric Google Cloud Project ID, and `LOCATION` is `global` or a specific region.*

### 2. Core API Specifications

#### A. Create Notebook
- **HTTP Method**: `POST`
- **Path**: `notebooks`
- **JSON Request Payload**:
  ```json
  {
    "title": "My Notebook Title"
  }
  ```
- **Response Structure**:
  ```json
  {
    "title": "My Notebook Title",
    "notebookId": "123abc45",
    "emoji": "📓",
    "metadata": {
      "userRole": "PROJECT_ROLE_OWNER",
      "isShared": false,
      "isShareable": true
    },
    "name": "projects/{PROJECT_NUMBER}/locations/global/notebooks/123abc45"
  }
  ```

#### B. Batch Add Sources
- **HTTP Method**: `POST`
- **Path**: `notebooks/{NOTEBOOK_ID}/sources:batchCreate`
- **JSON Request Payload**:
  ```json
  {
    "userContents": [
      {
        "textContent": {
          "sourceName": "Raw Document Title",
          "content": "Full raw text content here..."
        }
      },
      {
        "webContent": {
          "url": "https://example.com/page",
          "sourceName": "Webpage Title"
        }
      }
    ]
  }
  ```

#### C. Streaming Local File Upload
To load local files (.pdf, .txt, .md, .docx, .mp3, etc.), you must invoke the **`/upload/`** endpoint:
- **HTTP Method**: `POST`
- **Path**: `notebooks/{NOTEBOOK_ID}/sources:uploadFile`
- **Crucial HTTP Headers Required**:
  - `X-Goog-Upload-File-Name: <DISPLAY_NAME>`
  - `X-Goog-Upload-Protocol: raw`
  - `Content-Type: <FILE_MIME_TYPE>` (e.g. `application/pdf`, `text/markdown`, `text/plain`)
- **Body**: Raw Binary Stream of the target file.

#### D. Share Notebook
Notebook sharing is managed via the `:share` sub-resource.
- **HTTP Method**: `POST`
- **Path**: `notebooks/{NOTEBOOK_ID}:share`
- **JSON Request Payload**:
  ```json
  {
    "accountAndRoles": [
      {
        "email": "sarah@enterprise.com",
        "role": "PROJECT_ROLE_WRITER"
      },
      {
        "email": "david@enterprise.com",
        "role": "PROJECT_ROLE_READER"
      }
    ]
  }
  ```
- **Supported Roles**:
  - `PROJECT_ROLE_OWNER`: Has complete ownership.
  - `PROJECT_ROLE_WRITER`: Has read/write access.
  - `PROJECT_ROLE_READER`: Has read-only access.
  - `PROJECT_ROLE_NOT_SHARED`: Revokes user access.

---

## 🌐 Transitioning to Live Mode (Google Cloud)

To test these scripts against your live Google Cloud environment:

### 1. GCP Prerequisites
1. Ensure you have an active GCP Project with billing enabled.
2. Ensure you have set up NotebookLM Enterprise and licensed your users.
3. Grant the **Cloud NotebookLM User** IAM role to your testing accounts.

### 2. Generate an Access Token
Ensure the `gcloud` CLI is installed and authenticated, then run:
```bash
gcloud auth login --enable-gdrive-access
gcloud auth print-access-token
```
*Note: `--enable-gdrive-access` is required if you plan to import Google Drive sources.*

### 3. Update Your `.env` Configuration
Open your local `.env` and fill in your real Google Cloud parameters:
```env
GCP_PROJECT_NUMBER=YOUR_NUMERIC_PROJECT_ID
GCP_LOCATION=global
GCP_ENDPOINT_LOCATION=us
GCP_ACCESS_TOKEN=PasteYourOAuth2TokenHere
DEFAULT_MODE=live
VERBOSE_LOGGING=True
```

### 4. Run Live Integration Tests
You can execute individual scripts, or run the complete test suite against the live endpoint using `uv run`:
```bash
INTEGRATION_TEST_MODE=live uv run python -m unittest tests/test_scenarios.py
```
*Watch your console display the real, live transactions with GCP in real-time!*
