# F-DSE Dashboard Deployment & Operations Pipeline

This directory contains deployment pipelines and service shutdown controls for the **F-DSE Risk Intelligence Platform**.

---

## ⚙️ Configuration (`.env`)

You can define your allowed Google Groups, users, and blocked domains directly in your project root `.env` file (copied from `.env.example`):

```bash
# --- Cloud Run Deployment & Access Control Configuration ---
GCP_PROJECT_ID="uk-bh-experiments-argolis"
GCP_REGION="us-central1"
GCP_SERVICE_NAME="f-dse-risk-dashboard-private"

# Allowed Google Groups (comma-separated list, e.g. team@google.com or team@twosync.google.com)
ALLOWED_GROUPS="your-team-group@google.com"

# Allowed Individual Users (comma-separated list of @google.com emails)
ALLOWED_USERS="brendanhills@google.com,colleague@google.com"

# Blocked Domains (comma-separated list, strictly forbidden from receiving IAM access)
BLOCKED_DOMAINS="altostrat.com"
```

---

## 🔒 Deploying with Restricted Access

Once configured in `.env`, simply run:

```bash
# 1-Click deploy using .env configuration
./deploy/deploy_gcp.sh

# Or optionally override/add extra groups or users on the fly
./deploy/deploy_gcp.sh --group "extra-group@google.com" --user "lead@google.com"
```

---

## 🔍 Checking Service Status

```bash
# Check live status, service URL, and currently bound IAM policies
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

- **`deploy_gcp.sh`**: Private Cloud Run pipeline supporting `.env` config, `--group`, `--user`, `--status`, and `--stop` flags.
- **`shutdown.sh` / `stop.sh`**: Immediate service shutdown script to take the dashboard offline.
- **`deploy_c4a.py` / `deploy.sh`**: C4A Starter prototype pipeline.
- **`Dockerfile` & `nginx.conf`**: Container specifications for Cloud Run port 8080.
