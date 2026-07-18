#!/bin/bash

# Setup script for Conductor workflows in Antigravity

set -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REL_PATH="${SCRIPT_DIR}"
WORKFLOWS_DIR="${SCRIPT_DIR}/workflows"
GLOBAL_WORKFLOWS_DIR="${HOME}/.gemini/antigravity/global_workflows"

# Setup colored output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}Installing Conductor workflows for Antigravity...${NC}"

# Check Python & uv prerequisites
if ! command -v uv &> /dev/null; then
  echo -e "${YELLOW}Warning: uv is not installed. uv is recommended for fast dependency and test execution (https://github.com/astral-sh/uv).${NC}"
  if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Warning: python3 is not installed. Python 3.11+ is required for Conductor syntax validation tests.${NC}"
  else
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    IFS='.' read -r major minor <<< "$PYTHON_VERSION"
    if [ "$major" -lt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -lt 11 ]; }; then
      echo -e "${YELLOW}Warning: Python version $PYTHON_VERSION found. Conductor tests require Python 3.11+.${NC}"
    fi
  fi
else
  echo -e "  Found ${GREEN}uv $(uv --version | cut -d' ' -f2)${NC}!"
fi


# Check workflows directory
if [ ! -d "${WORKFLOWS_DIR}" ]; then
  echo -e "${RED}Error: Workflows directory ${WORKFLOWS_DIR} not found!${NC}"
  exit 1
fi

# Ensure target directories exist (e.g. on new installs where ~/.gemini/antigravity might be fresh)
echo -e "${BLUE}Ensuring Antigravity global workflows directory exists...${NC}"
mkdir -p "${GLOBAL_WORKFLOWS_DIR}"

# Install the workflows
for f in "${WORKFLOWS_DIR}"/conductor-*.md; do
  if [ -f "$f" ]; then
    filename=$(basename "$f")
    echo -e "  Installing ${BLUE}${filename}${NC}..."
    rm -f "${GLOBAL_WORKFLOWS_DIR}/${filename}"
    # Replace the relative commands/ path with the absolute path of this workspace
    sed "s|commands/|${REL_PATH}/commands/|g" "$f" > "${GLOBAL_WORKFLOWS_DIR}/${filename}"
  fi
done

echo -e "${GREEN}Workflows installed successfully to ${GLOBAL_WORKFLOWS_DIR}!${NC}"
