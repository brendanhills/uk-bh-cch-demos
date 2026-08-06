#!/bin/bash

# ADK Agent Virtual Environment Setup Script

set -e  # Exit on any error

# --- Function for error handling ---
handle_error() {
  echo "Error: $1"
  exit 1
}

# --- Part 1: Get your Google AI Studio API key ---
echo "--- Google AI Studio API Key ---"
echo "Get a free key at https://aistudio.google.com/app/apikey (it starts with 'AIza...')."

read -s -p "Please paste your Google AI Studio API key: " user_api_key
echo ""

if [[ -z "$user_api_key" ]]; then
  handle_error "No API key was entered."
fi
echo "API key received."

echo "🚀 Setting up ADK Agent virtual environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .adk_env

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .adk_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# --- Create .env file (Google AI Studio API key path) ---
echo "📝 Creating .env file..."
cat > .env << EOL
# Environment variables for ADK Agent, created by setup_venv.sh
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=${user_api_key}
EOL

echo "✅ Setup complete! A '.env' file has been created with your Google AI Studio API key."
echo ""
echo "To activate the virtual environment, run:"
echo "   source .adk_env/bin/activate"
echo ""
echo "Your agent will automatically load the settings from the .env file."
echo "To deactivate the virtual environment, run:"
echo "   deactivate"
