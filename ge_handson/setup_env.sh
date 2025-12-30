#!/bin/bash

# A script to automatically set up the local and cloud environment for the
# Gemini Enterprise Terraform and script-based resources.

set -eo pipefail

DEBUG=true

# Source the common configuration file
source "$(dirname "$0")/config.sh"

usage() {
  echo "Usage: $0 [-p <PROJECT_ID>] [-u <USER_EMAIL>]"
  echo "  -p PROJECT_ID: (Optional) The Google Cloud project ID to configure. Defaults to active gcloud project."
  echo "  -u USER_EMAIL: (Optional) The user to grant permissions to. Defaults to the active gcloud user."
  exit 1
}



# Get project ID if not provided
check_project_config() {
  if [ -z "${PROJECT_ID}" ]; then
    local gcloud_project
    gcloud_project=$(gcloud config get-value project 2>/dev/null)
    if [[ -z "${gcloud_project}" ]]; then
      echo "🗣 No GCP project is configured in gcloud. Please run: gcloud config set project YOUR_PROJECT_ID" >&2
      exit 1
    fi
  fi

  # Check for project mismatch
  if [ -f "terraform.tfvars" ]; then
    tf_project=$(grep -E '^\s*project_id\s*=' terraform.tfvars | sed -E 's/.*=\s*//' | tr -d '" ')
    if [ -n "${tf_project}" ] && [ "${gcloud_project}" != "${tf_project}" ]; then
      echo "❗ Mismatch Detected!"
      echo "  Your active gcloud project is:         '$gcloud_project'"
      echo "  Your terraform.tfvars project is:      '$tf_project'"
      echo "  These should match to avoid applying permissions to the wrong project."
      echo "
  To fix, run: gcloud config set project $tf_project or edit terraform.tfvars"
      exit 1
    fi
  fi

  # Export for other functions to use
  export PROJECT_ID=$gcloud_project
  export user=$(gcloud config get-value account 2>/dev/null)
}

set_project() {
  echo "1. Setting active gcloud project..."
  gcloud config set project "${PROJECT_ID}"
}

setup_adc() {
  echo -e "\n2. Setting up Application Default Credentials (ADC)..."
  local adc_file="$HOME/.config/gcloud/application_default_credentials.json"
  local quota_project=""

  # Check if user is logged in with ADC
  if ! gcloud auth application-default print-access-token &>/dev/null; then
    echo "   - ADC not configured. Initiating login, please follow browser prompts."
    gcloud auth application-default login
  else
    echo "   - ✅ User is already logged in with ADC."
  fi

  # Check if the quota project is set correctly
  if [ -f "$adc_file" ]; then
    quota_project=$(jq -r '.quota_project_id' "$adc_file" 2>/dev/null || true)
  fi

  if [[ "$quota_project" != "$PROJECT_ID" ]]; then
    echo "   - ADC quota project is not set to '${PROJECT_ID}'. Setting it now..."
    gcloud auth application-default set-quota-project "${PROJECT_ID}"
    echo "     ✅ ADC quota project set."
  else
    echo "   - ✅ ADC quota project is already set correctly to '${PROJECT_ID}'."
  fi
}

enable_apis() {
  echo -e "3. Enabling required Google Cloud APIs..."
  echo "   - Enabling: ${REQUIRED_APIS[*]}"
  # Attempt to enable all APIs at once for speed, capturing stderr to check for specific errors.
  if ! gcloud services enable "${REQUIRED_APIS[@]}" --project="${PROJECT_ID}" 2> >(tee /dev/stderr | grep -q "FAILED_PRECONDITION: The terms of service"); then
    # The command failed, and the error was the ToS precondition.
    echo "❌ Terms of Service for one or more APIs must be accepted." >&2
    echo "   Please visit the following URL to accept the terms, then re-run this script:" >&2
    echo "   ➡ https://console.cloud.google.com/terms/cloud?project=${PROJECT_ID}" >&2
    exit 1
  elif [ ${PIPESTATUS[0]} -ne 0 ]; then
    # The command failed for a different reason.
    echo "❌ An unexpected error occurred while trying to enable APIs. Please review the error message above." >&2
    exit 1
  fi
  echo "   - ✅ All required APIs are enabled."
}

grant_iam_roles() {
  echo -e "4. Granting required IAM roles..."

  # Combine all admin roles into a single gcloud command for the setup user
  echo "   - Granting required admin roles to setup user ('${USER_EMAIL}')..."
  local admin_role_args=""
  for role in "${ADMIN_ROLES[@]}"; do
    admin_role_args+=" --role=$role"
  done
  if $DEBUG; then
    echo "🐞 DEBUG: gcloud projects add-iam-policy-binding \"${PROJECT_ID}\" --member=\"user:${USER_EMAIL}\" ${admin_role_args} --condition=None"
  fi
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" --member="user:${USER_EMAIL}" ${admin_role_args} --condition=None > /dev/null
  echo "     ✅ Granted: ${ADMIN_ROLES[*]}"

  # Combine all Gemini user roles into a single gcloud command for each Gemini user
  echo "   - Granting viewer roles to Gemini Enterprise users..."
  local gemini_user_role_args=""
  for role in "${GEMINI_USER_ROLES[@]}"; do
    gemini_user_role_args+=" --role=$role"
  done

  for user in "${GEMINI_USERS[@]}"; do
    echo "     - Granting roles to '${user}'..."
    if $DEBUG; then
      echo "🐞 DEBUG: gcloud projects add-iam-policy-binding \"${PROJECT_ID}\" --member=\"user:${user}\" ${gemini_user_role_args} --condition=None"
    fi
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" --member="user:${user}" ${gemini_user_role_args} --condition=None > /dev/null
    echo "       ✅ Granted: ${GEMINI_USER_ROLES[*]}"
  done
}

