#!/bin/bash

# Source environment variables if .env file exists
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Common configuration for setup_env.sh and check_env.sh
# This file defines the required APIs and IAM roles for the project.

REQUIRED_APIS=(
  "discoveryengine.googleapis.com"
  "storage.googleapis.com"
  "serviceusage.googleapis.com"
  "logging.googleapis.com"
  "aiplatform.googleapis.com"
  "cloudresourcemanager.googleapis.com"
  "iam.googleapis.com"
)

# Roles for the administrator account running the setup.
ADMIN_ROLES=(
  "roles/storage.admin"
  "roles/discoveryengine.admin"
  "roles/serviceusage.serviceUsageConsumer"
  "roles/logging.viewer"
  roles/aiplatform.user
)

# End-users to be granted viewer/user access to the Gemini Enterprise application.
GEMINI_USERS=(
    devstar1012@gcplab.me
    devstar1013@gcplab.me
)

# Roles to be granted to the Gemini Enterprise end-users.
GEMINI_USER_ROLES=(
  "roles/discoveryengine.viewer"
  "roles/discoveryengine.user"
  roles/aiplatform.user
)