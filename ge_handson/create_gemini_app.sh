#!/bin/bash

# Script to create a Gemini Enterprise app (engine) using the REST API.

set -eo pipefail

usage() {
  echo "Usage: $0 -p <PROJECT_ID> -a <APP_ID> -d <APP_DISPLAY_NAME> -s <DATA_STORE_IDS> -l <LOCATION>"
  echo "  -p PROJECT_ID: Your Google Cloud project ID."
  echo "  -a APP_ID: The ID for the new Gemini Enterprise app."
  echo "  -d APP_DISPLAY_NAME: The display name for the new app."
  echo "  -s DATA_STORE_IDS: A comma-separated list of data store IDs to connect to the app."
  echo "  -l LOCATION: The location of the data stores (e.g., 'global' or 'us')."
  exit 1
}

while getopts ":p:a:d:s:l:" opt; do
  case ${opt} in
    p )
      PROJECT_ID=$OPTARG
      ;;
    a )
      APP_ID=$OPTARG
      ;;
    d )
      APP_DISPLAY_NAME=$OPTARG
      ;;
    s )
      DATA_STORE_IDS=$OPTARG
      ;;
    l )
      LOCATION=$OPTARG
      ;;
    \? )
      usage
      ;;
  esac
done

if [ -z "${PROJECT_ID}" ] || [ -z "${APP_ID}" ] || [ -z "${APP_DISPLAY_NAME}" ] || [ -z "${DATA_STORE_IDS}" ] || [ -z "${LOCATION}" ]; then
  usage
fi

# Check for gcloud and jq
if ! command -v gcloud &> /dev/null; then
    echo "gcloud command not found. Please install the Google Cloud SDK." >&2
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "jq command not found. Please install jq." >&2
    exit 1
fi

# Verify data stores exist
echo "Verifying data stores..."
for DATA_STORE_ID in $(echo "${DATA_STORE_IDS}" | tr ',' ' '); do
  echo "  - Checking for data store: ${DATA_STORE_ID}"
  if ! gcloud discovery-engine data-stores describe "${DATA_STORE_ID}" --project="${PROJECT_ID}" --location="${LOCATION}" &> /dev/null; then
    echo "Error: Data store '${DATA_STORE_ID}' not found in project '${PROJECT_ID}' and location '${LOCATION}'." >&2
    exit 1
  fi
done
echo "All data stores verified successfully."


ACCESS_TOKEN=$(gcloud auth print-access-token)

# Construct the JSON payload with a dynamic list of data store IDs
DATA_STORE_JSON=$(echo "${DATA_STORE_IDS}" | tr ',' '\n' | jq -R '.' | jq -s '.')

JSON_PAYLOAD=$(jq -n --arg name "${APP_DISPLAY_NAME}" --argjson stores "${DATA_STORE_JSON}" \
  '{
    "displayName": $name,
    "dataStoreIds": $stores,
    "solutionType": "SOLUTION_TYPE_SEARCH",
    "industryVertical": "GENERIC",
    "appType": "APP_TYPE_INTRANET"
  }')

API_URL="https://discoveryengine.googleapis.com/v1/projects/${PROJECT_ID}/locations/global/collections/default_collection/engines?engineId=${APP_ID}"


echo "Creating Gemini Enterprise app..."

curl -X POST \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Goog-User-Project: ${PROJECT_ID}" \
  "${API_URL}" \
  -d "${JSON_PAYLOAD}"

echo -e "\n\nApp creation request sent successfully."

