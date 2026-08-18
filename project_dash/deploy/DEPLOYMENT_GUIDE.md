# 🚀 Project Monaro Risk Dashboard — Automated CI/CD Deployment Guide

This guide documents the end-to-end, reproducible deployment procedure for the **Project Monaro Risk Dashboard** on **Google Cloud Run**, automated via **Google Cloud Build** triggers on GitHub push events, and secured with **Identity-Aware Proxy (IAP)** for seamless corporate Google SSO authentication.

---

## 🏗️ Architecture & Security Model

```mermaid
flowchart LR
    subgraph GitHub["GitHub (cloud-gtm/uk-bh-experiments)"]
        GitPush["Push to branch: dev\n(paths: project_dash/**)"]
    end

    subgraph CloudBuild["Google Cloud Build (monaro-risk-dev)"]
        Trigger["Trigger: deploy-monaro-risk-dash-dev"]
        Step1["1. Run Unit Tests (79 tests)"]
        Step2["2. Check/Create Artifact Registry"]
        Step3["3. Docker Build & Push"]
        Step4["4. Deploy to Cloud Run (--iap)"]
        Step5["5. Apply IAM & IAP Group Bindings"]
    end

    subgraph GCP["Google Cloud Platform"]
        AR["Artifact Registry\n(cloud-run-source-deploy)"]
        IAP["Identity-Aware Proxy (IAP)\n(Google SSO Login)"]
        CloudRun["Cloud Run Service\n(monaro-risk-dash-dev:8080)"]
    end

    subgraph Users["Authorized Users"]
        Browser["Chrome Browser\n(monaro-risk-dev@google.com)"]
    end

    GitPush --> Trigger
    Trigger --> Step1 --> Step2 --> Step3 --> Step4 --> Step5
    Step3 --> AR
    Step4 --> CloudRun
    Browser --> IAP --> CloudRun
```

### Environment Mapping

| Environment | GCP Project ID | Git Branch | Cloud Run Service Name | Cloud Build Trigger Name | Access Control Group |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Development** | `monaro-risk-dev` | `dev` | `monaro-risk-dash-dev` | `deploy-monaro-risk-dash-dev` | `monaro-risk-dev@google.com` |
| **Production** | `monaro-risk-prod` | `main` | `monaro-risk-dash` | `deploy-monaro-risk-dash-prod` | `monaro-risk-prod@google.com` |

---

## 📋 Step 1: GCP Project Initialization & Required APIs

Enable all required Google Cloud APIs for container build execution, artifact management, runtime hosting, identity proxying, logging, and storage:

```bash
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    containeranalysis.googleapis.com \
    logging.googleapis.com \
    iam.googleapis.com \
    iamcredentials.googleapis.com \
    iap.googleapis.com \
    cloudresourcemanager.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com \
    --project="monaro-risk-dev"
```

### API Reference Table

| API Name | Service Identifier | Purpose / Why Needed |
| :--- | :--- | :--- |
| **Cloud Run Admin API** | `run.googleapis.com` | Manages Cloud Run service lifecycles and revisions. |
| **Cloud Build API** | `cloudbuild.googleapis.com` | Orchestrates automated CI/CD container build pipelines. |
| **Artifact Registry API** | `artifactregistry.googleapis.com` | Stores and manages versioned Docker container images. |
| **Cloud Logging API** | `logging.googleapis.com` | Ingests build logs, access logs, and container stdout/stderr. |
| **Identity and Access Management (IAM) API** | `iam.googleapis.com` | Manages service accounts, roles, and resource policies. |
| **IAM Service Account Credentials API** | `iamcredentials.googleapis.com` | Handles short-lived token generation and OIDC auth. |
| **Cloud Identity-Aware Proxy (IAP) API** | `iap.googleapis.com` | Enforces corporate Google SSO login at the edge. |
| **Cloud Resource Manager API** | `cloudresourcemanager.googleapis.com` | Sets and verifies project-level and resource-level IAM policies. |
| **Cloud Storage API** | `storage.googleapis.com` | Backing store for Cloud Build artifacts and source staging. |
| **Secret Manager API** | `secretmanager.googleapis.com` | Secure storage and access for sensitive credentials/keys. |

---

## 👤 Step 2: Dedicated Service Account Setup

Cloud Build runs under a dedicated Service Account (`github-deployer@<PROJECT_ID>.iam.gserviceaccount.com`) with the permissions required to build images, push to Artifact Registry, deploy to Cloud Run, manage IAP bindings, and write build telemetry.

### 1. Create the Service Account:
```bash
gcloud iam service-accounts create github-deployer \
    --description="Cloud Build trigger execution service account" \
    --display-name="GitHub Deployer" \
    --project="monaro-risk-dev"
```

### 2. Grant Required IAM Roles:
Assign all required roles to `github-deployer@monaro-risk-dev.iam.gserviceaccount.com`:

