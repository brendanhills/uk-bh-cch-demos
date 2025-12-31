#!/bin/bash

# A "doctor" script to check if the local environment is correctly set up
# to run Terraform against Google Cloud, specifically for GCS and Discovery Engine.

set -eo pipefail

DEBUG=false

# Source the common configuration file
source "$(dirname "$0")/config.sh"

# Function to check if a command exists
command_exists() {
  command -v "$1" &> /dev/null
}

check_project_config() {
  local gcloud_project
  gcloud_project=$(gcloud config get-value project 2>/dev/null)
  if [[ -z "${gcloud_project}" ]]; then
    echo "🗣 No GCP project is configured in gcloud. Please run: gcloud config set project YOUR_PROJECT_ID" >&2
    exit 1
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
  export project_id=$gcloud_project
  export user=$(gcloud config get-value account 2>/dev/null)
}

check_admin_roles() {
  echo "🔑 Checking for required admin IAM roles for '$user'..."
  local user_roles
  # Extract roles for the current user from the pre-fetched IAM policy
  user_roles=$(echo "$iam_policy" | jq -r --arg user "user:$user" '.[] | select(.bindings.members == $user) | .bindings.role')
  for role in "${ADMIN_ROLES[@]}"; do
    if grep -q "^$role$" <<< "$user_roles"; then
      echo "✅ IAM role found: $role"
    else
      echo "❌ Admin role missing for '$user': $role"
      echo "   ➡ To fix, run: gcloud projects add-iam-policy-binding $project_id --member=\"user:$user\" --role=\"$role\""
      exit 1
    fi
  done
}

check_gemini_user_roles() {
  echo "👥 Checking for Gemini Enterprise end-user roles..."
  for gemini_user in "${GEMINI_USERS[@]}"; do
    # Extract roles for the specific Gemini user from the pre-fetched IAM policy
    user_roles=$(echo "$iam_policy" | jq -r --arg user "user:$gemini_user" '.[] | select(.bindings.members == $user) | .bindings.role')
    for role in "${GEMINI_USER_ROLES[@]}"; do
      if grep -q "^$role$" <<< "$user_roles"; then
        echo "✅ Role '$role' found for user: $gemini_user"
      else
        all_checks_passed=false
        echo "❌ Role '$role' missing for user: $gemini_user"
        echo "   ➡ To fix, re-run the ./setup_env.sh script."
      fi
    done
  done
}

check_adc() {
  echo "💰 Checking for Application Default Credentials (ADC) quota project..."
  local adc_file="$HOME/.config/gcloud/application_default_credentials.json"
  local quota_project=""

  if ! gcloud auth application-default print-access-token &>/dev/null; then
    echo "❌ Application Default Credentials are not logged in."
    echo "   ➡ To fix, run: gcloud auth application-default login"
    exit 1
  elif [ -f "$adc_file" ]; then
      quota_project=$(jq -r '.quota_project_id' "$adc_file" 2>/dev/null || true)

      if [[ -z "$quota_project" || "$quota_project" == "null" ]]; then
        echo "❌ ADC quota project is not set."
        echo "   ➡ To fix, run: gcloud auth application-default set-quota-project $project_id"
        exit 1
      elif [[ "$quota_project" != "$project_id" ]]; then
        echo "❌ ADC quota project ('$quota_project') does not match active gcloud project ('$project_id')."
        echo "   ➡ To fix, run: gcloud auth application-default set-quota-project $project_id"
        exit 1
      else
        echo "✅ ADC quota project is set to: $quota_project"
      fi
  else
    echo "❌ ADC configuration file not found at $adc_file."
    echo "   ➡ To fix, run: gcloud auth application-default login"
    exit 1
  fi
}

check_apis() {
  echo "☁️ Checking for enabled APIs..."
  local enabled_apis_output
  enabled_apis_output=$(gcloud services list --enabled --project="$project_id" --format="value(NAME)" 2>/dev/null || true)

  for api in "${REQUIRED_APIS[@]}"; do
    if grep -q "^$api$" <<< "$enabled_apis_output"; then
      echo "✅ API enabled: $api"
    else
      all_checks_passed=false
      echo "❌ API not enabled: $api"
      echo "   ➡ To fix, run: gcloud services enable $api --project=$project_id"
    fi
  done
}

