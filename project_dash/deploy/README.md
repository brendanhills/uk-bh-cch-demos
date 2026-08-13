# F-DSE Dashboard Deployment & Operations Pipeline

This directory contains deployment pipelines, role-based access configuration, and service shutdown controls for the **F-DSE Risk Intelligence Platform**.

---

## 👥 Ganpati (MDB) & TwoSync Groups Architecture

Access to the platform is managed through three dedicated Ganpati Prod groups synced to GCP via TwoSync:

| Group Name | Ganpati Type | GCP IAM Identity | Target Audience & Permissions |
| :--- | :--- | :--- | :--- |
| **`monaro-risk-admin`** | `ADMIN` | `monaro-risk-admin@twosync.google.com` | **Admin / Ownership Group**: Owns and administers access policies for dev/prod groups. |
| **`monaro-risk-dev`** | `TEAM` | `monaro-risk-dev@twosync.google.com` | **Developers / Editors**: Can deploy revisions and access development environments. |
| **`monaro-risk-prod`** | `TEAM` | `monaro-risk-prod@twosync.google.com` | **Production Viewers**: Executive stakeholders (e.g. `allins@google.com`) and governance viewers. |

### Useful Links
* **Admin Group UI**: [https://ganpati2.corp.google.com/group/%25monaro-risk-admin.prod](https://ganpati2.corp.google.com/group/%25monaro-risk-admin.prod)
* **Dev Team UI**: [https://ganpati2.corp.google.com/group/%25monaro-risk-dev.prod](https://ganpati2.corp.google.com/group/%25monaro-risk-dev.prod)
* **Prod Team UI**: [https://ganpati2.corp.google.com/group/%25monaro-risk-prod.prod](https://ganpati2.corp.google.com/group/%25monaro-risk-prod.prod)

---

## ⚙️ Configuration (`.env`)

Configure your authorized **Dashboard Viewers**, **Dashboard Admins/Editors**, blocked domains, and GCP project settings in your root `.env` file (copied from `.env.example`):

```bash
# --- Cloud Run Deployment Configuration ---
GCP_PROJECT_ID="uk-bh-experiments-argolis"
GCP_REGION="us-central1"
GCP_SERVICE_NAME="f-dse-risk-dashboard-private"

# --- Dashboard Viewer Access Control (IAM roles/run.invoker) ---
# Viewers can access and view the live dashboard web application via Google SSO.
DASHBOARD_VIEWER_GROUPS="monaro-risk-prod@twosync.google.com"
DASHBOARD_VIEWER_USERS="brendanhills@google.com,allins@google.com"

# --- Dashboard Admin / Editor Access Control (IAM roles/run.developer) ---
# Admins/Editors can deploy updates, manage revisions, and configure the service.
DASHBOARD_ADMIN_GROUPS="monaro-risk-dev@twosync.google.com"
DASHBOARD_ADMIN_USERS="brendanhills@google.com"

# --- Security & Domain Restrictions ---
BLOCKED_DOMAINS="altostrat.com"
```

---

## 🔒 Deploying with Role-Based Access

Once configured in `.env`, simply run:

```bash
# 1-Click deploy using .env configuration
./deploy/deploy_gcp.sh

# Or optionally override/add extra viewer or admin groups/users on the fly
./deploy/deploy_gcp.sh \
  --viewer-group "monaro-risk-prod@twosync.google.com" \
  --admin-group "monaro-risk-dev@twosync.google.com"
```

---

## 🔍 Checking Service Status & IAM Roles

```bash
# Check live status, service URL, and currently bound Viewers and Admins
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

- **`deploy_gcp.sh`**: Private Cloud Run pipeline supporting `.env` config, `--viewer-group`, `--viewer-user`, `--admin-group`, `--admin-user`, `--status`, and `--stop` flags.
- **`shutdown.sh` / `stop.sh`**: Immediate service shutdown script to take the dashboard offline.
- **`deploy_c4a.py` / `deploy.sh`**: C4A Starter prototype pipeline.
- **`Dockerfile` & `nginx.conf`**: Container specifications for Cloud Run port 8080.
