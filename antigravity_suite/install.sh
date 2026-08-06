#!/usr/bin/env bash
# Root installer and management script for the Antigravity Suite

set -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
GLOBAL_SKILLS_DIR="${HOME}/.gemini/config/skills"
GLOBAL_AGENTS_DIR="${HOME}/.gemini/config/agents"

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Function to display help menu
show_help() {
  echo "Usage: ./install.sh [OPTIONS]"
  echo ""
  echo "Default (no options): Perform a clean global installation of skills, rules, and hooks."
  echo ""
  echo "Options:"
  echo "  --diagnose          Perform integrity and version checks on the installation."
  echo "  --repair            Safely stop hung processes and synchronize project configurations."
  echo "  --help, -h          Show this help message."
}

# Function to perform default global installation
perform_install() {
  echo -e "${BLUE}======================================================${NC}"
  echo -e "${BLUE} Installing Antigravity Suite Globally...             ${NC}"
  echo -e "${BLUE}======================================================${NC}"

  # 1. Create target directories
  mkdir -p "${GLOBAL_SKILLS_DIR}"
  mkdir -p "${GLOBAL_AGENTS_DIR}"

  echo -e "  Target: ${GREEN}Global (${GLOBAL_SKILLS_DIR})${NC}\n"

  # 2. Copy harness skills
  if [ -d "${SCRIPT_DIR}/harness/skills" ]; then
    for skill in "${SCRIPT_DIR}/harness/skills"/*; do
      if [ -d "$skill" ]; then
        skill_name=$(basename "$skill")
        echo -e "  [+] Installing harness skill: ${BLUE}${skill_name}${NC}"
        rm -rf "${GLOBAL_SKILLS_DIR}/${skill_name}"
        cp -r "$skill" "${GLOBAL_SKILLS_DIR}/${skill_name}"
      fi
    done
  fi

  # 3. Copy Conductor skills
  if [ -d "${SCRIPT_DIR}/conductor/skills" ]; then
    for skill in "${SCRIPT_DIR}/conductor/skills"/*; do
      if [ -d "$skill" ]; then
        skill_name=$(basename "$skill")
        echo -e "  [+] Installing Conductor skill: ${BLUE}${skill_name}${NC}"
        rm -rf "${GLOBAL_SKILLS_DIR}/${skill_name}"
        cp -r "$skill" "${GLOBAL_SKILLS_DIR}/${skill_name}"
      fi
    done
  fi

  # 4. Copy rules
  if [ -d "${SCRIPT_DIR}/.agents/rules" ]; then
    echo -e "  [+] Copying rules..."
    mkdir -p "${GLOBAL_AGENTS_DIR}/rules"
    cp -r "${SCRIPT_DIR}/.agents/rules/"* "${GLOBAL_AGENTS_DIR}/rules/"
  fi

  # 5. Copy hooks
  if [ -d "${SCRIPT_DIR}/.agents/hooks" ]; then
    echo -e "  [+] Copying invocation hooks..."
    mkdir -p "${GLOBAL_AGENTS_DIR}/hooks"
    cp -r "${SCRIPT_DIR}/.agents/hooks/"* "${GLOBAL_AGENTS_DIR}/hooks/"
    chmod +x "${GLOBAL_AGENTS_DIR}/hooks/"*.py 2>/dev/null || true
  fi

  if [ -f "${SCRIPT_DIR}/.agents/hooks.json" ]; then
    cp "${SCRIPT_DIR}/.agents/hooks.json" "${GLOBAL_AGENTS_DIR}/hooks.json"
  fi

  # 6. Copy scripts
  if [ -d "${SCRIPT_DIR}/.agents/scripts" ]; then
    echo -e "  [+] Copying CLI scripts..."
    mkdir -p "${GLOBAL_AGENTS_DIR}/scripts"
    cp -r "${SCRIPT_DIR}/.agents/scripts/"* "${GLOBAL_AGENTS_DIR}/scripts/"
    chmod +x "${GLOBAL_AGENTS_DIR}/scripts/"*.py 2>/dev/null || true
  fi

  # 7. Copy prompt heuristics config
  if [ -f "${SCRIPT_DIR}/.agents/prompt_heuristics.md" ]; then
    cp "${SCRIPT_DIR}/.agents/prompt_heuristics.md" "${GLOBAL_AGENTS_DIR}/prompt_heuristics.md"
  fi

  echo -e "\n${GREEN}======================================================${NC}"
  echo -e "${GREEN} Antigravity Suite installed successfully!           ${NC}"
  echo -e "${GREEN}======================================================${NC}"
}

# Function to diagnose installation integrity
perform_diagnose() {
  echo -e "${BLUE}======================================================${NC}"
  echo -e "${BLUE} Diagnosing Installation Integrity...                 ${NC}"
  echo -e "${BLUE}======================================================${NC}"

  INSTALLED=true

  # Check directories
  if [ ! -d "${GLOBAL_SKILLS_DIR}" ]; then
    echo -e "  [${RED}✗${NC}] Global skills directory missing: ${GLOBAL_SKILLS_DIR}"
    INSTALLED=false
  else
    echo -e "  [${GREEN}✓${NC}] Global skills directory exists."
  fi

  if [ ! -d "${GLOBAL_AGENTS_DIR}" ]; then
    echo -e "  [${RED}✗${NC}] Global config agents directory missing: ${GLOBAL_AGENTS_DIR}"
    INSTALLED=false
  else
    echo -e "  [${GREEN}✓${NC}] Global config agents directory exists."
  fi

  # Check active skills
  if [ -d "${SCRIPT_DIR}/harness/skills" ]; then
    for skill in "${SCRIPT_DIR}/harness/skills"/*; do
      if [ -d "$skill" ]; then
        skill_name=$(basename "$skill")
        if [ ! -d "${GLOBAL_SKILLS_DIR}/${skill_name}" ]; then
          echo -e "  [${RED}✗${NC}] Missing skill in global config: ${skill_name}"
          INSTALLED=false
        fi
      fi
    done
  fi

  # Check active Conductor skills
  if [ -d "${SCRIPT_DIR}/conductor/skills" ]; then
    for skill in "${SCRIPT_DIR}/conductor/skills"/*; do
      if [ -d "$skill" ]; then
        skill_name=$(basename "$skill")
        if [ ! -d "${GLOBAL_SKILLS_DIR}/${skill_name}" ]; then
          echo -e "  [${RED}✗${NC}] Missing Conductor skill in global config: ${skill_name}"
          INSTALLED=false
        fi
      fi
    done
  fi

  if [ "$INSTALLED" = true ]; then
    echo -e "\n${GREEN}======================================================${NC}"
    echo -e "${GREEN} Status: INSTALLED & UP-TO-DATE (100% Synced) [✓]     ${NC}"
    echo -e "${GREEN}======================================================${NC}"
  else
    echo -e "\n${YELLOW}======================================================${NC}"
    echo -e "${YELLOW} Status: INCOMPLETE / OUT-OF-DATE [✗]                 ${NC}"
    echo -e " Run ${BLUE}./install.sh${NC} to perform a fresh global installation."
    echo -e "${YELLOW}======================================================${NC}"
  fi
}

# Function to execute repair operations
perform_repair() {
  echo -e "${BLUE}======================================================${NC}"
  echo -e "${BLUE} Initiating System Diagnostics and Repair...          ${NC}"
  echo -e "${BLUE}======================================================${NC}"

  if [ -f "${SCRIPT_DIR}/maintenance/fix_antigravity.sh" ]; then
    # Make sure fix_antigravity is executable and run it
    chmod +x "${SCRIPT_DIR}/maintenance/fix_antigravity.sh"
    "${SCRIPT_DIR}/maintenance/fix_antigravity.sh"
  else
    echo -e "${RED}Error: Maintenance script not found at ${SCRIPT_DIR}/maintenance/fix_antigravity.sh${NC}"
    exit 1
  fi
}

# Parse command line options
if [[ $# -eq 0 ]]; then
  perform_install
else
  case "$1" in
    --diagnose)
      perform_diagnose
      ;;
    --repair)
      perform_repair
      ;;
    --help|-h)
      show_help
      ;;
    *)
      echo -e "${RED}Unknown argument: $1${NC}"
      show_help
      exit 1
      ;;
  esac
fi
