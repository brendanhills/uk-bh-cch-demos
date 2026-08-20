# 🚀 Production Environment (`monaro-risk-prod`) Turnkey Provisioning Guide

This guide provides the complete, copy-paste instructions to provision and operate the production deployment of the **Project Monaro Risk Governance Dashboard** in Google Cloud Project **`monaro-risk-prod`** in the **Australian region (`australia-southeast1`)**.

---

## 🏛️ Environment Invariants

* **GCP Project ID**: `monaro-risk-prod`
* **Region**: `australia-southeast1` (Sydney, Australia)
* **Cloud Run Service Name**: `monaro-risk-dash-prod`
* **Artifact Registry Repository**: `cloud-run-source-deploy` (Region: `australia-southeast1`)
* **IAP Access Group (Viewers & Stakeholders)**: `monaro-risk-prod@google.com`
* **Nexus Project Owner**: `%monaro-risk-prod.prod` (or `%monaro-risk-admin.prod`)
* **Trigger Mechanism**: Release Tags on `dev` branch matching `^project_dash/prod-.*$`

---

## 🛠️ Step 1: Project Provisioning in Nexus / C4A IDP

1. Open **[C4A IDP Portal (go/idp)](http://go/idp)** or **[Nexus Portal](http://go/nexus)**.
2. Create or verify Project:
   * **Project ID**: `monaro-risk-prod`
   * **Project Title**: `Monaro Risk Governance Platform (Production)`
   * **Owner Group**: `%monaro-risk-prod.prod` (or `%monaro-risk-admin.prod`)
   * **Billing Account**: Assign Commonwealth / Project Monaro production billing account.

---

## ⚡ Step 2: Automated GCP Services & IAM Provisioning Script

Run the following script to enable the 11 required GCP APIs, create the dedicated deployer service account, and assign least-privilege IAM roles:

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
  echo "Granting ${ROLE}..."
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

echo "=== Setup complete for ${PROJECT_ID} in ${REGION}! ==="
```

---

## 🔗 Step 3: Connect GitHub Repository to Cloud Build

1. Open **[Cloud Build > Repositories in `monaro-risk-prod`](https://pantheon.corp.google.com/cloud-build/repositories?project=monaro-risk-prod)**.
2. Click **"Connect Repository"**.
3. Select **GitHub (Cloud Build GitHub App)**.
4. Authenticate and select repository: **`cloud-gtm/uk-bh-experiments`**.

---

## 🎯 Step 4: Create the Production Tag Release Trigger

Create the trigger via `gcloud` CLI or via Pantheon:

```bash
gcloud builds triggers create github \
  --project="monaro-risk-prod" \
  --name="deploy-monaro-risk-dash-prod" \
  --repo-name="uk-bh-experiments" \
  --repo-owner="cloud-gtm" \
  --tag-pattern="^project_dash/prod-.*$" \
  --build-config="project_dash/deploy/cloudbuild.yaml" \
  --service-account="projects/monaro-risk-prod/serviceAccounts/github-deployer@monaro-risk-prod.iam.gserviceaccount.com" \
  --substitutions="_SERVICE_NAME=monaro-risk-dash-prod,_ACCESS_GROUP=monaro-risk-prod@google.com,_REGION=australia-southeast1,_IMAGE_NAME=monaro-risk-dash-prod" \
  --description="Automated Production Deployment for Project Monaro Risk Dashboard in Sydney on prod tags"
```

---

## 🚀 Step 5: How to Deploy a Production Release

All development occurs on the **`dev`** branch. To promote verified changes to production:

```bash
# 1. Create a release tag on the dev branch
git tag project_dash/prod-v1.0.0

# 2. Push the tag to GitHub
git push origin project_dash/prod-v1.0.0
```

*(Alternatively, draft a new Release in the GitHub web interface and publish tag `project_dash/prod-v1.0.0` on branch `dev`).*

Cloud Build will automatically:
1. Run the 103 unit and ingestion tests.
2. Build the container image.
3. Deploy to Cloud Run: **`monaro-risk-dash-prod`** in **`australia-southeast1`**.
4. Bind Identity-Aware Proxy (IAP) to **`monaro-risk-prod@google.com`**.

---

## 🔄 Step 6: How End Users Update Live Data (Hands-Free)

1. Team members update Google Sheets or add weekly PDF reports to Google Drive.
2. Open the live production dashboard:
   👉 **`https://monaro-risk-dash-prod-<hash>.australia-southeast1.run.app/`**
3. Click **"Sync Workspace"** $\rightarrow$ **"Sync Live Data Now"**.
4. The Cloud Run backend runs the live ingestion pipeline and updates the view in real-time without requiring a code rebuild or terminal access.

---

## 🔍 Diagnostics & Build Monitoring

To check production build health from your terminal at any time:
```bash
# Check production build status
python3 scripts/check_build_status.py --env prod

# Check dev build status
python3 scripts/check_build_status.py --env dev
```
