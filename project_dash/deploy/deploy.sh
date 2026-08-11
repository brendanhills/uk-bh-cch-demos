#!/bin/bash
# Convenience wrapper for C4A Deployment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "${SCRIPT_DIR}/deploy_c4a.py" "$@"
