#!/bin/bash
# ==============================================================================
# Service Shutdown Script
# Immediately stops the Cloud Run service and takes the dashboard offline.
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Shut down private GCP service
"$SCRIPT_DIR/deploy_gcp.sh" --stop

# Also check for any active C4A service and shut down if running
C4A_PROJECT="f-dse-risk-intellige-q40fp-dev"
C4A_SERVICE="f-dse-risk-intelligence-dashboard"
if gcloud run services describe "$C4A_SERVICE" --project "$C4A_PROJECT" --region "us-central1" &>/dev/null; then
  echo "Stopping C4A service in $C4A_PROJECT..."
  gcloud run services delete "$C4A_SERVICE" --project "$C4A_PROJECT" --region "us-central1" --quiet || true
fi
