#!/usr/bin/env bash

# Central installer script for Conductor plugin and workflows in Antigravity

set -e

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
LOCAL_PLUGIN_DIR="${SCRIPT_DIR}/conductor"
GLOBAL_PLUGINS_DIR="${HOME}/.gemini/config/plugins"
CLI_PLUGINS_DIR="${HOME}/.gemini/antigravity-cli/plugins"

# Colors for terminal output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE} Installing Conductor Plugin and Workflows globally...${NC}"
echo -e "${BLUE}======================================================${NC}"

# 1. Prerequisite Check: Check if conductor git submodule is initialized
if [ ! -f "${LOCAL_PLUGIN_DIR}/gemini-extension.json" ]; then
  echo -e "${RED}Error: Conductor plugin source not found in '${LOCAL_PLUGIN_DIR}'.${NC}"
  echo -e "${YELLOW}Please initialize the git submodule first:${NC}"
  echo -e "  git submodule update --init --recursive"
  exit 1
fi


# 2. Provision and Synchronize global plugins directory (~/.gemini/config/plugins)
echo -e "\n${BLUE}[+] Sincronizando en la configuración global de Gemini...${NC}"
mkdir -p "${GLOBAL_PLUGINS_DIR}"
echo -e "  Target: ${BLUE}${GLOBAL_PLUGINS_DIR}/conductor${NC}"
rm -rf "${GLOBAL_PLUGINS_DIR}/conductor"
cp -r "${LOCAL_PLUGIN_DIR}" "${GLOBAL_PLUGINS_DIR}/conductor"
echo -e "  ${GREEN}Successfully synchronized config plugin!${NC}"

# 3. Provision and Synchronize CLI plugins directory (~/.gemini/antigravity-cli/plugins)
echo -e "\n${BLUE}[+] Sincronizando en la configuración de antigravity-cli...${NC}"
mkdir -p "${CLI_PLUGINS_DIR}"
echo -e "  Target: ${BLUE}${CLI_PLUGINS_DIR}/conductor${NC}"
rm -rf "${CLI_PLUGINS_DIR}/conductor"
cp -r "${LOCAL_PLUGIN_DIR}" "${CLI_PLUGINS_DIR}/conductor"
echo -e "  ${GREEN}Successfully synchronized CLI plugin!${NC}"

# 4. Sincronizar workflows globales llamando a setup_conductor.sh
echo -e "\n${BLUE}[+] Sincronizando flujos de trabajo (workflows) globales...${NC}"
if [ -f "${SCRIPT_DIR}/setup_conductor.sh" ]; then
  bash "${SCRIPT_DIR}/setup_conductor.sh"
else
  echo -e "${RED}Error: setup_conductor.sh not found in ${SCRIPT_DIR}!${NC}"
  exit 1
fi

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN} Installation completed successfully!${NC}"
echo -e " Conductor is now consistent and fully active in:"
echo -e "   - agy"
echo -e "   - antigravity-cli"
echo -e "   - antigravity-x64 / antigravity"
echo -e "${GREEN}======================================================${NC}"
