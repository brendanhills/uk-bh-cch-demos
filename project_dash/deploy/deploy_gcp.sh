#!/bin/bash
# ==============================================================================
# F-DSE Risk Intelligence Platform — Private GCP Cloud Run Pipeline
# Supports .env configuration for Dashboard Viewer Groups/Users, domain blocking,
# live status checks, and instant shutdown.
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# --- Load Configuration from .env ---
load_env() {
  local env_file=""
  if [[ -f "$PROJECT_ROOT/.env" ]]; then
    env_file="$PROJECT_ROOT/.env"
  elif [[ -f "$SCRIPT_DIR/.env" ]]; then
    env_file="$SCRIPT_DIR/.env"
  fi

  if [[ -n "$env_file" ]]; then
    while IFS='=' read -r key value; do
      key=$(echo "$key" | xargs)
      if [[ -z "$key" || "$key" =~ ^# ]]; then
        continue
      fi
      value=$(echo "$value" | sed -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//")
      case "$key" in
        GCP_PROJECT_ID)             ENV_PROJECT_ID="$value" ;;
        GCP_REGION)                 ENV_REGION="$value" ;;
        GCP_SERVICE_NAME)           ENV_SERVICE_NAME="$value" ;;
        DASHBOARD_VIEWER_GROUPS)    ENV_VIEWER_GROUPS="$value" ;;
        ALLOWED_GROUPS)             ENV_VIEWER_GROUPS="${ENV_VIEWER_GROUPS:-$value}" ;;
        DASHBOARD_VIEWER_USERS)     ENV_VIEWER_USERS="$value" ;;
        ALLOWED_USERS)              ENV_VIEWER_USERS="${ENV_VIEWER_USERS:-$value}" ;;
        BLOCKED_DOMAINS)            ENV_BLOCKED_DOMAINS="$value" ;;
      esac
    done < "$env_file"
  fi
}

load_env

# Apply defaults with .env overrides
PROJECT_ID="${ENV_PROJECT_ID:-uk-bh-experiments-argolis}"
SERVICE_NAME="${ENV_SERVICE_NAME:-f-dse-risk-dashboard-private}"
REGION="${ENV_REGION:-us-central1}"

# Blocked domains list (defaults + .env)
BLOCKED_DOMAINS_STR="${ENV_BLOCKED_DOMAINS:-altostrat.com}"
IFS=',' read -ra BLOCKED_DOMAINS <<< "$BLOCKED_DOMAINS_STR"

usage() {
  echo "Usage: $0 [options]"
  echo ""
  echo "Dashboard Viewer Access Control (overrides or augments .env):"
  echo "  --viewer-group, --group <email>   Google Group(s) granted viewer access (e.g. my-team@google.com or team@twosync.google.com)"
  echo "  --viewer-user, --user <emails>    Comma-separated user email(s) granted viewer access (e.g. alice@google.com,bob@google.com)"
  echo ""
  echo "Service Management Commands:"
  echo "  (default)           Build and deploy the dashboard to private Cloud Run with viewer IAM restrictions"
  echo "  --status, status    Check live status, endpoint URL, and current IAM viewer policy"
  echo "  --stop, --down, stop  Shut down the service and take it offline immediately"
  echo ""
  echo "Configuration (.env):"
  echo "  Viewer access lists are configured in .env via:"
  echo "    • DASHBOARD_VIEWER_GROUPS=\"team@google.com\""
  echo "    • DASHBOARD_VIEWER_USERS=\"user1@google.com,user2@google.com\""
  echo "    • BLOCKED_DOMAINS=\"altostrat.com\""
  echo ""
  echo "Examples:"
  echo "  ./deploy/deploy_gcp.sh                                     # Deploys with viewers defined in .env"
  echo "  ./deploy/deploy_gcp.sh --viewer-group team@google.com      # Appends/overrides viewer group"
  echo "  ./deploy/deploy_gcp.sh --status                            # Checks live service and viewer access list"
  echo "  ./deploy/deploy_gcp.sh --stop                              # Shuts down service"
  exit 1
}

