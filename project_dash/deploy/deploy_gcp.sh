#!/bin/bash
# ==============================================================================
# F-DSE Risk Intelligence Platform — Private GCP Cloud Run Pipeline
# Supports Google Group IAM binding, domain blocking, status, and shutdown.
# ==============================================================================
set -e

PROJECT_ID="uk-bh-experiments-argolis"
SERVICE_NAME="f-dse-risk-dashboard-private"
REGION="us-central1"

# List of domains strictly forbidden from receiving invoker access
BLOCKED_DOMAINS=("altostrat.com")

# Default authorized Google Groups or Users (e.g., group:your-team@google.com)
DEFAULT_PRINCIPALS=(
  "user:brendanhills@google.com"
)

usage() {
  echo "Usage: $0 [options]"
  echo ""
  echo "Access Control Options:"
  echo "  --group <email>     Google Group email to grant access (e.g. --group my-team@google.com or team@twosync.google.com)"
  echo "  --user <emails>     Comma-separated list of individual user emails (e.g. --user alice@google.com,bob@google.com)"
  echo ""
  echo "Service Management Commands:"
  echo "  (default)           Build and deploy the dashboard to private Cloud Run with IAM restrictions"
  echo "  --status, status    Check live status, endpoint URL, and current IAM policy"
  echo "  --stop, --down, stop  Shut down the service and take it offline immediately"
  echo ""
  echo "Examples:"
  echo "  ./deploy/deploy_gcp.sh --group f-dse-governance-team@google.com"
  echo "  ./deploy/deploy_gcp.sh --group my-team@twosync.google.com --user lead@google.com"
  echo "  ./deploy/deploy_gcp.sh --status"
  echo "  ./deploy/deploy_gcp.sh --stop"
  exit 1
}

# --- Validate Principal Domain ---
validate_domain() {
  local entry="$1"
  local email="${entry#*:}" # strip user: or group: prefix
  local domain="${email##*@}"

  for blocked in "${BLOCKED_DOMAINS[@]}"; do
    if [[ "$domain" == "$blocked" || "$domain" == *."$blocked" ]]; then
      echo "❌ SECURITY ERROR: Domain '$domain' (from '$email') is BLOCKED and cannot be granted access." >&2
      exit 1
    fi
  done
}

# --- Service Shutdown Function ---
stop_service() {
  echo "=================================================================="
  echo "🛑 SHUTTING DOWN SERVICE: $SERVICE_NAME"
  echo "   Project: $PROJECT_ID | Region: $REGION"
  echo "=================================================================="
  
  echo "Shutting down Cloud Run service..."
  if gcloud run services delete "$SERVICE_NAME" \
      --project "$PROJECT_ID" \
      --region "$REGION" \
      --quiet; then
    echo "✅ Service successfully stopped. The endpoint is completely OFFLINE."
  else
    echo "ℹ️ Service was not found or is already offline."
  fi
  echo "=================================================================="
  exit 0
}

# --- Status Check Function ---
check_status() {
  echo "🔍 Checking status for $SERVICE_NAME in $PROJECT_ID ($REGION)..."
  if gcloud run services describe "$SERVICE_NAME" --project "$PROJECT_ID" --region "$REGION" --format="yaml(status.url,status.conditions)" 2>/dev/null; then
    echo ""
    echo "🔒 Current IAM Access Policy:"
    gcloud run services get-iam-policy "$SERVICE_NAME" --project "$PROJECT_ID" --region "$REGION" --flatten="bindings[].members" --format="table(bindings.role,bindings.members)"
  else
    echo "❌ Service is currently OFFLINE (not running)."
  fi
  exit 0
}

# Parse flags
GROUPS_INPUT=""
USERS_INPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stop|--down|--shutdown|stop|down|shutdown)
      stop_service
      ;;
    --status|status)
      check_status
      ;;
    --group|--groups)
      GROUPS_INPUT="$2"
      shift 2
      ;;
    --user|--users|--allow|--allow-emails)
      USERS_INPUT="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Compile and validate principals
FINAL_PRINCIPALS=()

# 1. Add validated default principals
for def in "${DEFAULT_PRINCIPALS[@]}"; do
  validate_domain "$def"
  FINAL_PRINCIPALS+=("$def")
done

# 2. Add Google Groups
if [[ -n "$GROUPS_INPUT" ]]; then
  IFS=',' read -ra GRP_LIST <<< "$GROUPS_INPUT"
  for g in "${GRP_LIST[@]}"; do
    g_trimmed=$(echo "$g" | xargs)
    if [[ -n "$g_trimmed" ]]; then
      entry="group:$g_trimmed"
      validate_domain "$entry"
      FINAL_PRINCIPALS+=("$entry")
    fi
  done
fi

# 3. Add Individual Users
if [[ -n "$USERS_INPUT" ]]; then
  IFS=',' read -ra USR_LIST <<< "$USERS_INPUT"
  for u in "${USR_LIST[@]}"; do
    u_trimmed=$(echo "$u" | xargs)
    if [[ -n "$u_trimmed" ]]; then
      entry="user:$u_trimmed"
      validate_domain "$entry"
      FINAL_PRINCIPALS+=("$entry")
    fi
  done
fi

echo "=================================================================="
echo "🚀 Deploying F-DSE Risk Intelligence Dashboard (Private Mode)"
echo "   Project:         $PROJECT_ID"
echo "   Service:         $SERVICE_NAME"
echo "   Region:          $REGION"
echo "   Blocked Domains: ${BLOCKED_DOMAINS[*]}"
echo "=================================================================="

# 1. Build and deploy container to Cloud Run
echo "🔨 Building image and deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --source "$PROJECT_ROOT" \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --no-allow-unauthenticated

# 2. Retrieve service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --project "$PROJECT_ID" --region "$REGION" --format="value(status.url)")

# 3. Apply restricted IAM Invoker permissions
echo "🔒 Applying restricted IAM access control..."
for member in "${FINAL_PRINCIPALS[@]}"; do
  echo "   ➕ Granting Cloud Run Invoker access to: $member"
  gcloud run services add-iam-policy-binding "$SERVICE_NAME" \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --member="$member" \
    --role="roles/run.invoker" \
    --quiet >/dev/null
done

echo ""
echo "=================================================================="
echo "🎉 DEPLOYMENT COMPLETE & SECURED"
echo "=================================================================="
echo "  🌐 Private Service URL: $SERVICE_URL"
echo "  🔒 Allowed Principals:"
for member in "${FINAL_PRINCIPALS[@]}"; do
  echo "     • $member"
done
echo "  🚫 Explicitly Blocked: ${BLOCKED_DOMAINS[*]}"
echo "  🛑 Stop service:       ./deploy/shutdown.sh (or ./deploy/deploy_gcp.sh --stop)"
echo "=================================================================="
