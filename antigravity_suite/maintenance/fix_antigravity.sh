#!/usr/bin/env bash

# This diagnostic and troubleshooting script helps manually resolve the
# 'invalid project ID: ""' error if it occurs in the future.
# The purpose of this script is to provide a centralized tool to stop any hung
# application processes and correctly synchronize Gemini configuration files.

echo "======================================================"
echo " Starting Antigravity diagnostics and repair..."
echo "======================================================"

# 1. Safely find and stop any orphan processes from the application (such as 'language_server' or 'antigravity')
# that might be locking files or keeping stale project ID configurations cached.
# We exclude the current bash process ($$) to ensure the stability of the active terminal session.
CURRENT_PID=$$
STALE_PIDS=$(ps aux | grep -E -i "antigravity|language_server" | grep -v grep | grep -v "$CURRENT_PID" | awk '{print $2}')

if [ -n "$STALE_PIDS" ]; then
  echo "[+] Active Antigravity processes found. Clearing cache..."
  for PID in $STALE_PIDS; do
    kill -9 "$PID" 2>/dev/null
  done
  echo "[+] Hung processes successfully stopped."
else
  echo "[+] No hung processes found running."
fi

# 2. Get the directory where the script resides to dynamically locate the Python updater.
# This ensures the script functions correctly regardless of where it is run.
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

if [ -f "${SCRIPT_DIR}/update_projects.py" ]; then
  echo "[+] Synchronizing project configurations with gcloud..."
  python3 "${SCRIPT_DIR}/update_projects.py"
else
  echo "[-] Error: Update script not found at ${SCRIPT_DIR}/update_projects.py"
fi

echo "======================================================"
echo " Repair completed! You can now open Antigravity."
echo "======================================================"
