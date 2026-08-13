#!/bin/bash

# Exit on error
set -e

# Set SSL Certificate Path for secure Gemini Live API connections
echo "Configuring SSL certificate path..."
export SSL_CERT_FILE=$(uv run python -m certifi)

# Disable mutual TLS (mTLS) to avoid Enterprise Certificate Provider (ECP) failures
export GOOGLE_API_USE_CLIENT_CERTIFICATE=false
export GOOGLE_API_USE_MTLS_ENDPOINT=never

# Navigate to the script's directory (agent_demo) to ensure paths are correct
cd "$(dirname "$0")"

# Navigate to the app subdirectory and run the development server
# NOTE: We force '--loop asyncio' to ensure our IPv4 socket patch in Python's
# standard library is respected, as uvloop bypasses Python's socket.getaddrinfo.
echo "Starting ADK Gemini Live API Toolkit Demo on http://127.0.0.1:8000..."
cd app
uv run --project .. uvicorn main:app --reload --host 127.0.0.1 --port 8000 --loop asyncio
