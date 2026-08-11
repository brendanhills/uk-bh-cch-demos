#!/bin/bash
# ==============================================================================
# F-DSE Risk Intelligence Platform — Private GCP Cloud Run Pipeline
# Supports .env configuration for Dashboard Viewers and Admins/Editors,
# domain blocking, live status checks, and instant shutdown.
# Rule: All Admins/Editors automatically inherit Viewer access.
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
        DASHBOARD_ADMIN_GROUPS)     ENV_ADMIN_GROUPS="$value" ;;
        DASHBOARD_ADMIN_USERS)      ENV_ADMIN_USERS="$value" ;;
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
  echo "Access Control Options (overrides or augments .env):"
  echo "  --viewer-group, --group <email>   Google Group(s) granted VIEWER access (roles/run.invoker)"
  echo "  --viewer-user, --user <emails>    User email(s) granted VIEWER access (roles/run.invoker)"
  echo "  --admin-group <email>             Google Group(s) granted ADMIN/EDITOR access (roles/run.developer)"
  echo "  --admin-user <emails>             User email(s) granted ADMIN/EDITOR access (roles/run.developer)"
  echo ""
  echo "Note: All Admins/Editors automatically inherit Viewer permissions."
  echo ""
  echo "Service Management Commands:"
  echo "  (default)           Build and deploy the dashboard to private Cloud Run with IAM restrictions"
  echo "  --status, status    Check live status, endpoint URL, and current IAM viewer/admin policy"
  echo "  --stop, --down, stop  Shut down the service and take it offline immediately"
  echo ""
  echo "Configuration (.env):"
  echo "  Role assignments can be configured in .env via:"
  echo "    • DASHBOARD_VIEWER_GROUPS=\"team@google.com\""
  echo "    • DASHBOARD_VIEWER_USERS=\"viewer1@google.com,viewer2@google.com\""
  echo "    • DASHBOARD_ADMIN_GROUPS=\"lead-team@google.com\""
  echo "    • DASHBOARD_ADMIN_USERS=\"admin1@google.com\""
  echo "    • BLOCKED_DOMAINS=\"altostrat.com\""
  echo ""
  echo "Examples:"
  echo "  ./deploy/deploy_gcp.sh                                         # Deploys with roles defined in .env"
  echo "  ./deploy/deploy_gcp.sh --viewer-group team@google.com          # Adds viewer group"
  echo "  ./deploy/deploy_gcp.sh --admin-user lead@google.com            # Adds admin/editor user"
  echo "  ./deploy/deploy_gcp.sh --status                                # Checks live service & IAM roles"
  echo "  ./deploy/deploy_gcp.sh --stop                                  # Shuts down service"
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
    echo "🔒 Current IAM Access Policy (Viewers & Admins):"
    gcloud run services get-iam-policy "$SERVICE_NAME" --project "$PROJECT_ID" --region "$REGION" --flatten="bindings[].members" --format="table(bindings.role,bindings.members)"
  else
    echo "❌ Service is currently OFFLINE (not running)."
  fi
  exit 0
}

# Parse flags
VIEWER_GROUPS_FLAG=""
VIEWER_USERS_FLAG=""
ADMIN_GROUPS_FLAG=""
ADMIN_USERS_FLAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --stop|--down|--shutdown|stop|down|shutdown)
      stop_service
      ;;
    --status|status)
      check_status
      ;;
    --viewer-group|--viewer-groups|--group|--groups)
      VIEWER_GROUPS_FLAG="$2"
      shift 2
      ;;
    --viewer-user|--viewer-users|--user|--users|--allow|--allow-emails)
      VIEWER_USERS_FLAG="$2"
      shift 2
      ;;
    --admin-group|--admin-groups)
      ADMIN_GROUPS_FLAG="$2"
      shift 2
      ;;
    --admin-user|--admin-users)
      ADMIN_USERS_FLAG="$2"
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

# --- Process Admins / Editors ---
FINAL_ADMINS=()

ALL_ADMIN_GROUPS_STR="${ENV_ADMIN_GROUPS}"
if [[ -n "$ADMIN_GROUPS_FLAG" ]]; then
  ALL_ADMIN_GROUPS_STR="${ALL_ADMIN_GROUPS_STR:+${ALL_ADMIN_GROUPS_STR},}${ADMIN_GROUPS_FLAG}"
fi

if [[ -n "$ALL_ADMIN_GROUPS_STR" ]]; then
  IFS=',' read -ra GRP_LIST <<< "$ALL_ADMIN_GROUPS_STR"
  for g in "${GRP_LIST[@]}"; do
    g_trimmed=$(echo "$g" | xargs)
    if [[ -n "$g_trimmed" ]]; then
      entry="group:$g_trimmed"
      validate_domain "$entry"
      FINAL_ADMINS+=("$entry")
    fi
  done
fi

