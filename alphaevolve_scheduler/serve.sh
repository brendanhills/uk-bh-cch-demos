#!/usr/bin/env bash
# Serve the demos locally.
# Usage: ./serve.sh [PORT] [MODEL]
# Examples:
#   ./serve.sh 9000
#   ./serve.sh 9000 gemini-3.5-flash
#   MODEL=gemini-3.5-pro ./serve.sh 9000
cd "$(dirname "$0")"
PORT="${1:-9000}"
if [ -n "${2:-}" ]; then
  export MODEL="$2"
fi
PYTHONUNBUFFERED=1 uv run server.py "${PORT}" 2>&1 | tee server.log
