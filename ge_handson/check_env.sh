#!/bin/bash

# A "doctor" script to check if the local environment is correctly set up
# to run Terraform against Google Cloud, specifically for GCS and Discovery Engine.

set -eo pipefail

# Function to check if a command exists
command_exists() {
  command -v "$1" &> /dev/null
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

  local gcloud_project
  gcloud_project=$(gcloud config get-value project 2>/dev/null)
  if [[ -z "$gcloud_project" ]]; then
    echo "🗣 No GCP project is configured in gcloud. Please run: gcloud config set project YOUR_PROJECT_ID" >&2
    exit 1
  fi

  # Check for project mismatch
  if [ -f "terraform.tfvars" ]; then
    tf_project=$(grep -E '^\s*project_id\s*=' terraform.tfvars | sed -E 's/.*=\s*//' | tr -d '" ')
    if [ -n "$tf_project" ] && [ "$gcloud_project" != "$tf_project" ]; then
      echo "❗ Mismatch Detected!"
      echo "  Your active gcloud project is:         '$gcloud_project'"
      echo "  Your terraform.tfvars project is:      '$tf_project'"
      echo "  These should match to avoid applying permissions to the wrong project."
      echo "
  To fix, run: gcloud config set project $tf_project"
      exit 1
    fi
  fi

  local project_id=$gcloud_project
  local user
  user=$(gcloud config get-value account 2>/dev/null)
  echo "🔎 Checking environment for project '$project_id' and user '$user'...
"

  local all_checks_passed=true

  # 1. Check for required IAM roles
  echo "🔑 Checking for required IAM roles..."
  local required_roles=("roles/storage.admin" "roles/discoveryengine.admin")
  local user_roles

  user_roles=$(gcloud projects get-iam-policy "$project_id" --flatten="bindings[].members" --format="json" 2>/dev/null | jq -r --arg user "user:$user" '.[] | select(.bindings.members == $user) | .bindings.role' || true)

  for role in "${required_roles[@]}"; do
    if grep -q "^$role$" <<< "$user_roles"; then
      echo "✅ IAM role found: $role"
    else
      all_checks_passed=false
      echo "❌ IAM role missing: $role"
      echo "   ➡ To fix, run: gcloud projects add-iam-policy-binding $project_id --member=\"user:$user\" --role=\"$role\""
    fi
  done

  # 2. Check for ADC quota project
  echo "
💰 Checking for Application Default Credentials (ADC) quota project..."
  local adc_file="$HOME/.config/gcloud/application_default_credentials.json"
  local quota_project=""

  if ! gcloud auth application-default print-access-token &>/dev/null; then
    all_checks_passed=false
    echo "❌ Application Default Credentials are not logged in."
    echo "   ➡ To fix, run: gcloud auth application-default login"
  elif [ -f "$adc_file" ]; then
      quota_project=$(jq -r '.quota_project_id' "$adc_file" 2>/dev/null || true)

      if [[ -z "$quota_project" || "$quota_project" == "null" ]]; then
        all_checks_passed=false
        echo "❌ ADC quota project is not set."
        echo "   ➡ To fix, run: gcloud auth application-default set-quota-project $project_id"
      elif [[ "$quota_project" != "$project_id" ]]; then
        all_checks_passed=false
        echo "❌ ADC quota project ('$quota_project') does not match active gcloud project ('$project_id')."
        echo "   ➡ To fix, run: gcloud auth application-default set-quota-project $project_id"
      else
        echo "✅ ADC quota project is set to: $quota_project"
      fi
  else
    all_checks_passed=false
    echo "❌ ADC configuration file not found at $adc_file."
    echo "   ➡ To fix, run: gcloud auth application-default login"
  fi

  # 3. Check for required APIs
  echo "
☁️ Checking for enabled APIs..."
  local required_apis=("discoveryengine.googleapis.com" "storage.googleapis.com")
  local enabled_apis_output
  enabled_apis_output=$(gcloud services list --enabled --project="$project_id" --format="value(NAME)" 2>/dev/null || true)

  for api in "${required_apis[@]}"; do
    if grep -q "^$api$" <<< "$enabled_apis_output"; then
      echo "✅ API enabled: $api"
    else
      all_checks_passed=false
      echo "❌ API not enabled: $api"
      echo "   ➡ To fix, run: gcloud services enable $api --project=$project_id"
    fi
  done

  # 4. Check for Gemini Enterprise License/Entitlement
  echo "
📜 Checking for Gemini Enterprise license..."
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

  local http_status
  local license_is_active=false

  http_status=$(curl -s -o /dev/null -w "% {http_code}" -H "Authorization: Bearer $access_token" "https://discoveryengine.googleapis.com/v1/projects/$project_id/locations/$de_location/collections/default_collection/engines")
  license_check_output=$(curl -s -H "Authorization: Bearer $access_token" "https://discoveryengine.googleapis.com/v1/projects/$project_id/locations/$de_location/collections/default_collection/engines")

  if [[ "$http_status" -eq 200 ]]; then
    license_is_active=true
  fi

  if [[ "$license_is_active" == true ]]; then
    echo "✅ Gemini Enterprise license appears to be active."
  else
    if echo "$license_check_output" | grep -q "SERVICE_DISABLED"; then
        all_checks_passed=false
        echo "❌ Gemini Enterprise license may be missing or disabled for this project."
        echo "   The API returned a 'SERVICE_DISABLED' error."
        echo "   ➡ To fix, you may need to start a trial. Follow these steps:"
        echo "     1. Navigate to: https://console.cloud.google.com/gemini-enterprise/start"
        echo "     2. Click the blue \"Start 30-day cost-free trial\" button."
        echo "     3. IMPORTANT: When prompted, make sure you choose the location '$de_location' to match your Terraform configuration."
        echo "     4. After activating the trial, wait a few minutes and re-run this script."
    else
        all_checks_passed=false
        echo "⚠️ Could not definitively check for Gemini Enterprise license. The API call failed with an unexpected error:"
        echo "--- Begin API Error (HTTP Status: $http_status) ---"
        echo "$license_check_output"
        echo "--- End API Error ---"
    fi
  fi

  # Final summary
  if [[ "$all_checks_passed" == true ]]; then
    echo "🎉 Your environment is correctly configured! You can now run 'terraform plan' and then 'terraform apply'."
  else
    echo "❗ Please run the suggested commands to fix your environment, then re-run this script to confirm all issues are resolved."
    exit 1
  fi
}

main
