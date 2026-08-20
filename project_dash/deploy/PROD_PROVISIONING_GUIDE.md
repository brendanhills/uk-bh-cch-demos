# 🚀 Production Environment (`monaro-risk-prod`) Provisioning & Operations Guide

This guide provides both **Click-Ops (Google Cloud Console)** and **CLI (Scripted)** instructions to provision, configure, and operate the production deployment of the **Project Monaro Risk Governance Platform** in Google Cloud Project **`monaro-risk-prod`** in the **Australian region (`australia-southeast1` — Sydney)**.

---

> [!CAUTION]
> ### 🚨 CRITICAL OPS TASK: 90-Day Temporary Project Expiration
> The `monaro-risk-prod` (and `monaro-risk-dev`) environments are currently provisioned as **90-day temporary Google Cloud sandbox projects**.
> * **Action Required**: A permanent Commonwealth / Project Monaro billing account MUST be attached to `monaro-risk-prod` in Pantheon Billing before the 90-day expiration window.
> * **Risk**: If a permanent billing account is not attached prior to day 90, Google Cloud will automatically suspend and delete all project resources, Cloud Run services, and Artifact Registry container images.

---

## 🏛️ Environment Invariants & System Matrix

| Parameter | Development (`dev`) | Production (`prod`) |
| :--- | :--- | :--- |
| **GCP Project ID** | `monaro-risk-dev` | **`monaro-risk-prod`** |
| **Deployment Region** | **`australia-southeast1`** (Sydney) | **`australia-southeast1`** (Sydney) |
| **Cloud Run Service Name** | `monaro-risk-dash-dev` | **`monaro-risk-dash-prod`** |
| **Active Git Branch** | `dev` | **`dev`** *(All code remains on `dev`)* |
| **Production Trigger Event** | Push to `dev` branch | **Push tag matching `^project_dash/prod-.*$`** |
| **Artifact Registry Repo** | `cloud-run-source-deploy` (Sydney) | `cloud-run-source-deploy` (Sydney) |
| **IAP Google SSO Group** | `monaro-risk-dev@google.com` | **`monaro-risk-prod@google.com`** |
| **Deployer Service Account** | `github-deployer@monaro-risk-dev...` | **`github-deployer@monaro-risk-prod...`** |
| **Live Data Sync Method** | In-Dashboard **"Sync Workspace"** | In-Dashboard **"Sync Workspace"** |

---

## 🧭 Quick Navigation: Google Cloud Console & Identity Directory

