#!/bin/bash

# A script to automatically set up the local and cloud environment for the
# Gemini Enterprise Terraform and script-based resources.

set -eo pipefail

usage() {
  echo "Usage: $0 [-p <PROJECT_ID>] [-u <USER_EMAIL>]"
  echo "  -p PROJECT_ID: (Optional) The Google Cloud project ID to configure. Defaults to active gcloud project."
  echo "  -u USER_EMAIL: (Optional) The user to grant permissions to. Defaults to the active gcloud user."
  exit 1
}

PROJECT_ID=""
USER_EMAIL=""

while getopts ":p:u:" opt; do
  case ${opt} in
    p )
      PROJECT_ID=$OPTARG
      ;;
    u )
      USER_EMAIL=$OPTARG
      ;;
    \? )
      usage
      ;;
  esac
done

# Get project ID if not provided
if [ -z "${PROJECT_ID}" ]; then
  PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
  if [ -z "${PROJECT_ID}" ]; then
    echo "❌ No GCP project ID provided via -p flag and no project configured in gcloud." >&2
    usage
  fi
fi

# Get active user if not provided
if [ -z "${USER_EMAIL}" ]; then
  USER_EMAIL=$(gcloud config get-value account 2>/dev/null)
  if [ -z "${USER_EMAIL}" ]; then
    echo "❌ Could not determine active gcloud user. Please login first or specify with -u flag."
    exit 1
  fi
fi

echo "🚀 Setting up environment for project '${PROJECT_ID}' and user '${USER_EMAIL}'...\n"

# 1. Set gcloud project
echo "1. Setting active gcloud project..."
gcloud config set project "${PROJECT_ID}"

# 2. Enable APIs
echo "2. Enabling required Google Cloud APIs..."
APIS_TO_ENABLE=(
  "discoveryengine.googleapis.com"
  "storage.googleapis.com"
)
for api in "${APIS_TO_ENABLE[@]}"; do
  echo "   - Enabling $api..."
  # Attempt to enable the API, capturing stderr to check for specific errors.
  if ! gcloud services enable "$api" --project="${PROJECT_ID}" 2> >(tee /dev/stderr | grep -q "FAILED_PRECONDITION: The terms of service"); then
    # The command failed, and the error was the ToS precondition.
    echo "❌ Terms of Service for '$api' must be accepted." >&2
    echo "   Please visit the following URL to accept the terms, then re-run this script:" >&2
    echo "   ➡ https://console.cloud.google.com/terms/cloud?project=${PROJECT_ID}" >&2
    exit 1
  elif [ ${PIPESTATUS[0]} -ne 0 ]; then
    # The command failed for a different reason.
    echo "❌ An unexpected error occurred while trying to enable '$api'. Please review the error message above." >&2
    exit 1
  fi
done

# 3. Grant IAM Roles
echo "3. Granting required IAM roles..."
ROLES_TO_GRANT=(
  "roles/storage.admin"
  "roles/discoveryengine.admin"
  "roles/serviceusage.serviceUsageConsumer"
)
for role in "${ROLES_TO_GRANT[@]}"; do
  echo "   - Granting $role to $USER_EMAIL..."
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" --member="user:${USER_EMAIL}" --role="$role" --condition=None > /dev/null
done

# 4. Set up Application Default Credentials (ADC)
echo "4. Setting up Application Default Credentials (ADC)..."
echo "   - Initiating ADC login. Please follow the browser prompts."
gcloud auth application-default login

echo "   - Setting ADC quota project..."
gcloud auth application-default set-quota-project "${PROJECT_ID}"

echo "✅ Environment setup complete for project '${PROJECT_ID}'!"
echo "You can now run './check_env.sh' to verify, followed by 'terraform apply'."
