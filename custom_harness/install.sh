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
UPDATE_SUBMODULES=false

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
    --update-submodules)
      UPDATE_SUBMODULES=true
      shift
      ;;
    --help|-h)
      echo "Usage: ./install.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --global              Install skills, plugins, hooks, and scripts globally to ~/.gemini/config/ (default)"
      echo "  --local <dir_path>    Install skills, plugins, hooks, and scripts locally to <dir_path>/.agents/"
      echo "  --update-submodules   Pull latest upstream updates for Git submodules (e.g. conductor)"
      echo "  --help, -h            Show this help message"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown argument: $1${NC}"
      exit 1
      ;;
  esac
done

if [ "$UPDATE_SUBMODULES" = true ]; then
  echo -e "${BLUE}Updating Git submodules...${NC}"
  git submodule update --init --recursive --remote
  echo -e "${GREEN}Submodules updated successfully!${NC}"
fi

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

# 4. Install rules (.agents/rules)
if [ -d "${SCRIPT_DIR}/.agents/rules" ]; then
  mkdir -p "${DEST_AGENTS_DIR}/rules"
  echo -e "  Installing rules to ${DEST_AGENTS_DIR}/rules/..."
  for rule in "${SCRIPT_DIR}/.agents/rules"/*; do
    if [ -f "$rule" ]; then
      rule_name=$(basename "$rule")
      echo -e "  Installing rule: ${BLUE}${rule_name}${NC}"
      cp "$rule" "${DEST_AGENTS_DIR}/rules/${rule_name}"
      if [ "$TARGET_MODE" == "global" ]; then
        mkdir -p "${HOME}/.gemini/config/rules"
        ln -sfn "${DEST_AGENTS_DIR}/rules/${rule_name}" "${HOME}/.gemini/config/rules/${rule_name}"
      fi
    fi
  done
fi

# 5. Idempotently configure global AGENTS.md
if [ "$TARGET_MODE" == "global" ]; then
  GLOBAL_CONFIG_DIR="${HOME}/.gemini/config"
  AGENTS_FILE="${GLOBAL_CONFIG_DIR}/AGENTS.md"
  mkdir -p "${GLOBAL_CONFIG_DIR}"
  touch "${AGENTS_FILE}"

  # Clean up legacy Bug Reporting & Management Protocol block if present
  if grep -q "Bug Reporting & Management Protocol" "${AGENTS_FILE}"; then
    echo -e "  Migrating legacy bug rules in ${BLUE}AGENTS.md${NC} to plugin..."
    # Replace full legacy file with clean modern standard
    cat << 'EOF' > "${AGENTS_FILE}"
# Global Rules

- **Direct File Editing & Anti-Scripting Mandate**:
  * **Exclusively Native Tools**: All file reading, searching, creating, editing, and notebook modifications MUST use native tools (`view_file`, `grep_search`, `list_dir`, `replace_file_content`, `write_to_file`, `notebook_edit`).
  * **Strict Prohibitions**: NEVER use shell commands (`sed`, `awk`, `cat <<EOF`, `echo >`) or temporary Python/bash helper scripts to read, parse, or edit files.
  * **Edit Recovery**: If `replace_file_content` fails on character matching, use `view_file` to re-read the exact line chunk and retry native replacement; do NOT fall back to terminal scripts.

- **Bug Workflow Scoping**:
  * When reporting or triaging issues (`/bug`, `/triage_bug`, `/bug_plan`), do not modify source code or attempt immediate fixes; only record metadata or investigate root causes. Execute fixes only when `/fix_bug` is explicitly invoked.

- **checkpoint**: When requested with "checkpoint" (or when you say "checkpoint" or "Finish for the day" or "finish for the day"), update the README.md and Resume.md (compaction summary), track status, check for any untracked project source files/directories in the active workspace (confirming .gitignore is clean), stage and commit all relevant modified and untracked project files with a descriptive message, and push the branch to the remote repository to ensure complete machine portability.
EOF
  else
    if ! grep -q "Direct File Editing & Anti-Scripting Mandate" "${AGENTS_FILE}"; then
      echo -e "  Configuring direct file editing rule in ${BLUE}AGENTS.md${NC}..."
      cat << 'EOF' >> "${AGENTS_FILE}"

- **Direct File Editing & Anti-Scripting Mandate**:
  * **Exclusively Native Tools**: All file reading, searching, creating, editing, and notebook modifications MUST use native tools (`view_file`, `grep_search`, `list_dir`, `replace_file_content`, `write_to_file`, `notebook_edit`).
  * **Strict Prohibitions**: NEVER use shell commands (`sed`, `awk`, `cat <<EOF`, `echo >`) or temporary Python/bash helper scripts to read, parse, or edit files.
  * **Edit Recovery**: If `replace_file_content` fails on character matching, use `view_file` to re-read the exact line chunk and retry native replacement; do NOT fall back to terminal scripts.
EOF
    fi

    if ! grep -q "Bug Workflow Scoping" "${AGENTS_FILE}"; then
      echo -e "  Configuring bug workflow rule in ${BLUE}AGENTS.md${NC}..."
      cat << 'EOF' >> "${AGENTS_FILE}"

- **Bug Workflow Scoping**:
  * When reporting or triaging issues (`/bug`, `/triage_bug`, `/bug_plan`), do not modify source code or attempt immediate fixes; only record metadata or investigate root causes. Execute fixes only when `/fix_bug` is explicitly invoked.
EOF
    fi
  fi
fi

echo -e "${GREEN}Custom Harness installed successfully!${NC}"
