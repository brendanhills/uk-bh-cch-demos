#!/usr/bin/env bash

# Uninstall script for Conductor plugin and workflows in Antigravity

set -e

GLOBAL_PLUGINS_DIR="${HOME}/.gemini/config/plugins/conductor"
CLI_PLUGINS_DIR="${HOME}/.gemini/antigravity-cli/plugins/conductor"
GLOBAL_WORKFLOWS_DIR="${HOME}/.gemini/antigravity/global_workflows"

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}======================================================${NC}"
echo -e "${YELLOW} Removing Conductor Plugin and Workflows globally...  ${NC}"
echo -e "${YELLOW}======================================================${NC}"

# 1. Remove from global config plugins
if [ -d "${GLOBAL_PLUGINS_DIR}" ]; then
  echo -e "  Removing ${RED}${GLOBAL_PLUGINS_DIR}${NC}..."
  rm -rf "${GLOBAL_PLUGINS_DIR}"
  echo -e "  ${GREEN}Removed global config plugin!${NC}"
else
  echo -e "  No global config plugin found at ${GLOBAL_PLUGINS_DIR}."
fi

# 2. Remove from CLI config plugins
if [ -d "${CLI_PLUGINS_DIR}" ]; then
  echo -e "  Removing ${RED}${CLI_PLUGINS_DIR}${NC}..."
  rm -rf "${CLI_PLUGINS_DIR}"
  echo -e "  ${GREEN}Removed CLI plugin!${NC}"
else
  echo -e "  No CLI plugin found at ${CLI_PLUGINS_DIR}."
fi

# 3. Remove global workflows files
echo -e "\n${BLUE}[+] Removing global workflows...${NC}"
WORKFLOW_REMOVED=0
for f in "${GLOBAL_WORKFLOWS_DIR}"/conductor-*.md; do
  if [ -f "$f" ]; then
    filename=$(basename "$f")
    echo -e "  Removing workflow: ${RED}${filename}${NC}..."
    rm -f "$f"
    WORKFLOW_REMOVED=$((WORKFLOW_REMOVED + 1))
  fi
done

if [ "$WORKFLOW_REMOVED" -eq 0 ]; then
  echo -e "  No global Conductor workflows found in ${GLOBAL_WORKFLOWS_DIR}."
else
  echo -e "  ${GREEN}Successfully removed ${WORKFLOW_REMOVED} workflows!${NC}"
fi

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN} Uninstallation completed successfully!${NC}"
echo -e " Conductor has been removed and is no longer active."
echo -e "${GREEN}======================================================${NC}"
