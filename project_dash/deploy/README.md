# F-DSE Dashboard Deployment & Operations Pipeline

This directory contains deployment pipelines and service shutdown controls for the **F-DSE Risk Intelligence Platform**.

---

## ⚙️ Configuration (`.env`)

Configure your authorized **Dashboard Viewers** (Google Groups and individual users), blocked domains, and GCP project settings in your root `.env` file (copied from `.env.example`):

```bash
# --- Cloud Run Deployment Configuration ---
GCP_PROJECT_ID="uk-bh-experiments-argolis"
GCP_REGION="us-central1"
GCP_SERVICE_NAME="f-dse-risk-dashboard-private"

# --- Dashboard Viewer Access Control (IAM roles/run.invoker) ---
# DASHBOARD_VIEWER_GROUPS: Google Groups granted viewer access to the dashboard
DASHBOARD_VIEWER_GROUPS="your-team-group@google.com"

# DASHBOARD_VIEWER_USERS: Individual user accounts granted viewer access
DASHBOARD_VIEWER_USERS="brendanhills@google.com,colleague@google.com"

# BLOCKED_DOMAINS: Domains strictly forbidden from viewer access
BLOCKED_DOMAINS="altostrat.com"
```

---

## 🔒 Deploying with Restricted Viewer Access

Once configured in `.env`, simply run:

```bash
# 1-Click deploy using .env configuration
./deploy/deploy_gcp.sh

# Or optionally override/add extra viewer groups or users on the fly
./deploy/deploy_gcp.sh --viewer-group "extra-group@google.com" --viewer-user "lead@google.com"
```

---

## 🔍 Checking Service Status & Viewer IAM

```bash
# Check live status, service URL, and currently bound Dashboard Viewers
./deploy/deploy_gcp.sh --status
```

---

## 🛑 Stopping / Shutting Down the Service

To immediately stop the service and take the dashboard offline (like `sudo shutdown -h now`):

```bash
# 1-Click Service Shutdown
./deploy/shutdown.sh

# Or using the alias / flag
./deploy/stop.sh
./deploy/deploy_gcp.sh --stop
```

This immediately halts all ingress traffic and removes the running Cloud Run service instance.

---

## 📁 Files in this Directory

- **`deploy_gcp.sh`**: Private Cloud Run pipeline supporting `.env` config, `--viewer-group`, `--viewer-user`, `--status`, and `--stop` flags.
- **`shutdown.sh` / `stop.sh`**: Immediate service shutdown script to take the dashboard offline.
- **`deploy_c4a.py` / `deploy.sh`**: C4A Starter prototype pipeline.
- **`Dockerfile` & `nginx.conf`**: Container specifications for Cloud Run port 8080.
