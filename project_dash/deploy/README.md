# F-DSE Dashboard Deployment & Operations Pipeline

This directory contains deployment pipelines and service shutdown controls for the **F-DSE Risk Intelligence Platform**.

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

This immediately halts all traffic and removes the running Cloud Run service instance.

---

## 🔒 Deploying with Restricted Access (Google Groups & IAM)

Deploys the dashboard to your team GCP project (**`uk-bh-experiments-argolis`**) with `--no-allow-unauthenticated`. Access is strictly restricted to your specified Google Group or user allowlist, and automatically blocks unauthorized domains like `altostrat.com`.

### 1. Deploy with a Google Group
```bash
# Grant access to a Google Group (e.g. @google.com or @twosync.google.com)
./deploy/deploy_gcp.sh --group "f-dse-governance-team@google.com"

# Or with multiple groups and individual users
./deploy/deploy_gcp.sh \
  --group "f-dse-governance-team@google.com,my-team@twosync.google.com" \
  --user "lead@google.com"
```

### 2. Check Live Status & Access Policies
```bash
./deploy/deploy_gcp.sh --status
```

---

## 📁 Files in this Directory

- **`shutdown.sh` / `stop.sh`**: Immediate service shutdown script to take the dashboard offline.
- **`deploy_gcp.sh`**: Private Cloud Run pipeline supporting `--group`, `--user`, `--status`, and `--stop` flags.
- **`deploy_c4a.py` / `deploy.sh`**: C4A Starter prototype pipeline.
- **`Dockerfile` & `nginx.conf`**: Container specifications for Cloud Run port 8080.