check_license() {
  echo "📜 Checking for Gemini Enterprise license..."
  local de_location="us" # Use a common location for the check
  if [ -f "terraform.tfvars" ]; then
      # If location is specified in tfvars, use it for a more accurate check
      tf_loc=$(grep -E '^\s*location\s*=' terraform.tfvars | sed -E 's/.*=\s*//' | tr -d '" ')
      if [ -n "$tf_loc" ]; then
          de_location=$tf_loc
      fi
  fi

  local license_check_output
  local access_token
  access_token=$(gcloud auth application-default print-access-token 2>/dev/null || true)

  if [ -z "$access_token" ]; then
      # This case is already handled by the ADC check, but as a safeguard:
      all_checks_passed=false
      echo "❌ Could not get authentication token to check license. Please run 'gcloud auth application-default login'."
      return
  fi

  # Make a single API call to get both status and output
  local response
  response=$(mktemp)
  local http_status

  # Build the command as a string to be printed and then executed with eval.
  # Using eval ensures that the nested quotes for headers are interpreted correctly.
  local curl_command
  curl_url="https://${de_location}-discoveryengine.googleapis.com/v1/projects/${project_id}/locations/${de_location}/userStores/default_user_store/userLicenses"
  if $DEBUG; then
    echo "curl_url ${curl_url}"
  fi

  curl_command="curl -s -w '%{http_code}' \
    -H 'Authorization: Bearer ${access_token}' \
    -H 'x-goog-user-project: ${project_id}' \
    '${curl_url}' \
    -o '${response}'"

  if $DEBUG; then
    echo "🐞 Preparing to execute curl command:"
    echo "${curl_command}"
  fi
  http_status=$(eval "${curl_command}")
  license_check_output=$(cat "$response")


  if [[ "$http_status" -eq 200 ]]; then
    # A 200 OK is good, but we must verify the 'userLicenses' array is not empty.
    # An empty array or object means the API is on, but no license is active.
    if [[ "$(jq '(.userLicenses | length // 0) > 0' "$response")" == "true" ]]; then
        echo "✅ Gemini Enterprise license is active. Found the following assignments:"
        # Parse the JSON response and print a summary for each license found.
        # Filter for only ASSIGNED licenses and handle cases where licenseConfig might be null.
        jq -r '.userLicenses[] | select(.licenseAssignmentState == "ASSIGNED") | "  - User: \(.userPrincipal), State: \(.licenseAssignmentState), Type: \(.licenseConfig // "N/A" | split("/")[-1])"' "$response"
    else
        all_checks_passed=false
        echo "❌ Gemini Enterprise license is not active for this project."
        echo "   The API call succeeded, but no active license was found in the response."
        echo "   ➡ To fix, you may need to start a trial. Follow these steps:"
        echo "     1. Navigate to: https://console.cloud.google.com/gemini-enterprise/start?project=$project_id"
        echo "     2. IMPORTANT: When prompted, make sure you choose the location '$de_location' to match your Terraform configuration."
        echo "     3. After activating the trial, wait a few minutes and re-run this script."
    fi
  else
    all_checks_passed=false
    echo "❌ Received HTTP status ${http_status} when checking the Gemini Enterprise license."
    #echo "Full error message:"
    #cat "$response"
        
    if grep -q "SERVICE_DISABLED" "$response"; then
        all_checks_passed=false
        echo "❌ Gemini Enterprise license may be missing or disabled for this project."
        echo "   The API returned a 'SERVICE_DISABLED' error."
        echo "   ➡ To fix, you may need to start a trial. Follow these steps:"
        echo "     1. Navigate to: https://console.cloud.google.com/gemini-enterprise/start"
        echo "     1. Navigate to: https://console.cloud.google.com/gemini-enterprise/start?project=$project_id"
        echo "     2. IMPORTANT: When prompted, make sure you choose the location '$de_location' to match your Terraform configuration."
        echo "     3. After activating the trial, wait a few minutes and re-run this script."
    else
        all_checks_passed=false
        echo "⚠️ Could not definitively check for Gemini Enterprise license. The API call failed with an unexpected error:"
        echo "--- Begin API Error (HTTP Status: $http_status) ---"
        echo "$license_check_output"
        echo "--- End API Error ---"
    fi
  fi
  rm -f "$response"

}

