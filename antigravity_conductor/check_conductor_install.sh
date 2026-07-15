#!/usr/bin/env bash

# Diagnostics script to check if the custom Conductor extension is installed and up-to-date

set -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
LOCAL_PLUGIN_DIR="${SCRIPT_DIR}/conductor"
LOCAL_COMMANDS_DIR="${SCRIPT_DIR}/commands"
LOCAL_WORKFLOWS_DIR="${SCRIPT_DIR}/workflows"
REL_PATH="${SCRIPT_DIR}"

GLOBAL_PLUGINS_DIR="${HOME}/.gemini/config/plugins/conductor"
CLI_PLUGINS_DIR="${HOME}/.gemini/antigravity-cli/plugins/conductor"
GLOBAL_WORKFLOWS_DIR="${HOME}/.gemini/antigravity/global_workflows"

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE} Checking Conductor Installation Integrity...         ${NC}"
echo -e "${BLUE}======================================================${NC}"

INSTALLED=true
UP_TO_DATE=true
MISMATCHED_FILES=()

# 1. Check if directories exist
echo -e "\n[+] Checking directories..."
if [ ! -d "${GLOBAL_PLUGINS_DIR}" ]; then
  echo -e "  [${RED}✗${NC}] Global config plugin not found at: ${GLOBAL_PLUGINS_DIR}"
  INSTALLED=false
else
  echo -e "  [${GREEN}✓${NC}] Global config plugin directory exists."
fi

if [ ! -d "${CLI_PLUGINS_DIR}" ]; then
  echo -e "  [${RED}✗${NC}] CLI plugin not found at: ${CLI_PLUGINS_DIR}"
  INSTALLED=false
else
  echo -e "  [${GREEN}✓${NC}] CLI plugin directory exists."
fi

if [ ! -d "${GLOBAL_WORKFLOWS_DIR}" ]; then
  echo -e "  [${RED}✗${NC}] Global workflows directory not found at: ${GLOBAL_WORKFLOWS_DIR}"
  INSTALLED=false
else
  echo -e "  [${GREEN}✓${NC}] Global workflows directory exists."
fi

# Print metadata versions if present
if [ -f "${SCRIPT_DIR}/metadata.json" ]; then
  LOCAL_VER=$(python3 -c "import json; print(json.load(open('${SCRIPT_DIR}/metadata.json'))['version'])")
  LOCAL_DATE=$(python3 -c "import json; print(json.load(open('${SCRIPT_DIR}/metadata.json'))['last_updated'])")
  echo -e "\n  Local Workspace Version:  ${BLUE}${LOCAL_VER}${NC} (Released: ${LOCAL_DATE})"
fi

if [ -f "${GLOBAL_PLUGINS_DIR}/metadata.json" ]; then
  INSTALLED_VER=$(python3 -c "import json; print(json.load(open('${GLOBAL_PLUGINS_DIR}/metadata.json'))['version'])")
  INSTALLED_DATE=$(python3 -c "import json; print(json.load(open('${GLOBAL_PLUGINS_DIR}/metadata.json'))['last_updated'])")
  echo -e "  Installed Global Version: ${GREEN}${INSTALLED_VER}${NC} (Released: ${INSTALLED_DATE})"
fi


if [ "$INSTALLED" = false ]; then
  echo -e "\n${RED}======================================================${NC}"
  echo -e "${RED} Status: NOT INSTALLED${NC}"
  echo -e " One or more of the required directories are missing."
  echo -e " To perform a fresh global installation, run:"
  echo -e "   ${BLUE}./install_conductor.sh${NC}"
  echo -e "${RED}======================================================${NC}"
  exit 0
fi

# 2. Check if files are up to date
echo -e "\n[+] Comparing local source with installed files..."

