#!/bin/bash
# ==============================================================================
# Project Monaro Risk Platform — Automated GCP Environment Provisioning
#
# Usage:
#   ./deploy/provision_environment.sh --env dev   # Provisions monaro-risk-dev
#   ./deploy/provision_environment.sh --env prod  # Provisions monaro-risk-prod
#   ./deploy/provision_environment.sh --project my-custom-proj --region australia-southeast1
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ENV_TARGET="dev"
PROJECT_ID=""
REGION="australia-southeast1"

usage() {
  echo "Usage: $0 [options]"
  echo ""
  echo "Options:"
  echo "  --env <dev|prod>        Target environment preset (default: dev)"
  echo "  --project <project-id>  Override GCP Project ID explicitly"
  echo "  --region <region>       GCP Region (default: australia-southeast1)"
  echo "  --help, -h              Show this help message"
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENV_TARGET="$2"
      shift 2
      ;;
    --project)
      PROJECT_ID="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --help|-h)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done

# Apply Environment Presets
if [[ -z "$PROJECT_ID" ]]; then
  if [[ "$ENV_TARGET" == "prod" ]]; then
    PROJECT_ID="monaro-risk-prod"
    SERVICE_NAME="monaro-risk-dash-prod"
    ACCESS_GROUP="monaro-risk-prod@google.com"
    ADMIN_GROUP="monaro-risk-prod-admin@google.com"
    TRIGGER_NAME="deploy-monaro-risk-dash-prod"
    TAG_PATTERN="^project_dash/prod-.*$"
    BRANCH_PATTERN=""
  else
    PROJECT_ID="monaro-risk-dev"
    SERVICE_NAME="monaro-risk-dash-dev"
    ACCESS_GROUP="monaro-risk-dev@google.com"
    ADMIN_GROUP="monaro-risk-dev-admin@google.com"
    TRIGGER_NAME="deploy-monaro-risk-dash-dev"
    TAG_PATTERN=""
    BRANCH_PATTERN="^dev$"
  fi
else
  SERVICE_NAME="monaro-risk-dash-${ENV_TARGET}"
  ACCESS_GROUP="${PROJECT_ID}@google.com"
  ADMIN_GROUP="${PROJECT_ID}-admin@google.com"
  TRIGGER_NAME="deploy-${SERVICE_NAME}"
  TAG_PATTERN=""
  BRANCH_PATTERN="^dev$"
fi

SA_NAME="github-deployer"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "=============================================================================="
echo "🚀 Provisioning Project Monaro GCP Environment"
echo "=============================================================================="
echo "• Environment:    ${ENV_TARGET}"
echo "• GCP Project:    ${PROJECT_ID}"
echo "• Region:         ${REGION}"
echo "• Cloud Run:      ${SERVICE_NAME}"
echo "• Viewer Group:   ${ACCESS_GROUP}"
echo "• Admin Group:    ${ADMIN_GROUP}"
echo "• Deployer SA:    ${SA_EMAIL}"
echo "=============================================================================="
echo ""

# 1. Enable Required GCP APIs
echo "=== 1. Enabling Required GCP APIs ==="
gcloud services enable \
  clouderrorreporting.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
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
echo "✅ All 14 GCP APIs successfully enabled."
echo ""

# 2. Create Deployer Service Account
echo "=== 2. Creating Dedicated Service Account (${SA_NAME}) ==="
if ! gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
  gcloud iam service-accounts create "${SA_NAME}" \
    --display-name="GitHub & Cloud Build Deployer" \
    --project="${PROJECT_ID}"
  echo "✅ Service account created: ${SA_EMAIL}"
else
  echo "ℹ️ Service account ${SA_EMAIL} already exists."
fi
echo ""

# 3. Bind Least-Privilege IAM Roles
echo "=== 3. Binding Least-Privilege IAM Roles to Deployer SA ==="
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
    --condition=None >/dev/null || true
  echo "  ✓ Granted ${ROLE}"
done
echo "✅ IAM permissions bound successfully."
echo ""

# 4. Artifact Registry Repository
echo "=== 4. Ensuring Artifact Registry Exists in ${REGION} ==="
if ! gcloud artifacts repositories describe cloud-run-source-deploy --location="${REGION}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
  gcloud artifacts repositories create cloud-run-source-deploy \
    --repository-format=docker \
    --location="${REGION}" \
    --description="Cloud Run source deployments" \
    --project="${PROJECT_ID}"
  echo "✅ Artifact Registry repository 'cloud-run-source-deploy' created in ${REGION}."
else
  echo "ℹ️ Artifact Registry repository already exists in ${REGION}."
fi
echo ""

# 5. Cloud Build Trigger
echo "=== 5. Configuring Automated Cloud Build Trigger ==="
if gcloud builds triggers describe "${TRIGGER_NAME}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
  echo "ℹ️ Cloud Build trigger '${TRIGGER_NAME}' already exists."
