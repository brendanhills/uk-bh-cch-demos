#!/bin/bash
set -e

# This script deploys the MCP Toolbox for Databases to Cloud Run.
# NOTE: This script uses a hardcoded password for the database.
# For production environments, it is strongly recommended to use Google Secret Manager for the password.

export TOOLBOX_IMAGE=us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:latest
export PROJECT_ID=$(gcloud config get-value project)

if [ -z "$PROJECT_ID" ]; then
    echo "GCP Project ID is not set. Please run 'gcloud config set project YOUR_PROJECT_ID'"
    exit 1
fi
echo "Updating Secret"
gcloud secrets versions add tools --data-file=deployment/mcp-toolbox/tools.yaml

echo "Deploying toolbox to project: $PROJECT_ID"

gcloud run deploy toolbox \
    --image $TOOLBOX_IMAGE \
    --service-account toolbox-identity \
    --region us-central1 \
    --set-secrets "/app/tools.yaml=tools:latest,DB_PASS=db-password:latest" \
    --set-env-vars="PROJECT_ID=$PROJECT_ID,DB_USER=postgres" \
    --args="--tools-file=/app/tools.yaml,--address=0.0.0.0,--port=8080" \
    --allow-unauthenticated
    
    # https://cloud.google.com/run/docs/authenticating/public#gcloud