configure_idp() {
  echo -e "5. Configuring Discovery Engine Identity Provider (IdP)..."

  # This is required for ACL-enabled connectors like Google Drive and Gmail.
  # First, check if an IdP mapping store already exists to make the script idempotent.
  ACCESS_TOKEN=$(gcloud auth print-access-token)
  IDP_CHECK_URL="https://discoveryengine.googleapis.com/v1/projects/${PROJECT_ID}/locations/global/identityMappingStores"

  if $DEBUG; then
    echo "🐞 DEBUG: Checking for IdP at URL: ${IDP_CHECK_URL}"
    echo "🐞 DEBUG: curl -s -H \"Authorization: Bearer ...\" -H \"X-Goog-User-Project: ${PROJECT_ID}\" \"${IDP_CHECK_URL}\""
  fi

  IDP_RESPONSE=$(curl -s -H "Authorization: Bearer ${ACCESS_TOKEN}" -H "X-Goog-User-Project: ${PROJECT_ID}" "${IDP_CHECK_URL}")

  IDP_EXISTS=$(echo "${IDP_RESPONSE}" | jq '(.identityMappingStores | length // 0) > 0')

  if [[ "${IDP_EXISTS}" == "true" ]]; then
    echo "   - ✅ IdP is already configured."
  else
    echo "   - IdP not found. Attempting to create it..."

    # This is a workaround for a 'chicken-and-egg' API requirement.
    # We must first create a temporary aclConfig to "prime" the project,
    # which then allows the identityMappingStore to be created.
    echo "     - Priming project with temporary global ACL config..."
    ACL_CONFIG_URL="https://discoveryengine.googleapis.com/v1/projects/${PROJECT_ID}/locations/global/aclConfig"
    PRIME_CURL_COMMAND="curl -s -w '%{http_code}' -X PATCH \
      -H \"Authorization: Bearer ${ACCESS_TOKEN}\" \
      -H 'Content-Type: application/json' \
      -H \"X-Goog-User-Project: ${PROJECT_ID}\" \
      \"${ACL_CONFIG_URL}\" \
      -d '{\"idp_config\": {}}'
      "

    if $DEBUG; then
      echo "🐞 DEBUG: Priming IdP at URL: ${ACL_CONFIG_URL}"
      echo "🐞 DEBUG: ${PRIME_CURL_COMMAND}"
    fi
    PRIME_RESPONSE=$(eval "${PRIME_CURL_COMMAND}")  


    PRIME_HTTP_CODE=$(echo "$PRIME_RESPONSE" | tail -n1)
    if [[ "$PRIME_HTTP_CODE" -ne 200 ]]; then
        PRIME_BODY=$(echo "$PRIME_RESPONSE" | sed '$d')
        # A 404 here is okay, it means it was already primed. Any other error is a failure.
        if [[ "$PRIME_HTTP_CODE" -ne 404 ]]; then
            echo "   - ❌ Failed to prime project with ACL config." >&2
            echo "${PRIME_BODY}" >&2
        fi
    fi

    # Create a unique name for the store based on the project ID.
    IDP_STORE_ID="idp-for-${PROJECT_ID}"
    curl_url="${IDP_CHECK_URL}?identityMappingStoreId=${IDP_STORE_ID}"
    
   
    curl_command="curl -s -w '%{http_code}' \
      -X POST \
      -H 'Content-Type: application/json' \
      -H \"Authorization: Bearer ${ACCESS_TOKEN}\" \
      -H 'x-goog-user-project: ${PROJECT_ID}' \
      '${curl_url}' \
      -d '{\"name\": \"${IDP_STORE_ID}\"}'"

    if $DEBUG; then
      echo "🐞 DEBUG: Creating IdP at URL: ${curl_url}"
      echo "🐞 DEBUG: ${curl_command}"
    fi

    CREATE_HTTP_CODE=$(eval "${curl_command}")
    #CREATE_HTTP_CODE=$(echo "$CREATE_RESPONSE" | tail -n1)
    
    if [[ "$CREATE_HTTP_CODE" -ge 200 && "$CREATE_HTTP_CODE" -lt 300 ]]; then
      echo "   - ✅ Successfully created Identity Provider mapping store."
    else
      CREATE_BODY=$(echo "$CREATE_RESPONSE" | sed '$d')
      echo "   - ❌ Failed to create Identity Provider." >&2
      echo "     Received HTTP status ${CREATE_HTTP_CODE}. Error:" >&2
      echo "${CREATE_BODY}" >&2
      exit 1
    finally
      # Clean up the temporary ACL config.
      echo "     - Cleaning up temporary ACL config..."
      curl -s -X DELETE \
        -H "Authorization: Bearer ${ACCESS_TOKEN}" \
        -H "X-Goog-User-Project: ${PROJECT_ID}" \
        "${ACL_CONFIG_URL}" > /dev/null
    fi
  fi
}

main() {
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

  check_project_config
  # Get active user if not provided
  if [ -z "${USER_EMAIL}" ]; then
    USER_EMAIL=$(gcloud config get-value account 2>/dev/null)
    if [ -z "${USER_EMAIL}" ]; then
      echo "❌ Could not determine active gcloud user. Please login first or specify with -u flag."
      exit 1
    fi
  fi

  echo "🚀 Setting up environment for project '${PROJECT_ID}' and user '${USER_EMAIL}'..."

  set_project
  setup_adc
  enable_apis
  grant_iam_roles
  configure_idp

  echo -e "\n✅ Environment setup complete for project '${PROJECT_ID}'!"
  echo "Run './check_env.sh' to verify, then 'terraform apply' to deploy resources."
}

main