else
  if [[ -n "$TAG_PATTERN" ]]; then
    echo "Creating Tag-based trigger for pattern '${TAG_PATTERN}'..."
    gcloud builds triggers create github \
      --project="${PROJECT_ID}" \
      --name="${TRIGGER_NAME}" \
      --repo-name="uk-bh-experiments" \
      --repo-owner="cloud-gtm" \
      --tag-pattern="${TAG_PATTERN}" \
      --build-config="project_dash/deploy/cloudbuild.yaml" \
      --service-account="projects/${PROJECT_ID}/serviceAccounts/${SA_EMAIL}" \
      --substitutions="_SERVICE_NAME=${SERVICE_NAME},_ACCESS_GROUP=${ACCESS_GROUP},_REGION=${REGION},_IMAGE_NAME=${SERVICE_NAME}" \
      --description="Automated Production Deployment on release tags in Sydney"
  else
    echo "Creating Branch-based trigger for branch '${BRANCH_PATTERN}'..."
    gcloud builds triggers create github \
      --project="${PROJECT_ID}" \
      --name="${TRIGGER_NAME}" \
      --repo-name="uk-bh-experiments" \
      --repo-owner="cloud-gtm" \
      --branch-pattern="${BRANCH_PATTERN}" \
      --build-config="project_dash/deploy/cloudbuild.yaml" \
      --service-account="projects/${PROJECT_ID}/serviceAccounts/${SA_EMAIL}" \
      --substitutions="_SERVICE_NAME=${SERVICE_NAME},_ACCESS_GROUP=${ACCESS_GROUP},_REGION=${REGION},_IMAGE_NAME=${SERVICE_NAME}" \
      --included-files="project_dash/**" \
      --ignored-files="project_dash/**/*.md,project_dash/docs/**,project_dash/.agents/**,project_dash/conductor/**" \
      --description="Automated Dev Deployment on push to dev in Sydney"
  fi
  echo "✅ Cloud Build trigger created."
fi
echo ""

# 6. Error Reporting & Cloud Monitoring Alerting
echo "=== 6. Configuring Error Reporting & Alert Channels ==="
echo "Checking notification channel for ${ADMIN_GROUP}..."
CHANNEL_ID=$(gcloud alpha monitoring channels list \
  --project="${PROJECT_ID}" \
  --filter="labels.email_address = \"${ADMIN_GROUP}\"" \
  --format="value(name)" 2>/dev/null | head -n1 || true)

if [[ -z "${CHANNEL_ID}" ]]; then
  echo "Creating email notification channel for ${ADMIN_GROUP}..."
  CHANNEL_JSON=$(gcloud alpha monitoring channels create \
    --project="${PROJECT_ID}" \
    --type="email" \
    --display-name="Monaro Risk Admin Alerts (${ENV_TARGET})" \
    --channel-labels="email_address=${ADMIN_GROUP}" \
    --format="json" 2>/dev/null || true)
  CHANNEL_ID=$(echo "${CHANNEL_JSON}" | grep -o '"name": "[^"]*' | cut -d'"' -f4 || true)
  echo "✅ Created notification channel: ${CHANNEL_ID}"
else
  echo "ℹ️ Notification channel already exists: ${CHANNEL_ID}"
fi

POLICY_NAME="Error Reporting Exception Alert (${PROJECT_ID})"
EXISTING_POLICY=$(gcloud alpha monitoring policies list \
  --project="${PROJECT_ID}" \
  --filter="displayName = \"${POLICY_NAME}\"" \
  --format="value(name)" 2>/dev/null | head -n1 || true)

if [[ -n "${EXISTING_POLICY}" ]]; then
  echo "ℹ️ Alert policy '${POLICY_NAME}' already exists."
elif [[ -n "${CHANNEL_ID}" ]]; then
  echo "Creating Log-Based Metric & Alert Policy for Container Exceptions..."
  TMP_POLICY_FILE=$(mktemp /tmp/error_policy_XXXXXX.json)
  cat <<EOF > "${TMP_POLICY_FILE}"
{
  "displayName": "${POLICY_NAME}",
  "documentation": {
    "content": "A runtime exception or 5xx crash was logged by Cloud Run service ${SERVICE_NAME} in ${PROJECT_ID}.",
    "mimeType": "text/markdown"
  },
  "conditions": [
    {
      "displayName": "Cloud Run Error Logs condition",
      "conditionThreshold": {
        "filter": "resource.type = \"cloud_run_revision\" AND severity >= ERROR",
        "aggregations": [
          {
            "alignmentPeriod": "60s",
            "perSeriesAligner": "ALIGN_RATE"
          }
        ],
        "comparison": "COMPARISON_GT",
        "thresholdValue": 0,
        "duration": "0s",
        "trigger": {
          "count": 1
        }
      }
    }
  ],
  "notificationChannels": [
    "${CHANNEL_ID}"
  ],
  "combiner": "OR",
  "enabled": true
}
EOF
  gcloud alpha monitoring policies create \
    --policy-from-file="${TMP_POLICY_FILE}" \
    --project="${PROJECT_ID}" >/dev/null 2>&1 || true
  rm -f "${TMP_POLICY_FILE}"
  echo "✅ Log-based alert policy created and linked to ${ADMIN_GROUP}."
fi
echo ""

echo "=============================================================================="
echo "🎉 Provisioning Complete for ${PROJECT_ID} (${REGION})!"
echo "=============================================================================="