| Resource / Console | Development (`monaro-risk-dev`) | Production (`monaro-risk-prod`) | Global & Corp Links |
| :--- | :--- | :--- | :--- |
| **Live Deployed Dashboard** | [👉 Open Dev Dashboard](https://monaro-risk-dash-dev-525025654699.us-central1.run.app/) | [👉 Open Prod Dashboard](https://monaro-risk-dash-prod-525025654699.australia-southeast1.run.app/) | [Local Dev Server (Port 9000)](http://uk-bh-cloudtop.c.googlers.com:9000/?project=sample) |
| **Cloud Run Services** | [👉 Cloud Run (Dev)](https://pantheon.corp.google.com/run?project=monaro-risk-dev) | [👉 Cloud Run (Prod)](https://pantheon.corp.google.com/run?project=monaro-risk-prod) | — |
| **Cloud Build Triggers** | [👉 Build Triggers (Dev)](https://pantheon.corp.google.com/cloud-build/triggers?project=monaro-risk-dev) | [👉 Build Triggers (Prod)](https://pantheon.corp.google.com/cloud-build/triggers?project=monaro-risk-prod) | [Connected Repositories](https://pantheon.corp.google.com/cloud-build/repositories) |
| **Cloud Build History** | [👉 Build History (Dev)](https://pantheon.corp.google.com/cloud-build/builds?project=monaro-risk-dev) | [👉 Build History (Prod)](https://pantheon.corp.google.com/cloud-build/builds?project=monaro-risk-prod) | — |
| **Artifact Registry** | [👉 Docker Registry (Dev)](https://pantheon.corp.google.com/artifacts?project=monaro-risk-dev) | [👉 Docker Registry (Prod)](https://pantheon.corp.google.com/artifacts?project=monaro-risk-prod) | — |
| **Identity-Aware Proxy (IAP)** | [👉 IAP Access (Dev)](https://pantheon.corp.google.com/security/iap?project=monaro-risk-dev) | [👉 IAP Access (Prod)](https://pantheon.corp.google.com/security/iap?project=monaro-risk-prod) | [OAuth Consent Screen](https://pantheon.corp.google.com/apis/credentials/consent) |
| **IAM & Permissions** | [👉 IAM Permissions (Dev)](https://pantheon.corp.google.com/iam-admin/iam?project=monaro-risk-dev) | [👉 IAM Permissions (Prod)](https://pantheon.corp.google.com/iam-admin/iam?project=monaro-risk-prod) | — |
| **Service Accounts** | [👉 Service Accounts (Dev)](https://pantheon.corp.google.com/iam-admin/serviceaccounts?project=monaro-risk-dev) | [👉 Service Accounts (Prod)](https://pantheon.corp.google.com/iam-admin/serviceaccounts?project=monaro-risk-prod) | — |
| **Google Groups (Access Control)** | [👉 monaro-risk-dev@google.com](https://groups.google.com/a/google.com/g/monaro-risk-dev) | [👉 monaro-risk-prod@google.com](https://groups.google.com/a/google.com/g/monaro-risk-prod) | [Google Groups Home](https://groups.google.com) |
| **Nexus Portal & Ownership** | [👉 Nexus (monaro-risk-dev)](http://go/nexus) (`%monaro-risk-dev.prod`) | [👉 Nexus (monaro-risk-prod)](http://go/nexus) (`%monaro-risk-prod.prod`) | [go/nexus](http://go/nexus) & [go/idp](http://go/idp) |
| **Ganpati Groups (MDB)** | `%monaro-risk-dev.prod` | `%monaro-risk-prod.prod` | `%monaro-risk-admin.prod` |

## 👤 Operator Prerequisites: Required GCP IAM Roles

To perform the provisioning and administrative operations described in this guide, your Google corporate account (`<user>@google.com`) must be granted the following IAM roles on project **`monaro-risk-prod`**:

| Role Name | IAM Role Identifier | Purpose |
| :--- | :--- | :--- |
| **Project IAM Admin** | `roles/resourcemanager.projectIamAdmin` | Granting IAM roles to service accounts and groups |
| **Cloud Run Admin** | `roles/run.admin` | Managing services, revisions, and traffic routing |
| **Cloud Build Editor** | `roles/cloudbuild.builds.editor` | Creating and executing build triggers |
| **Artifact Registry Admin** | `roles/artifactregistry.admin` | Creating and managing container repositories |
| **IAP Admin** | `roles/iap.admin` | Configuring OAuth consent screen and IAP access |
| **Service Usage Admin** | `roles/serviceusage.serviceUsageAdmin` | Enabling required Google Cloud APIs |
| **Service Account Admin** | `roles/iam.serviceAccountAdmin` | Creating deployer service accounts |

---

## 🖱️ Method A: "Click-Ops" Provisioning via Google Cloud Console

If you prefer using the web browser UI (Pantheon), follow these sequential steps:

### Step 1: Enable APIs
1. Open **[APIs & Services > Library in `monaro-risk-prod`](https://pantheon.corp.google.com/apis/library?project=monaro-risk-prod)**.
2. Search and click **"Enable"** for each of the following 11 APIs:
   * `Cloud Build API` (`cloudbuild.googleapis.com`)
   * `Cloud Run Admin API` (`run.googleapis.com`)
   * `Artifact Registry API` (`artifactregistry.googleapis.com`)
   * `Identity-Aware Proxy (IAP) API` (`iap.googleapis.com`)
   * `Compute Engine API` (`compute.googleapis.com`)
   * `Vertex AI API` (`aiplatform.googleapis.com`)
   * `Container Analysis API` (`containeranalysis.googleapis.com`)
   * `Container Scanning API` (`containerscanning.googleapis.com`)
   * `Google Sheets API` (`sheets.googleapis.com`)
   * `Google Drive API` (`drive.googleapis.com`)
   * `Identity and Access Management (IAM) API` (`iam.googleapis.com`)

### Step 2: Create Artifact Registry Repository in Sydney
1. Open **[Artifact Registry > Repositories](https://pantheon.corp.google.com/artifacts?project=monaro-risk-prod)**.
2. Click **"+ CREATE REPOSITORY"**.
3. Set **Name**: `cloud-run-source-deploy`.
4. Set **Format**: `Docker`.
5. Set **Location type**: `Region` $\rightarrow$ Select **`australia-southeast1 (Sydney)`**.
6. Click **"CREATE"**.

### Step 3: Create Deployer Service Account & Assign Roles
1. Open **[IAM & Admin > Service Accounts](https://pantheon.corp.google.com/iam-admin/serviceaccounts?project=monaro-risk-prod)**.
2. Click **"+ CREATE SERVICE ACCOUNT"**.
3. Set **Service account name**: `github-deployer`.
4. Click **"CREATE AND CONTINUE"**.
5. In the **Grant this service account access to project** step, add the following roles:
   * `Cloud Run Admin` (`roles/run.admin`)
   * `Artifact Registry Administrator` (`roles/artifactregistry.admin`)
   * `Service Account User` (`roles/iam.serviceAccountUser`)
   * `IAP Policy Admin` (`roles/iap.admin`)
   * `Logs Writer` (`roles/logging.logWriter`)
   * `Storage Object Viewer` (`roles/storage.objectViewer`)
   * `Container Analysis Occurrences Editor` (`roles/containeranalysis.occurrences.editor`)
6. Click **"DONE"**.

### Step 4: Connect GitHub Repository to Cloud Build
1. Open **[Cloud Build > Repositories](https://pantheon.corp.google.com/cloud-build/repositories?project=monaro-risk-prod)**.
2. Click **"Connect Repository"**.
3. Select **GitHub (Cloud Build GitHub App)**.
4. Select repository: **`cloud-gtm/uk-bh-experiments`** and click **"Connect"**.

### Step 5: Create the Tag Release Trigger
1. Open **[Cloud Build > Triggers](https://pantheon.corp.google.com/cloud-build/triggers?project=monaro-risk-prod)**.
2. Click **"+ CREATE TRIGGER"**.
3. Fill in the trigger parameters:
   * **Name**: `deploy-monaro-risk-dash-prod`
   * **Event**: `Push new tag`
   * **Repository**: `cloud-gtm/uk-bh-experiments (GitHub)`
   * **Tag (regex)**: `^project_dash/prod-.*$`
   * **Configuration**: `Cloud Build configuration file (yaml or json)`
   * **Location**: `Repository` $\rightarrow$ File path: `project_dash/deploy/cloudbuild.yaml`
   * **Service Account**: `projects/monaro-risk-prod/serviceAccounts/github-deployer@monaro-risk-prod.iam.gserviceaccount.com`
   * **Advanced > Substitution variables**:
     * `_SERVICE_NAME` = `monaro-risk-dash-prod`
     * `_ACCESS_GROUP` = `monaro-risk-prod@google.com`
     * `_REGION` = `australia-southeast1`
     * `_IMAGE_NAME` = `monaro-risk-dash-prod`
4. Click **"CREATE"**.

---

## ⚡ Method B: Automated CLI Provisioning Script

Alternatively, execute this turnkey bash script in Cloud Shell or your workstation:

```bash
#!/bin/bash
set -euo pipefail

PROJECT_ID="monaro-risk-prod"
REGION="australia-southeast1"
SA_NAME="github-deployer"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "=== 1. Enabling GCP APIs for ${PROJECT_ID} ==="
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  iap.googleapis.com \
  compute.googleapis.com \
  aiplatform.googleapis.com \
  containeranalysis.googleapis.com \
  containerscanning.googleapis.com \
  sheets.googleapis.com \
  drive.googleapis.com \
  iam.googleapis.com \
  --project="${PROJECT_ID}"

echo "=== 2. Creating Dedicated Deployer Service Account ==="
if ! gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
  gcloud iam service-accounts create "${SA_NAME}" \
    --display-name="GitHub & Cloud Build Deployer" \
    --project="${PROJECT_ID}"
fi

echo "=== 3. Binding Least-Privilege IAM Roles ==="
ROLES=(
  "roles/run.admin"
  "roles/artifactregistry.admin"
  "roles/iam.serviceAccountUser"
  "roles/iap.admin"
  "roles/logging.logWriter"
  "roles/storage.objectViewer"
  "roles/containeranalysis.occurrences.editor"
)

for ROLE in "${ROLES[@]}"; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="${ROLE}" \
    --condition=None || true
done

echo "=== 4. Ensuring Artifact Registry Exists in ${REGION} ==="
gcloud artifacts repositories describe cloud-run-source-deploy \
  --location="${REGION}" \
  --project="${PROJECT_ID}" >/dev/null 2>&1 || \
gcloud artifacts repositories create cloud-run-source-deploy \
  --repository-format=docker \
  --location="${REGION}" \
  --description="Cloud Run source deployments" \
  --project="${PROJECT_ID}"

echo "=== 5. Creating Cloud Build Tag Trigger ==="
gcloud builds triggers create github \
  --project="${PROJECT_ID}" \
  --name="deploy-monaro-risk-dash-prod" \
  --repo-name="uk-bh-experiments" \
  --repo-owner="cloud-gtm" \
  --tag-pattern="^project_dash/prod-.*$" \
  --build-config="project_dash/deploy/cloudbuild.yaml" \
  --service-account="projects/${PROJECT_ID}/serviceAccounts/${SA_EMAIL}" \
  --substitutions="_SERVICE_NAME=monaro-risk-dash-prod,_ACCESS_GROUP=monaro-risk-prod@google.com,_REGION=${REGION},_IMAGE_NAME=monaro-risk-dash-prod" \
  --description="Automated Production Deployment on prod tags in Sydney" || true

echo "=== Setup complete for ${PROJECT_ID} in ${REGION}! ==="
```

---

## 🚀 How to Deploy a Production Release

All development occurs on the **`dev`** branch. To promote verified changes to production:

```bash
# 1. Create a release tag on the dev branch
git tag project_dash/prod-v1.0.0

# 2. Push the tag to GitHub
git push origin project_dash/prod-v1.0.0
```

*(Alternatively, draft a new Release in the GitHub web interface and publish tag `project_dash/prod-v1.0.0` on branch `dev`).*

Cloud Build will automatically:
1. Run the automated unit and ingestion test suite.
2. Inject build version tag and UTC timestamp into `data/build_info.json`.
3. Build the container image and push to Artifact Registry in Sydney.
4. Deploy to Cloud Run: **`monaro-risk-dash-prod`** in **`australia-southeast1`**.
5. Bind Identity-Aware Proxy (IAP) to **`monaro-risk-prod@google.com`**.

---

## 🔄 How End Users Update Live Data (Hands-Free)

1. Team members update Google Sheets or upload weekly PDF reports to Google Drive.
2. Open the live production dashboard in browser:
   👉 **`https://monaro-risk-dash-prod-<hash>.australia-southeast1.run.app/`**
3. Click **"Sync Workspace"** $\rightarrow$ **"Sync Live Data Now"**.
4. The Cloud Run backend (`/api/sync-all`) runs the ingestion pipeline and updates the view in real-time without requiring code rebuilds or terminal access.

---

## 🛠️ Critical Operations Runbooks

### Runbook 1: Roll Back to a Previous Release (Instant Traffic Shift)
If a newly deployed release has an issue, you can instantly shift 100% of live traffic back to the previous healthy revision in seconds:

* **Click-Ops (Console)**:
  1. Open **[Cloud Run > monaro-risk-dash-prod](https://pantheon.corp.google.com/run?project=monaro-risk-prod)**.
  2. Click the **"REVISIONS"** tab.
  3. Click **"MANAGE TRAFFIC"**.
  4. Select the previous healthy revision, set traffic to **100%**, and set the failing revision to **0%**.
  5. Click **"SAVE"**. Traffic shifts instantly with zero downtime.

* **CLI**:
  ```bash
  # List recent revisions
  gcloud run revisions list --service=monaro-risk-dash-prod --region=australia-southeast1 --project=monaro-risk-prod

  # Route 100% traffic to specific healthy revision
  gcloud run services update-traffic monaro-risk-dash-prod \
    --to-revisions=<HEALTHY_REVISION_NAME>=100 \
    --region=australia-southeast1 \
    --project=monaro-risk-prod
  ```

---

### Runbook 2: Restore an Older Release from Tag / Artifact Registry
To redeploy a specific historical version from a past git tag or container image:

* **Click-Ops (Console)**:
  1. Open **[Cloud Build > Triggers in `monaro-risk-prod`](https://pantheon.corp.google.com/cloud-build/triggers?project=monaro-risk-prod)**.
  2. Locate `deploy-monaro-risk-dash-prod` and click **"RUN"**.
  3. In the slide-out panel, select the historical **Tag** (e.g. `project_dash/prod-v1.0.0`).
  4. Click **"Run trigger"**.

* **CLI**:
  ```bash
  # Deploy specific historical commit image
  gcloud run deploy monaro-risk-dash-prod \
    --image=australia-southeast1-docker.pkg.dev/monaro-risk-prod/cloud-run-source-deploy/monaro-risk-dash-prod:<HISTORICAL_COMMIT_SHA> \
    --region=australia-southeast1 \
    --project=monaro-risk-prod
  ```

---

### Runbook 3: Emergency Shutdown / Shut Off the Server
To immediately stop serving all traffic in an emergency:

* **Click-Ops (Console)**:
  1. Open **[Cloud Run > monaro-risk-dash-prod](https://pantheon.corp.google.com/run?project=monaro-risk-prod)**.
  2. Click **"EDIT & DEPLOY NEW REVISION"**.
  3. Under **Scaling**, set **Maximum number of instances** to `0`.
  4. Click **"DEPLOY"**. Cloud Run will terminate all instances and cease serving requests.

* **CLI**:
  ```bash
  # Scale service to 0 instances
  gcloud run services update monaro-risk-dash-prod \
    --max-instances=0 \
    --region=australia-southeast1 \
    --project=monaro-risk-prod
  ```

*(To restore service after emergency, set `--max-instances=10` or use the Console to restore normal scaling).*

---

### Runbook 4: Maintenance Mode / Temporarily Revoke Access
To place the dashboard in maintenance mode so only admins have access:

* **Click-Ops (Console)**:
  1. Open **[Security > Identity-Aware Proxy](https://pantheon.corp.google.com/security/iap?project=monaro-risk-prod)**.
  2. Select `monaro-risk-dash-prod` under HTTPS Resources.
  3. In the right-hand panel, temporarily remove `group:monaro-risk-prod@google.com`.
  4. Only designated project admins retain access.

* **CLI**:
  ```bash
  # Remove general viewer group access
  gcloud beta iap web remove-iam-policy-binding \
    --project=monaro-risk-prod \
    --resource-type=cloud-run \
    --service=monaro-risk-dash-prod \
    --region=australia-southeast1 \
    --member="group:monaro-risk-prod@google.com" \
    --role="roles/iap.httpsResourceAccessor"
  ```

---

## 🔍 Diagnostics & Build Monitoring

To inspect build logs and status at any time from your terminal:
```bash
# Check production builds in Sydney
python3 scripts/check_build_status.py --env prod

# Check dev builds in Sydney
python3 scripts/check_build_status.py --env dev
```