ALL_ADMIN_USERS_STR="${ENV_ADMIN_USERS:-brendanhills@google.com}"
if [[ -n "$ADMIN_USERS_FLAG" ]]; then
  ALL_ADMIN_USERS_STR="${ALL_ADMIN_USERS_STR:+${ALL_ADMIN_USERS_STR},}${ADMIN_USERS_FLAG}"
fi

if [[ -n "$ALL_ADMIN_USERS_STR" ]]; then
  IFS=',' read -ra USR_LIST <<< "$ALL_ADMIN_USERS_STR"
  for u in "${USR_LIST[@]}"; do
    u_trimmed=$(echo "$u" | xargs)
    if [[ -n "$u_trimmed" ]]; then
      entry="user:$u_trimmed"
      validate_domain "$entry"
      FINAL_ADMINS+=("$entry")
    fi
  done
fi

# --- Process Viewers (including Automatic Admin Inheritance) ---
FINAL_VIEWERS=()

# Helper function to add viewer uniquely
add_unique_viewer() {
  local item="$1"
  for existing in "${FINAL_VIEWERS[@]}"; do
    if [[ "$existing" == "$item" ]]; then
      return 0
    fi
  done
  FINAL_VIEWERS+=("$item")
}

# 1. Explicit Viewer Groups
ALL_VIEWER_GROUPS_STR="${ENV_VIEWER_GROUPS}"
if [[ -n "$VIEWER_GROUPS_FLAG" ]]; then
  ALL_VIEWER_GROUPS_STR="${ALL_VIEWER_GROUPS_STR:+${ALL_VIEWER_GROUPS_STR},}${VIEWER_GROUPS_FLAG}"
fi

if [[ -n "$ALL_VIEWER_GROUPS_STR" ]]; then
  IFS=',' read -ra GRP_LIST <<< "$ALL_VIEWER_GROUPS_STR"
  for g in "${GRP_LIST[@]}"; do
    g_trimmed=$(echo "$g" | xargs)
    if [[ -n "$g_trimmed" ]]; then
      entry="group:$g_trimmed"
      validate_domain "$entry"
      add_unique_viewer "$entry"
    fi
  done
fi

# 2. Explicit Viewer Users
ALL_VIEWER_USERS_STR="${ENV_VIEWER_USERS}"
if [[ -n "$VIEWER_USERS_FLAG" ]]; then
  ALL_VIEWER_USERS_STR="${ALL_VIEWER_USERS_STR:+${ALL_VIEWER_USERS_STR},}${VIEWER_USERS_FLAG}"
fi

if [[ -n "$ALL_VIEWER_USERS_STR" ]]; then
  IFS=',' read -ra USR_LIST <<< "$ALL_VIEWER_USERS_STR"
  for u in "${USR_LIST[@]}"; do
    u_trimmed=$(echo "$u" | xargs)
    if [[ -n "$u_trimmed" ]]; then
      entry="user:$u_trimmed"
      validate_domain "$entry"
      add_unique_viewer "$entry"
    fi
  done
fi

# 3. RULE: All Admins/Editors are automatically Viewers
for admin_entry in "${FINAL_ADMINS[@]}"; do
  add_unique_viewer "$admin_entry"
done

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

# 3. Apply IAM Invoker permissions to all Viewers (including inherited Admins)
echo "🔒 Applying restricted IAM access control for Dashboard Viewers (roles/run.invoker)..."
for member in "${FINAL_VIEWERS[@]}"; do
  echo "   👥 Granting Viewer access (roles/run.invoker) to: $member"
  gcloud run services add-iam-policy-binding "$SERVICE_NAME" \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --member="$member" \
    --role="roles/run.invoker" \
    --quiet >/dev/null
done

# 4. Apply IAM Developer permissions to Dashboard Admins/Editors
echo "🔒 Applying restricted IAM access control for Dashboard Admins/Editors (roles/run.developer)..."
for member in "${FINAL_ADMINS[@]}"; do
  echo "   🛠️ Granting Admin/Editor access (roles/run.developer) to: $member"
  gcloud run services add-iam-policy-binding "$SERVICE_NAME" \
    --project "$PROJECT_ID" \
    --region "$REGION" \
    --member="$member" \
    --role="roles/run.developer" \
    --quiet >/dev/null
done

echo ""
echo "=================================================================="
echo "🎉 DEPLOYMENT COMPLETE & SECURED"
echo "=================================================================="
echo "  🌐 Private Service URL: $SERVICE_URL"
echo ""
echo "  👥 Dashboard Viewers (Can view via Google SSO):"
for member in "${FINAL_VIEWERS[@]}"; do
  echo "     • $member"
done
echo ""
echo "  🛠️ Dashboard Admins / Editors (Can deploy & manage):"
for member in "${FINAL_ADMINS[@]}"; do
  echo "     • $member (inherits Viewer access)"
done
echo ""
echo "  🚫 Explicitly Blocked Domains: ${BLOCKED_DOMAINS[*]}"
echo "  🛑 Stop service:               ./deploy/shutdown.sh (or ./deploy/deploy_gcp.sh --stop)"
echo "=================================================================="
