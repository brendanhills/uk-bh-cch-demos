#!/bin/bash
# Install script for Custom Harness (Antigravity & Jetski)

set -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
GLOBAL_SKILLS_DIR="${HOME}/.gemini/config/skills"
GLOBAL_AGENTS_DIR="${HOME}/.gemini/config/agents"
GLOBAL_PLUGINS_DIR="${HOME}/.gemini/config/plugins"
GLOBAL_HOOKS_DIR="${HOME}/.gemini/config/hooks"

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
      echo "  --global              Install skills, plugins, hooks, and scripts globally to ~/.gemini/config/ (default)"
      echo "  --local <dir_path>    Install skills, plugins, hooks, and scripts locally to <dir_path>/.agents/"
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
  DEST_AGENTS_DIR="${GLOBAL_AGENTS_DIR}"
  DEST_PLUGINS_DIR="${GLOBAL_PLUGINS_DIR}"
  mkdir -p "${DEST_SKILLS_DIR}"
  mkdir -p "${DEST_PLUGINS_DIR}"
  echo -e "  Target: ${GREEN}Global (${DEST_SKILLS_DIR})${NC}"
else
  DEST_SKILLS_DIR="${TARGET_DIR}/.agents/skills"
  DEST_AGENTS_DIR="${TARGET_DIR}/.agents"
  DEST_PLUGINS_DIR="${TARGET_DIR}/.agents/plugins"
  mkdir -p "${DEST_SKILLS_DIR}"
  mkdir -p "${DEST_PLUGINS_DIR}"
  echo -e "  Target: ${GREEN}Local (${DEST_SKILLS_DIR})${NC}"
fi

# 1. Install plugins
if [ -d "${SCRIPT_DIR}/.agents/plugins" ]; then
  for plugin in "${SCRIPT_DIR}/.agents/plugins"/*; do
    if [ -d "$plugin" ]; then
      plugin_name=$(basename "$plugin")
      echo -e "  Installing plugin: ${BLUE}${plugin_name}${NC}"
      if [ "$TARGET_MODE" == "global" ]; then
        ln -sfn "$plugin" "${DEST_PLUGINS_DIR}/${plugin_name}"
      else
        rm -rf "${DEST_PLUGINS_DIR}/${plugin_name}"
        cp -r "$plugin" "${DEST_PLUGINS_DIR}/${plugin_name}"
      fi
    fi
  done
fi

# Install Conductor plugin
if [ -d "${SCRIPT_DIR}/conductor" ] && [ -f "${SCRIPT_DIR}/conductor/plugin.json" ]; then
  echo -e "  Installing Conductor plugin: ${BLUE}conductor${NC}"
  if [ "$TARGET_MODE" == "global" ]; then
    ln -sfn "${SCRIPT_DIR}/conductor" "${DEST_PLUGINS_DIR}/conductor"
  else
    rm -rf "${DEST_PLUGINS_DIR}/conductor"
    cp -r "${SCRIPT_DIR}/conductor" "${DEST_PLUGINS_DIR}/conductor"
  fi
fi

# 2. Copy standalone skills from .agents/skills
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

# 3. Copy hooks and scripts
if [ -d "${SCRIPT_DIR}/.agents/hooks" ]; then
  mkdir -p "${DEST_AGENTS_DIR}/hooks"
  cp -r "${SCRIPT_DIR}/.agents/hooks/"* "${DEST_AGENTS_DIR}/hooks/"
  chmod +x "${DEST_AGENTS_DIR}/hooks/"*.py 2>/dev/null || true
fi

if [ -f "${SCRIPT_DIR}/.agents/hooks.json" ]; then
  cp "${SCRIPT_DIR}/.agents/hooks.json" "${DEST_AGENTS_DIR}/hooks.json"
fi

if [ -d "${SCRIPT_DIR}/.agents/scripts" ]; then
  mkdir -p "${DEST_AGENTS_DIR}/scripts"
  cp -r "${SCRIPT_DIR}/.agents/scripts/"* "${DEST_AGENTS_DIR}/scripts/"
  chmod +x "${DEST_AGENTS_DIR}/scripts/"*.py 2>/dev/null || true
fi

if [ -f "${SCRIPT_DIR}/.agents/prompt_heuristics.md" ]; then
  cp "${SCRIPT_DIR}/.agents/prompt_heuristics.md" "${DEST_AGENTS_DIR}/prompt_heuristics.md"
fi

echo -e "${GREEN}Custom Harness installed successfully!${NC}"