check_idp() {
  echo "🆔 Checking for Discovery Engine IdP configuration..."
  echo "⚠️ The check for IdP configuration has proven to be unreliable and is being skipped."
  echo "   Assuming you have followed the manual steps to configure the IdP."
  # The original check is commented out below for reference.
  #
  # local access_token
  # access_token=$(gcloud auth application-default print-access-token 2>/dev/null || true)
  #
  # if [ -z "$access_token" ]; then
  #     all_checks_passed=false
  #     echo "❌ Could not get authentication token to check IdP configuration. Please run 'gcloud auth application-default login'."
  #     return
  # fi
  #
  # local idp_check_url="https://discoveryengine.googleapis.com/v1/projects/${project_id}/locations/global/identityMappingStores"
  # local idp_response
  # idp_response=$(mktemp)
  # local idp_http_status
  #
  # local idp_curl_command="curl -s -w '%{http_code}' \
  #   -H 'Authorization: Bearer ${access_token}' \
  #   -H 'x-goog-user-project: ${project_id}' \
  #   '${idp_check_url}' \
  #   -o '${idp_response}'"
  #
  # idp_http_status=$(eval "${idp_curl_command}")
  #
  # if [[ "$idp_http_status" -eq 200 ]]; then
  #     # Check if the 'identityMappingStores' array exists and is not empty
  #     if [[ "$(jq '(.identityMappingStores | length // 0) > 0' "$idp_response")" == "true" ]]; then
  #         echo "✅ Discovery Engine IdP is configured."
  #     else
  #         all_checks_passed=false
  #         echo "❌ Discovery Engine IdP is not configured."
  #         echo "   This is a one-time setup required for connectors like Google Drive and Gmail."
  #         echo "   ➡ To fix, follow these manual steps:"
  #         echo "     1. Go to Data Stores in the console: https://console.cloud.google.com/gen-app-builder/data-stores?project=${project_id}"
  #         echo "     2. Click 'NEW DATA STORE' and select 'Google Drive'."
  #         echo "     3. In the configuration panel, click 'CONFIGURE' next to 'Identity provider'."
  #         echo "     4. Select 'Google Workspace', click 'SAVE', and then you can CANCEL the data store creation."
  #     fi
  # else
  #     all_checks_passed=false
  #     echo "⚠️ Could not check for IdP configuration. API call failed with HTTP status ${idp_http_status}."
  #     echo "--- Begin API Error ---"
  #     cat "${idp_response}"
  #     echo "--- End API Error ---"
  # fi
  # rm -f "$idp_response"
}

main() {
  if ! command_exists terraform; then
    echo "🗣 terraform command not found. Please install Terraform." >&2
    exit 1
  fi

  if ! command_exists gcloud; then
    echo "🗣 gcloud command not found. Please install the Google Cloud SDK and authenticate." >&2
    exit 1
  fi

  check_project_config
  echo "🔎 Checking environment for project '$project_id' and user '$user'..."

  # This global variable is used by check functions to track the overall status.
  all_checks_passed=true

  # Fetch the entire IAM policy once to avoid multiple gcloud calls.
  echo "Fetching project IAM policy for analysis..."
  iam_policy=$(gcloud projects get-iam-policy "$project_id" --flatten="bindings[].members" --format="json" 2>/dev/null)
  if [[ -z "$iam_policy" ]]; then
    echo "❌ Could not fetch IAM policy for project '$project_id'. Please check permissions."
    exit 1
  fi
  export iam_policy

  check_admin_roles
  echo
  check_gemini_user_roles
  echo
  check_adc
  echo
  check_apis
  echo
  check_license
  echo
  check_idp

  if [[ "$all_checks_passed" == true ]]; then
    echo -e "\n🎉 Your environment is correctly configured! You can now run 'terraform plan' and then 'terraform apply'."
  else
    echo -e "\n❗ Please run the suggested commands to fix your environment, then re-run this script to confirm all issues are resolved."
    exit 1
  fi
}

main
