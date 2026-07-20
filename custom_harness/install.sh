#!/bin/bash
# Install script for Custom Harness (Antigravity & Jetski)

set -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
GLOBAL_SKILLS_DIR="${HOME}/.gemini/config/skills"
GLOBAL_AGENTS_DIR="${HOME}/.gemini/config/agents"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

TARGET_MODE="global"
TARGET_DIR=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --global)
      TARGET_MODE="global"
      shift
      ;;
    --local)
      TARGET_MODE="local"
      TARGET_DIR="$2"
      if [ -z "$TARGET_DIR" ]; then
        echo -e "${RED}Error: --local requires a target workspace directory path.${NC}"
        exit 1
      fi
      shift 2
      ;;
    --help|-h)
      echo "Usage: ./install.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --global              Install skills globally to ~/.gemini/config/skills/ (default)"
      echo "  --local <dir_path>    Install skills locally to <dir_path>/.agents/skills/"
      echo "  --help, -h            Show this help message"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown argument: $1${NC}"
      exit 1
      ;;
  esac
done

echo -e "${BLUE}Installing Custom Harness for Antigravity & Jetski...${NC}"

if [ "$TARGET_MODE" == "global" ]; then
  DEST_SKILLS_DIR="${GLOBAL_SKILLS_DIR}"
  mkdir -p "${DEST_SKILLS_DIR}"
  echo -e "  Target: ${GREEN}Global (${DEST_SKILLS_DIR})${NC}"
else
  DEST_SKILLS_DIR="${TARGET_DIR}/.agents/skills"
  mkdir -p "${DEST_SKILLS_DIR}"
  echo -e "  Target: ${GREEN}Local (${DEST_SKILLS_DIR})${NC}"
fi

# Copy skills
if [ -d "${SCRIPT_DIR}/.agents/skills" ]; then
  for skill in "${SCRIPT_DIR}/.agents/skills"/*; do
    if [ -d "$skill" ]; then
      skill_name=$(basename "$skill")
      echo -e "  Installing skill: ${BLUE}${skill_name}${NC}"
      rm -rf "${DEST_SKILLS_DIR}/${skill_name}"
      cp -r "$skill" "${DEST_SKILLS_DIR}/${skill_name}"
    fi
  done
fi

echo -e "${GREEN}Custom Harness installed successfully!${NC}"