# --- Validate Principal Domain ---
validate_domain() {
  local entry="$1"
  local email="${entry#*:}" # strip user: or group: prefix
  local domain="${email##*@}"

  for blocked in "${BLOCKED_DOMAINS[@]}"; do
    blocked_trimmed=$(echo "$blocked" | xargs)
    if [[ -n "$blocked_trimmed" && ("$domain" == "$blocked_trimmed" || "$domain" == *."$blocked_trimmed") ]]; then
      echo "❌ SECURITY ERROR: Domain '$domain' (from '$email') is BLOCKED and cannot be granted viewer access." >&2
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
    echo "🔒 Current Dashboard Viewers (IAM roles/run.invoker):"
    gcloud run services get-iam-policy "$SERVICE_NAME" --project "$PROJECT_ID" --region "$REGION" --flatten="bindings[].members" --format="table(bindings.role,bindings.members)"
  else
    echo "❌ Service is currently OFFLINE (not running)."
  fi
  exit 0
}

# Parse flags
GROUPS_FLAG=""
USERS_FLAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stop|--down|--shutdown|stop|down|shutdown)
      stop_service
      ;;
    --status|status)
      check_status
      ;;
    --viewer-group|--viewer-groups|--group|--groups)
      GROUPS_FLAG="$2"
      shift 2
      ;;
    --viewer-user|--viewer-users|--user|--users|--allow|--allow-emails)
      USERS_FLAG="$2"
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

cd "$PROJECT_ROOT"

# Compile and validate viewer principals from .env + CLI flags
FINAL_VIEWERS=()

# 1. Process Dashboard Viewer Google Groups (.env + flag)
ALL_GROUPS_STR="${ENV_VIEWER_GROUPS}"
if [[ -n "$GROUPS_FLAG" ]]; then
  if [[ -n "$ALL_GROUPS_STR" ]]; then
    ALL_GROUPS_STR="${ALL_GROUPS_STR},${GROUPS_FLAG}"
  else
    ALL_GROUPS_STR="${GROUPS_FLAG}"
  fi
fi

if [[ -n "$ALL_GROUPS_STR" ]]; then
  IFS=',' read -ra GRP_LIST <<< "$ALL_GROUPS_STR"
  for g in "${GRP_LIST[@]}"; do
    g_trimmed=$(echo "$g" | xargs)
    if [[ -n "$g_trimmed" ]]; then
      entry="group:$g_trimmed"
      validate_domain "$entry"
      FINAL_VIEWERS+=("$entry")
    fi
  done
fi

# 2. Process Dashboard Viewer Individual Users (.env + flag)
ALL_USERS_STR="${ENV_VIEWER_USERS:-brendanhills@google.com}"
if [[ -n "$USERS_FLAG" ]]; then
  if [[ -n "$ALL_USERS_STR" ]]; then
    ALL_USERS_STR="${ALL_USERS_STR},${USERS_FLAG}"
  else
    ALL_USERS_STR="${USERS_FLAG}"
  fi
fi

if [[ -n "$ALL_USERS_STR" ]]; then
  IFS=',' read -ra USR_LIST <<< "$ALL_USERS_STR"
  for u in "${USR_LIST[@]}"; do
    u_trimmed=$(echo "$u" | xargs)
    if [[ -n "$u_trimmed" ]]; then
      entry="user:$u_trimmed"
      validate_domain "$entry"
      FINAL_VIEWERS+=("$entry")
    fi
  done
fi

if [[ ${#FINAL_VIEWERS[@]} -eq 0 ]]; then
  echo "❌ Error: No dashboard viewer groups or users specified in .env or via CLI flags." >&2
  exit 1
fi

echo "=================================================================="
echo "🚀 Deploying F-DSE Risk Intelligence Dashboard (Private Mode)"
echo "   Config Source:   .env"
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

# 3. Apply restricted IAM Invoker permissions to Dashboard Viewers
echo "🔒 Applying restricted IAM access control for Dashboard Viewers..."
for member in "${FINAL_VIEWERS[@]}"; do
  echo "   ➕ Granting Dashboard Viewer access (roles/run.invoker) to: $member"
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
echo "  👥 Authorized Dashboard Viewers:"
for member in "${FINAL_VIEWERS[@]}"; do
  echo "     • $member"
done
echo "  🚫 Explicitly Blocked: ${BLOCKED_DOMAINS[*]}"
echo "  🛑 Stop service:       ./deploy/shutdown.sh (or ./deploy/deploy_gcp.sh --stop)"
echo "=================================================================="
