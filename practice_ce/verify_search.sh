#!/bin/bash

# Configuration
PROJECT_ID="376231489344"
LOCATION="us"
ENGINE_ID="agents-agentspace_1749039293552"

TOKEN=$(gcloud auth print-access-token)
if [ -z "$TOKEN" ]; then
  echo "Error: Could not get access token. Please run 'gcloud auth login' first."
  exit 1
fi

USER_EMAIL=$(gcloud config get-value account)
echo "========================================================"
echo "Running ACL Verification Suite for: $USER_EMAIL"
echo "========================================================"

# Helper function to run search
run_search() {
    local QUERY="$1"
    local EXPECTED_ID="$2"
    local SHOULD_FIND="$3" # "true" or "false"

    echo "--------------------------------------------------------"
    echo "Query: '$QUERY'"
    echo "Looking for Doc ID: $EXPECTED_ID"
    
    response=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    "https://$LOCATION-discoveryengine.googleapis.com/v1alpha/projects/$PROJECT_ID/locations/$LOCATION/collections/default_collection/engines/$ENGINE_ID/servingConfigs/default_search:search" \
    -d '{
      "query": "'"$QUERY"'",
      "pageSize": 5,
      "contentSearchSpec": {
        "snippetSpec": { "returnSnippet": true }
      }
    }')
    
    if echo "$response" | grep -q "\"id\": \"$EXPECTED_ID\""; then
        if [ "$SHOULD_FIND" == "true" ]; then
            echo "✅ PASS: Found $EXPECTED_ID (Allowed)"
        else
            echo "❌ FAIL: Found $EXPECTED_ID (Blocked)"
        fi
    else
        if [ "$SHOULD_FIND" == "true" ]; then
            echo "❌ FAIL: Did NOT find $EXPECTED_ID (Allowed)"
        else
            echo "✅ PASS: Did NOT find $EXPECTED_ID (Blocked)"
        fi
    fi
}

# 1. Test Public Document (Should See)
run_search "SEC Form 10-K" "RF-10K-2023" "true"

# 2. Test Restricted Document (Should Not See)
run_search "Suspicious Activity Report" "RF-SAR-994" "false"

# 3. Test Restricted Trading Rule (Should Not See)
run_search "Volcker Rule" "TR-004" "false"

# 4. Test Restricted Chinese Walls (Should Not See)
run_search "Chinese Walls" "TR-006" "false"

