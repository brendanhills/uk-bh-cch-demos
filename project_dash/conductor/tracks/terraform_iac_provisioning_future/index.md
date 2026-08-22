# Track: Terraform Infrastructure as Code (IaC) Provisioning

**Status:** `[ ] Future Enhancement`  
**Owner:** Platform / DevOps  
**Created:** `2026-08-20`  

---

## 🎯 Context & Objective
Currently, environment provisioning across `monaro-risk-dev` and `monaro-risk-prod` in `australia-southeast1` (Sydney) is automated via the idempotent bash CLI tool [`deploy/provision_environment.sh`](../../deploy/provision_environment.sh).

As a future enhancement once permanent enterprise billing accounts are attached (replacing 90-day sandbox projects), transition the infrastructure management to declarative **Terraform (IaC)**.

---

## 📋 Scope & Requirements

1. **Declarative Resource Definitions**:
   - `google_project_service`: Enable all 14 required GCP APIs.
   - `google_service_account` & `google_project_iam_member`: `github-deployer` service account with least-privilege roles.
   - `google_artifact_registry_repository`: `cloud-run-source-deploy` in `australia-southeast1`.
   - `google_cloudbuild_trigger`: Tag release trigger (`monaro-risk-prod`) and dev branch trigger (`monaro-risk-dev`).
   - `google_monitoring_notification_channel` & `google_monitoring_alert_policy`: Email notification channel for `*-admin@google.com` and log-based error alerting policies.

2. **State Management**:
   - Configure remote backend on Google Cloud Storage (`backend "gcs"`).
   - Set up workspace-based or folder-based isolation between `dev` and `prod`.

3. **CI/CD Integration**:
   - Optional automated `terraform plan` and `terraform apply` workflow via Cloud Build or GitHub Actions.
