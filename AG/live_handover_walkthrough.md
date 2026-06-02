# Live Handover & Recovery Testing Guide
This document provides a step-by-step walkthrough for validating the administrative offboarding and resource recovery flow in **live Google Cloud Discovery Engine (NotebookLM Enterprise)** mode.

---

## 📋 Scenario Overview
1. **User A (Alice)** is hired, assigned standard NotebookLM privileges, and creates a critical business notebook.
2. **Alice** shares the notebook with **User B (Bob / You)** as a writer/editor.
3. **Alice** departs the company, and her Google Workspace account is suspended/deleted.
4. **Administrator (You)** accesses the orphaned notebook, verifies content integrity, and assumes full control of the resource using project-level IAM credentials.

---

## 🛠️ Prerequisite Configuration

To prevent standard users from possessing dangerous project-wide permissions (like primitive Project Owner/Editor roles), grant them the minimum necessary access to use NotebookLM:

1. **For Alice (`alicenb@brendanhills.altostrat.com`):**
   * Go to the **IAM & Admin** page in the Google Cloud Console.
   * Add a principal for Alice's email.
   * Grant her the **Cloud NotebookLM User** role (`roles/discoveryengine.notebookLmUser`).
2. **For Yourself / Administrator (`brendan@brendanhills.altostrat.com`):**
   * Ensure your principal has the **Discovery Engine Admin** (`roles/discoveryengine.admin`) or **Cloud NotebookLM Admin** (`roles/discoveryengine.notebookLmOwner`) role.

> [!NOTE]
> Do **not** use the standard Vertex AI "Notebooks Admin" or "Notebooks Editor" roles. Those are reserved for Jupyter notebook VMs (`notebooks.googleapis.com`) and do not apply to NotebookLM Enterprise (`discoveryengine.googleapis.com`).

---

## 🚀 Step-by-Step Execution Plan

### Part 1: Swapping to Alice & Creating the Notebook

1. **Switch your active terminal identity to Alice:**
   ```bash
   uv run setup_env.py alicenb
   ```
   *Since Alice is unauthenticated, the script will pause, display an interactive message, and open your web browser. Authenticate as `alicenb@brendanhills.altostrat.com` to proceed.*

2. **Alice creates a new corporate notebook:**
   ```bash
   uv run nblm_api.py create "Core Systems Blueprint"
   ```
   *Note the **Notebook ID** printed at the very end of the output (e.g., `a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d`).*

3. **Alice adds a secret text content source:**
   ```bash
   uv run nblm_api.py add-source <NOTEBOOK_ID> text "System Overview" "This contains crucial systems engineering secrets and private system access details."
   ```

4. **Alice shares the notebook with you (Bob) as a collaborator:**
   ```bash
   uv run nblm_api.py share <NOTEBOOK_ID> "brendan@brendanhills.altostrat.com" PROJECT_ROLE_WRITER
   ```

---

### Part 2: Simulating Alice's Departure

1. Open your **Google Workspace Admin Console**.
2. Find `alicenb@brendanhills.altostrat.com`.
3. **Suspend or Delete** her account. 
   *(Alice's active OAuth2 access tokens and Workspace login sessions are now permanently revoked).*

---

### Part 3: Recovering the Notebook as Administrator

1. **Restore your active terminal identity back to yourself:**
   ```bash
   uv run setup_env.py brendan
   ```
   *This switches the active account configuration back to `brendan@brendanhills.altostrat.com` and automatically refreshes your `.env` session token.*

2. **Retrieve and verify the orphaned notebook:**
   ```bash
   uv run nblm_api.py get <NOTEBOOK_ID>
   ```
   *Because you are a Project Owner / Discovery Engine Admin, your project-level permissions override individual ACL sharing blocks. You will successfully retrieve the notebook and see Alice's added source `"System Overview"`, confirming full, seamless administrative recovery.*

3. **Programmatically Transfer Ownership via Cloning:**
   Since Google Cloud Discovery Engine permanently binds resource creation metadata to the original creator, standard ownership is immutable. To perform a clean ownership transfer, the Admin (or new owner) can clone the notebook under their own active credentials:
   ```bash
   uv run nblm_api.py clone <NOTEBOOK_ID> --title "Core Systems Blueprint - Brendan's Copy"
   ```
   *This creates a fresh notebook where **you** are the sole primary owner. All webpage sources are programmatically cloned and re-ingested. Any local files or raw text sources will be listed as non-replicable (since Discovery Engine's REST API is strictly ingestion-only), instructing you to re-upload them.*

4. **Clean up the original test resource (Optional):**
   ```bash
   uv run nblm_api.py delete <NOTEBOOK_ID>
   ```

---

## 💡 Troubleshooting & Behavioral Insights

### Why does setting an owner to `PROJECT_ROLE_NOT_SHARED` return a `400 Bad Request`?
If you attempt to run:
```bash
uv run nblm_api.py share <NOTEBOOK_ID> "alicenb@brendanhills.altostrat.com" PROJECT_ROLE_NOT_SHARED
```
while Alice is the original creator, the live GCP API will reject it with `400 INVALID_ARGUMENT`. This is expected behavior:
* A notebook must **always** have an active primary owner (the creator), and the API blocks you from revoking the creator's access.
* In a real offboarding scenario, you do not need to explicitly "unshare" the departed employee from their own notebook because suspending their Workspace account automatically terminates their access to all GCP resources.

### Silenced Owner Elevation (Cross-Domain Constraint)
If you attempt to share a notebook as `PROJECT_ROLE_OWNER` to a collaborator across a Google Workspace domain boundary (e.g., sharing a `brendanhills.altostrat.com` notebook to a `brendanhills@altostrat.com` email address), Google's security policies will accept the command with `200 OK` but silently ignore the owner elevation or map it to a standard Editor (`PROJECT_ROLE_WRITER`) status. Always keep operations in-domain when performing ownership tests.
