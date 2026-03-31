#!/bin/bash

# Setup script for Conductor workflows in JetSki

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REL_PATH="${SCRIPT_DIR/#$HOME/\~}"
WORKFLOWS_DIR="${SCRIPT_DIR}/workflows"
GLOBAL_WORKFLOWS_DIR="${HOME}/.gemini/jetski/global_workflows"

echo "Installing Conductor workflows via symlinks..."

if [ ! -d "${WORKFLOWS_DIR}" ]; then
  echo "Error: Workflows directory ${WORKFLOWS_DIR} not found!"
  exit 1
fi

mkdir -p "${GLOBAL_WORKFLOWS_DIR}"

for f in "${WORKFLOWS_DIR}"/conductor-*.md; do
  if [ -f "$f" ]; then
    filename=$(basename "$f")
    echo "Installing ${filename} with absolute paths to ${GLOBAL_WORKFLOWS_DIR}"
    rm -f "${GLOBAL_WORKFLOWS_DIR}/${filename}"
    sed "s|commands/|${REL_PATH}/commands/|g" "$f" > "${GLOBAL_WORKFLOWS_DIR}/${filename}"
  fi
done

echo "Workflows installed successfully!"
