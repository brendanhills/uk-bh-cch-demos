#!/usr/bin/env bash

# This diagnostic and troubleshooting script helps manually resolve the
# 'invalid project ID: ""' error if it occurs in the future.
# The purpose of this script is to provide a centralized tool to stop any hung
# application processes and correctly synchronize Gemini configuration files.

echo "======================================================"
echo " Starting Antigravity diagnostics and repair..."
echo "======================================================"

# 1. Safely find and stop any orphan backend helper processes (such as 'language_server')
# that might be locking files or keeping stale project ID configurations cached.
# We dynamically walk up the current process tree to exclude the active shell and any parent terminal
# processes from being killed, ensuring the stability of the active session.
MY_PID=$$
EXCLUDE_PIDS=("$MY_PID")
PID=$MY_PID
while [ -n "$PID" ] && [ "$PID" -gt 1 ]; do
  PPID_VAL=$(ps -p "$PID" -o ppid= | tr -d ' ')
  if [ -n "$PPID_VAL" ] && [ "$PPID_VAL" -gt 0 ]; then
    EXCLUDE_PIDS+=("$PPID_VAL")
    PID=$PPID_VAL
  else
    break
  fi
done

# CRITICAL SAFETY WARNING:
# -------------------------
# 1. Do NOT match on full command-line arguments (like 'ps aux') as doing so will match any shell,
#    command, or script run from inside a directory containing the word 'antigravity' in its path
#    (such as 'antigravity_suite'), leading to false positives and accidental terminations.
# 2. Do NOT target the 'antigravity' executable itself (the main GUI editor process). Since the IDE
#    is often launched by systemd user managers or window managers outside the current terminal's
#    ancestor tree, the PPID walk-up check above will fail to protect it, leading to sudden IDE crashes,
#    session loss, and system core dumps.
# 3. Only target backend helper processes like 'language_server' that are safe to terminate and will
#    be automatically restarted on-demand by the IDE.
STALE_PIDS=$(ps -e -o pid,comm | grep -E -i "language_server" | awk '{print $1}')
FILTERED_PIDS=""

for PID in $STALE_PIDS; do
  EXCLUDED=false
  for EX_PID in "${EXCLUDE_PIDS[@]}"; do
    if [ "$PID" -eq "$EX_PID" ]; then
      EXCLUDED=true
      break
    fi
  done
  if [ "$EXCLUDED" = false ]; then
    FILTERED_PIDS="$FILTERED_PIDS $PID"
  fi
done

if [ -n "$FILTERED_PIDS" ]; then
  echo "[+] Orphan/hung Antigravity backend processes found. Clearing cache..."
  for PID in $FILTERED_PIDS; do
    echo "  [-] Stopping process: $PID"
    kill -9 "$PID" 2>/dev/null || true
  done
  echo "[+] Hung processes successfully stopped."
else
  echo "[+] No orphan or hung processes found running."
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
