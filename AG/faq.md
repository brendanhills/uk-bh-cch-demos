# NotebookLM Enterprise API: Architectural & Behavioral FAQ

Welcome to the Internal Technical Sandbox Reference & FAQ for Google NotebookLM Enterprise (built on the Google Cloud Discovery Engine platform). This document consolidates our core findings, engineering constraints, and administrative recovery protocols discovered during our team's developer deep-dive.

---

## 🗺️ Table of Contents
1. [Platform Architecture & Location Constraints](#1-platform-architecture--location-constraints)
2. [Identity & Access Management (IAM) Roles](#2-identity--access-management-iam-roles)
3. [Resource Discovery & Cataloging](#3-resource-discovery--cataloging)
4. [Resource Ownership & The Cloning Handover Pattern](#4-resource-ownership--the-cloning-handover-pattern)
5. [Sharing Boundaries & Cross-Domain Constraints](#5-sharing-boundaries--cross-domain-constraints)
6. [Future Development & Validation Tracks](#6-future-development--validation-tracks)

---

## 1. Platform Architecture & Location Constraints

### Q: What is the underlying engine behind NotebookLM Enterprise?
NotebookLM Enterprise does not run on custom independent servers; it is a specialized service layer built on top of **Google Cloud Discovery Engine** (`discoveryengine.googleapis.com`). All REST endpoints, schemas, and resource paths are managed as Discovery Engine sub-resources:
`projects/{PROJECT_NUMBER}/locations/{LOCATION}/notebooks`

### Q: What location constraints and subdomain errors exist?
Google Cloud Discovery Engine enforces a strict regional matching rule. If you are interacting with resources in a specific region, your API subdomain and request path location MUST align perfectly:

1. **Subdomain-Path Alignment Rules**:
   - **Regional Locations (e.g., `us` or `eu`)**: If your request path is `locations/us`, you must call `https://us-discoveryengine.googleapis.com/...`.
   - **Global Location (`global`)**: If your request path is `locations/global`, you must omit the regional prefix and call `https://discoveryengine.googleapis.com/...`.

2. **Location Mismatch Errors (HTTP 400)**:
   > [!CAUTION]
   > Any misalignment—such as sending a request containing `locations/global` in the path to the `us-discoveryengine.googleapis.com` subdomain, or vice versa—will cause the Google Cloud API gateway to immediately reject the request with an **HTTP 400 Bad Request (Location Mismatch)** error.

### Q: What are the two API hosts used by the SDK?
Depending on whether you are querying metadata or uploading raw local binaries, the SDK routes traffic to two different subdomains:
1. **Metadata & Management Endpoint**:
   `https://{LOCATION}-discoveryengine.googleapis.com/v1alpha`
2. **Binary File Ingestion Endpoint**:
   `https://{LOCATION}-discoveryengine.googleapis.com/upload/v1alpha`

---

## 2. Identity & Access Management (IAM) Roles

### Q: Can I use standard Vertex AI roles to administer NotebookLM?
> [!WARNING]
> **No.** Standard Vertex AI roles (such as "Vertex AI Administrator" or "Notebooks Admin") are designed for Jupyter Notebook VMs and Vertex AI pipelines. They do **not** grant any permissions over NotebookLM Enterprise resources.

### Q: What are all the NotebookLM-related IAM roles and their differences?
NotebookLM Enterprise features several predefined IAM roles under the Discovery Engine service namespace, divided into **Service-Level Access Roles** and **Notebook-Level Access Roles**:

| Predefined IAM Role Name | Predefined Role ID | Type | Description / Scope |
| :--- | :--- | :--- | :--- |
| **Cloud NotebookLM Admin** | `roles/discoveryengine.notebookLmOwner` | Service-Level | Allows configuring organization-wide identity settings, managing user access to NotebookLM, and accessing administrative dashboards. |
| **Cloud NotebookLM User** | `roles/discoveryengine.notebookLmUser` | Service-Level | Grants the standard permissions required to sign in to the user interface, view shared notebooks, and create new notebooks. |
| **Cloud NotebookLM Notebook Owner** | `roles/discoveryengine.notebookOwner` | Notebook-Level | Grants full ownership privileges (read, write, delete, share) over a *specific* Cloud NotebookLM Notebook. |
| **Cloud NotebookLM Notebook Editor** | `roles/discoveryengine.notebookEditor` | Notebook-Level | Grants modification and editor privileges (read, write) over a *specific* Cloud NotebookLM Notebook. |
| **Cloud NotebookLM Notebook Viewer** | `roles/discoveryengine.notebookViewer` | Notebook-Level | Grants read-only privileges over a *specific* Cloud NotebookLM Notebook. |
| **Gemini Enterprise Admin** | `roles/discoveryengine.agentspaceAdmin` | Auditing | Required for administrative accounts to enable and access organization-wide NotebookLM usage audit logs. |

> [!NOTE]
> Service-Level roles are typically managed in the Google Cloud Console IAM page. Notebook-Level roles are automatically mapped and applied to users through the user interface when notebooks are created or shared, and are not intended for manual management in the GCP IAM Console.

### Q: How do Project-Level IAM permissions interact with Notebook-Level ACLs?
NotebookLM maintains internal Access Control Lists (ACLs) to determine who can see notebooks in the consumer Web UI. However:
1. **Regular Users** are bound strictly by the ACLs. If a notebook isn't shared with them, they cannot see or read it.
2. **Project Administrators** with the `roles/discoveryengine.admin` role bypass the ACL check at the API level. Even if they are not explicitly added to the notebook's share settings, they can run `get`, `delete`, or `clone` on any notebook using its exact GUID.

---

## 3. Resource Discovery & Cataloging

### Q: Why does the standard `list` command only return notebooks I have opened?
The underlying GET endpoint used by the API is `:listRecentlyViewed`:
`GET .../locations/{LOCATION}/notebooks:listRecentlyViewed`

This endpoint operates as a **personal recency timeline** rather than a database catalog:
* It only lists notebooks that the *currently authenticated caller* has explicitly created or opened.
* It is restricted to a personal interaction log (capped at 500 items).

### Q: Is there a project-wide catalog endpoint to list *all* corporate notebooks?
> [!IMPORTANT]
> **No.** The standard collection-level list endpoint `GET .../locations/{LOCATION}/notebooks` is completely **unimplemented** by Google Cloud Discovery Engine. Attempting to query it will return an error or empty results.
> Because `:listRecentlyViewed` is strictly user-scoped, an Administrator running `list` will only see notebooks *they* have opened. If a departed employee created a notebook and never shared it with the Admin, that notebook **will not show up** in the Admin's `list` output.

---

## 4. Resource Ownership & The Cloning Handover Pattern

### Q: Why can't I change the owner of an existing notebook?
In Google Cloud Discovery Engine, **primary resource ownership is immutable**. The platform permanently binds the creation of the notebook and its underlying metadata to the unique identity (Workspace account) of the user who originally created it. Even if you share a notebook with a new owner, the original creator remains marked as the owner in the system.

### Q: Why does revoking the creator's access via `PROJECT_ROLE_NOT_SHARED` fail?
If you attempt to run:
```bash
uv run nblm_api.py share <NOTEBOOK_ID> "departed_user@company.com" PROJECT_ROLE_NOT_SHARED
```
The live API will reject the request with `400 INVALID_ARGUMENT` (Bad Request). 
* The API enforces a constraint that the **original creator must always retain full owner/writer access**.
* **Mitigation**: You do not need to manually unshare the departed employee. Suspending or deleting their corporate Google Workspace account automatically revokes their active session and blocks their access to all GCP resources.

### Q: What is the recommended mechanism for transferring ownership?
Since ownership is immutable, the recommended mechanism for handover is the **Cloning Pattern**:
1. An administrator uses their project-level IAM credentials to retrieve the orphaned notebook.
2. The administrator (or the designated new owner) runs the `clone` command under their own active credentials.
3. This creates a brand new notebook where the caller is the primary creator/owner.
4. The old notebook is then safely deleted.

```bash
# Clone an orphaned notebook to assume primary ownership
uv run nblm_api.py clone <NOTEBOOK_ID> --title "My Recovered Notebook"
```

### Q: How does the programmatic notebook cloning process behave?
When cloning a notebook, the programmatic tool:
1. Creates a fresh destination notebook under the caller's active credentials.
2. Programmatically re-ingests and clones any Webpage sources (retaining their original URLs via `webpageMetadata.webpageUrl`).
3. Gathers and flags any non-replicable sources (such as uploaded files, raw text blocks, Google Docs, or Google Drive files), returning them as `non_replicable_sources` so the user or administrative script can handle re-upload.

### Q: Why can't the API clone files or raw text sources programmatically?
> [!IMPORTANT]
> Google Cloud Discovery Engine's REST API is **strictly ingestion-only** for files and raw text. 
> * Once a PDF, document, or raw text string is ingested and processed by NotebookLM, the raw source payload is immediately converted into vectorized search representations and LLM embeddings.
> * The REST API does **not** provide any endpoint to download or read back the original raw binary stream or full-text payload of an existing source.
> * **Mitigation**: When cloning, the SDK identifies these sources, alerts the user, and prints a warning instructing them to re-upload the raw assets to the newly cloned notebook.

---

## 5. Sharing Boundaries & Cross-Domain Constraints

### Q: What is "Silenced Owner Elevation" (Cross-Domain Sharing)?
If you attempt to share a notebook as `PROJECT_ROLE_OWNER` with a user across a Google Workspace domain boundary (e.g., from `yourcompany.com` to `external-consultant.com`):
* The API will respond with `200 OK`.
* However, Google's cross-domain security policies will **silently ignore** the owner elevation or map the recipient down to a standard collaborator (`PROJECT_ROLE_WRITER`) status.
* **Best Practice**: Always keep administrative handovers and ownership transfers within the same Google Workspace domain boundary.

---

## 6. Future Development & Validation Tracks

These items represent untested hypotheses and engineering proposals for future system automation and validation:

### 🔬 Untested Hypothesis: Discovery via Cloud Audit Logs
* **The Hypothesis**: We hypothesize that all query and creation events for `discoveryengine.googleapis.com` are published to Google Cloud Audit Logs. If verified, this would allow an administrator to query Cloud Logging for `CreateNotebook` or `GetNotebook` transactions to extract the unique notebook IDs and creator emails across the entire project.
* **Proposed Future Track**: Run an integration campaign to verify that these audit logs record all relevant events, and validate that they contain the required GUID metadata.

### 🤖 Proposed Agentic / Scripted Automation
* **The Proposal**: Since there is no project-wide `list` endpoint, we propose developing a custom Python administration script or a specialized **Gemini Engine (GE) Agent**.
* **Automation Behavior**: The script/agent would periodically query the Google Cloud Logging API (using the verified Audit Logs track above) to index and catalog all active notebook IDs in the organization, creating a central catalog database to automatically alert administrators about orphaned or unshared notebooks.