# Check workflows
for wf_path in "${LOCAL_WORKFLOWS_DIR}"/conductor-*.md; do
  if [ -f "${wf_path}" ]; then
    filename=$(basename "${wf_path}")
    installed_wf_path="${GLOBAL_WORKFLOWS_DIR}/${filename}"
    
    if [ ! -f "${installed_wf_path}" ]; then
      UP_TO_DATE=false
      MISMATCHED_FILES+=("workflows/${filename} (Missing globally)")
    else
      # Compile local file in-memory using sed (matching install logic) to compare
      local_compiled=$(sed "s|commands/|${REL_PATH}/commands/|g" "${wf_path}")
      installed_content=$(cat "${installed_wf_path}")
      
      if [ "${local_compiled}" != "${installed_content}" ]; then
        UP_TO_DATE=false
        MISMATCHED_FILES+=("workflows/${filename} (Diverged/Out-of-date)")
      fi
    fi
  fi
done

# Check plugin skills/templates/policies/gemini-extension.json files
if [ -d "${LOCAL_PLUGIN_DIR}" ]; then
  # Compare all files recursively in conductor submodule
  cd "${LOCAL_PLUGIN_DIR}"
  find . -type f | while read -r relative_file; do
    # Skip temporary, local-only, or git files
    if [[ "${relative_file}" == *".git"* ]]; then
      continue
    fi
    local_file="${LOCAL_PLUGIN_DIR}/${relative_file}"
    global_installed_file="${GLOBAL_PLUGINS_DIR}/${relative_file}"
    cli_installed_file="${CLI_PLUGINS_DIR}/${relative_file}"
    
    # Check global config file
    if [ ! -f "${global_installed_file}" ]; then
      UP_TO_DATE=false
      echo "mismatch" > "${SCRIPT_DIR}/.mismatch_flag"
      echo "conductor/${relative_file} (Missing in ~/.gemini/config/plugins)" >> "${SCRIPT_DIR}/.mismatch_list"
    elif ! cmp -s "${local_file}" "${global_installed_file}"; then
      UP_TO_DATE=false
      echo "mismatch" > "${SCRIPT_DIR}/.mismatch_flag"
      echo "conductor/${relative_file} (Out-of-date in ~/.gemini/config/plugins)" >> "${SCRIPT_DIR}/.mismatch_list"
    fi
    
    # Check CLI file
    if [ ! -f "${cli_installed_file}" ]; then
      UP_TO_DATE=false
      echo "mismatch" > "${SCRIPT_DIR}/.mismatch_flag"
      echo "conductor/${relative_file} (Missing in ~/.gemini/antigravity-cli/plugins)" >> "${SCRIPT_DIR}/.mismatch_list"
    elif ! cmp -s "${local_file}" "${cli_installed_file}"; then
      UP_TO_DATE=false
      echo "mismatch" > "${SCRIPT_DIR}/.mismatch_flag"
      echo "conductor/${relative_file} (Out-of-date in ~/.gemini/antigravity-cli/plugins)" >> "${SCRIPT_DIR}/.mismatch_list"
    fi
  done
  cd "${SCRIPT_DIR}"
fi

# Clean up and load background checks
if [ -f "${SCRIPT_DIR}/.mismatch_flag" ]; then
  UP_TO_DATE=false
  while read -r line; do
    MISMATCHED_FILES+=("$line")
  done < "${SCRIPT_DIR}/.mismatch_list"
  rm -f "${SCRIPT_DIR}/.mismatch_flag" "${SCRIPT_DIR}/.mismatch_list"
fi

# 3. Report Results
if [ "$UP_TO_DATE" = true ]; then
  echo -e "\n${GREEN}======================================================${NC}"
  echo -e "${GREEN} Status: INSTALLED & UP-TO-DATE (100% Synced) [✓]${NC}"
  echo -e " Your installed Conductor is completely in sync with"
  echo -e " your local repository changes."
  echo -e "${GREEN}======================================================${NC}"
else
  echo -e "\n${YELLOW}======================================================${NC}"
  echo -e "${YELLOW} Status: INSTALLED BUT OUT-OF-DATE [✗]${NC}"
  echo -e " Your local source code has changes that are not yet"
  echo -e " active in your global installation folders."
  echo -e "\n Out-of-sync items:"
  for item in "${MISMATCHED_FILES[@]}"; do
    echo -e "   - ${RED}${item}${NC}"
  done
  echo -e "\n To push your local changes and update globally, run:"
  echo -e "   ${BLUE}./install_conductor.sh${NC}"
  echo -e "${YELLOW}======================================================${NC}"
fi