```bash
SA_EMAIL="github-deployer@monaro-risk-dev.iam.gserviceaccount.com"
PROJECT_ID="monaro-risk-dev"

# 1. Cloud Run Deployment & Service Management
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/run.admin"

# 2. Artifact Registry Docker Image Creation & Push
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/artifactregistry.admin"

# 3. Cloud Build Execution & Trigger Management
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudbuild.builds.editor"

# 4. Act as the Runtime Service Account Identity
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/iam.serviceAccountUser"

# 5. Write Execution Logs to Cloud Logging
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/logging.logWriter"

# 6. Manage Cloud Storage Source & Build Cache Buckets
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.admin"

# 7. Manage Identity-Aware Proxy (IAP) Policies
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/iap.admin"
```

---

## 🔗 Step 3: Connect GitHub to Google Cloud Build

> [!NOTE]
> Use standard **Cloud Build Repositories (GitHub App)** rather than Developer Connect to avoid cross-organization OAuth redirection issues.

1. In Pantheon, open **[Cloud Build > Repositories (1st gen)](https://pantheon.corp.google.com/cloud-build/repositories/1st-gen?project=monaro-risk-dev)**.
2. Click **"CONNECT REPOSITORY"**.
3. Select source: **GitHub (Cloud Build GitHub App)**.
4. Authorize Google Cloud Build to access your GitHub organization/account (`cloud-gtm`).
5. Select repository: **`cloud-gtm/uk-bh-experiments`**.
6. Check the box agreeing to terms and click **"Connect"**.

---

## ⚡ Step 4: Create the Automated Cloud Build Trigger

Create a trigger that runs automated tests and deploys whenever files inside `project_dash/**` are pushed to the `dev` branch:

1. Open **[Cloud Build > Triggers](https://pantheon.corp.google.com/cloud-build/triggers?project=monaro-risk-dev)**.
2. Click **"CREATE TRIGGER"**.
3. Configure the trigger settings:
   * **Name**: `deploy-monaro-risk-dash-dev`
   * **Region**: `global` (or `us-central1`)
   * **Event**: `Push to a branch`
   * **Source**:
     * **Repository**: `cloud-gtm/uk-bh-experiments (github)`
     * **Branch**: `^dev$`
   * **Included files filter (glob)**:
     ```
     project_dash/**
     ```
   * **Configuration**:
     * **Type**: `Cloud Build configuration file (yaml or json)`
     * **Location**: `Repository`
     * **Cloud Build configuration file location**: `project_dash/deploy/cloudbuild.yaml`
   * **Advanced > Service Account**:
     * Select `github-deployer@monaro-risk-dev.iam.gserviceaccount.com`
4. Click **"Create"**.

---

## 📦 Step 5: The Automated CI/CD Pipeline (`cloudbuild.yaml`)

The pipeline definition is stored in [`project_dash/deploy/cloudbuild.yaml`](file:///usr/local/google/home/brendanhills/dev/uk-bh-experiments/project_dash/deploy/cloudbuild.yaml). It executes 6 automated stages:

```yaml
steps:
  # 1. Run Automated Unit & Ingestion Tests
  - name: 'python:3.13-slim'
    dir: 'project_dash'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install --no-cache-dir -r requirements.txt
        python3 -m unittest discover -s tests -p "test_*.py"

  # 2. Ensure Artifact Registry repository exists (Idempotent)
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        gcloud artifacts repositories describe cloud-run-source-deploy --location=us-central1 --project=$PROJECT_ID || \
        gcloud artifacts repositories create cloud-run-source-deploy --repository-format=docker --location=us-central1 --description="Cloud Run source deployments" --project=$PROJECT_ID

  # 3. Build Container Image using Custom Multi-Stage Dockerfile
  - name: 'gcr.io/cloud-builders/docker'
    dir: 'project_dash'
    args:
      - 'build'
      - '-f'
      - 'deploy/Dockerfile'
      - '-t'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/monaro-risk-dash-dev:$COMMIT_SHA'
      - '-t'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/monaro-risk-dash-dev:latest'
      - '.'

  # 4. Push Container Image to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/monaro-risk-dash-dev:$COMMIT_SHA'

  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/monaro-risk-dash-dev:latest'

  # 5. Deploy to Cloud Run (Private Mode + Native IAP Enabled)
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'monaro-risk-dash-dev'
      - '--image'
      - 'us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/monaro-risk-dash-dev:$COMMIT_SHA'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
      - '--no-allow-unauthenticated'
      - '--iap'
      - '--port'
      - '8080'

  # 6. Enforce IAM Invoker and IAP SSO Access Policies via CLI
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        # 1. Grant Cloud Run Invoker to IAP Service Agent
        gcloud run services add-iam-policy-binding monaro-risk-dash-dev \
          --project=$PROJECT_ID \
          --region=us-central1 \
          --member="serviceAccount:service-$PROJECT_NUMBER@gcp-sa-iap.iam.gserviceaccount.com" \
          --role="roles/run.invoker" || true

        # 2. Grant Cloud Run Invoker to allowlisted groups and leads
        gcloud run services add-iam-policy-binding monaro-risk-dash-dev \
          --project=$PROJECT_ID \
          --region=us-central1 \
          --member="group:monaro-risk-dev@google.com" \
          --role="roles/run.invoker" || true

        gcloud run services add-iam-policy-binding monaro-risk-dash-dev \
          --project=$PROJECT_ID \
          --region=us-central1 \
          --member="group:monaro-risk-dev@twosync.google.com" \
          --role="roles/run.invoker" || true

        gcloud run services add-iam-policy-binding monaro-risk-dash-dev \
          --project=$PROJECT_ID \
          --region=us-central1 \
          --member="user:brendanhills@google.com" \
          --role="roles/run.invoker" || true

        gcloud run services add-iam-policy-binding monaro-risk-dash-dev \
          --project=$PROJECT_ID \
          --region=us-central1 \
          --member="user:allins@google.com" \
          --role="roles/run.invoker" || true

        # 3. Grant IAP-secured Web App User role using gcloud beta iap web
        gcloud beta iap web add-iam-policy-binding \
          --project=$PROJECT_ID \
          --resource-type="cloud-run" \
          --service="monaro-risk-dash-dev" \
          --region="us-central1" \
          --member="group:monaro-risk-dev@google.com" \
          --role="roles/iap.httpsResourceAccessor"

        gcloud beta iap web add-iam-policy-binding \
          --project=$PROJECT_ID \
          --resource-type="cloud-run" \
          --service="monaro-risk-dash-dev" \
          --region="us-central1" \
          --member="group:monaro-risk-dev@twosync.google.com" \
          --role="roles/iap.httpsResourceAccessor"

        gcloud beta iap web add-iam-policy-binding \
          --project=$PROJECT_ID \
          --resource-type="cloud-run" \
          --service="monaro-risk-dash-dev" \
          --region="us-central1" \
          --member="user:brendanhills@google.com" \
          --role="roles/iap.httpsResourceAccessor"

        gcloud beta iap web add-iam-policy-binding \
          --project=$PROJECT_ID \
          --resource-type="cloud-run" \
          --service="monaro-risk-dash-dev" \
          --region="us-central1" \
          --member="user:allins@google.com" \
          --role="roles/iap.httpsResourceAccessor"

images:
  - 'us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/monaro-risk-dash-dev:$COMMIT_SHA'
  - 'us-central1-docker.pkg.dev/$PROJECT_ID/cloud-run-source-deploy/monaro-risk-dash-dev:latest'

options:
  logging: CLOUD_LOGGING_ONLY
```

---

## 🚀 Step 6: Everyday Developer Workflow

Deployment and access policy binding are completely hands-free:

```bash
# 1. Edit code or data files under project_dash/
# 2. Run local unit tests to verify
python3 -m unittest discover -s project_dash/tests -p "test_*.py"

# 3. Commit and push to the dev branch
git add project_dash/
git commit -m "feat: update risk dashboard calculations and UI layout"
git push origin dev
```

Cloud Build automatically triggers, runs tests, creates the container, deploys with `--iap`, and programmatically enforces `roles/iap.httpsResourceAccessor` for `group:monaro-risk-dev@google.com` and designated technical leads.

* 👉 **Track Build Status**: [Cloud Build History](https://pantheon.corp.google.com/cloud-build/builds?project=monaro-risk-dev)
* 👉 **Access Dashboard**: [Live Service URL](https://monaro-risk-dash-dev-525025654699.us-central1.run.app/)

---

## 🔧 Production Replication (`monaro-risk-prod`)

To onboard the production environment, follow the exact same steps substituting:
* **GCP Project**: `monaro-risk-prod`
* **Git Branch**: `main`
* **Cloud Run Service**: `monaro-risk-dash`
* **Trigger Name**: `deploy-monaro-risk-dash-prod`
* **Access Group**: `monaro-risk-prod@google.com`

---

## 💡 Troubleshooting & Common Gotchas Resolved

| Issue Encountered | Root Cause | Permanent Resolution |
| :--- | :--- | :--- |
| **`FileNotFoundError` during Cloud Build tests** | Tests had hardcoded Cloudtop absolute paths (`/usr/local/google/...`). | Replaced with dynamic relative paths `os.path.join(os.path.dirname(__file__), "..", ...)`. |
| **`FileNotFoundError: 'node'` during build** | `test_presentation_decoupling.py` assumed `node` binary was installed on worker. | Made `node` execution conditional on `shutil.which('node')`. |
| **`Repository "cloud-run-source-deploy" not found`** | Artifact Registry repository must be initialized before `docker push`. | Added Step 2 in `cloudbuild.yaml` to auto-check/create repo idempotently. |
| **Missing `roles/logging.logWriter`** | Custom Service Account lacked permission to write build logs. | Granted `roles/logging.logWriter` to `github-deployer@...`. |
| **`403 Forbidden` on `.run.app` in browser** | `--no-allow-unauthenticated` rejects browser requests lacking OIDC token. | Enabled `--iap` on Cloud Run and granted `roles/iap.httpsResourceAccessor`. |
| **Pantheon UI Validation Warning on Group** | Pantheon client-side form validator fails to resolve internal groups in the UI. | Bound directly via Cloud Build using `gcloud iap web add-iam-policy-binding --member="group:monaro-risk-dev@google.com"`. |
