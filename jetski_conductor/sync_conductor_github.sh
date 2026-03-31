#!/bin/bash

# Configuration
UPSTREAM_URL="https://github.com/gemini-cli-extensions/conductor.git"
TEMP_DIR="__temp_upstream__"
LOG_FILE="diff_report.txt"

# Redirect stdout to both console and log file
exec > >(tee "$LOG_FILE")

echo "Cloning upstream repository (shallow)..."
git clone --depth 1 "$UPSTREAM_URL" "$TEMP_DIR" > /dev/null 2>&1

if [ $? -ne 0 ]; then
  echo "Error: Failed to clone upstream repository."
  exit 1
fi

echo "Analyzing commands..."
# Find all .toml files in local workspace
for local_file in commands/*.toml; do
  filename=$(basename "$local_file")
  
  # Find matching file in upstream
  upstream_file=$(find "$TEMP_DIR" -name "$filename" -print -quit)
  
  if [ -n "$upstream_file" ]; then
    echo "----------------------------------------"
    echo "Comparing local commands/$filename vs upstream $(basename "$upstream_file")"
    diff -u "$local_file" "$upstream_file"
    if [ $? -eq 0 ]; then
      echo "✅ No differences found."
    fi
  else
    echo "----------------------------------------"
    echo "⚠️ Warning: No matching file found in upstream for commands/$filename"
  fi
done

echo "Analyzing policies..."
# Find all .toml files in local policies/
for local_file in policies/*.toml; do
  if [ ! -f "$local_file" ]; then continue; fi
  filename=$(basename "$local_file")
  
  # Find matching file in upstream
  upstream_file=$(find "$TEMP_DIR" -name "$filename" -print -quit)
  
  if [ -n "$upstream_file" ]; then
    echo "----------------------------------------"
    echo "Comparing local policies/$filename vs upstream $(basename "$upstream_file")"
    diff -u "$local_file" "$upstream_file"
    if [ $? -eq 0 ]; then
      echo "✅ No differences found."
    fi
  else
    echo "----------------------------------------"
    echo "⚠️ Warning: No matching file found in upstream for policies/$filename"
  fi
done

echo "----------------------------------------"
echo "Checking for NEW upstream files..."
# Find all .toml files in upstream that are NOT in local commands/ or policies/
find "$TEMP_DIR" -name "*.toml" | while read upstream_file; do
  filename=$(basename "$upstream_file")
  if [ ! -f "commands/$filename" ] && [ ! -f "policies/$filename" ]; then
    echo "🆕 New upstream file found: $filename (at $upstream_file)"
  fi
done

echo "----------------------------------------"
echo "Cleaning up..."
rm -rf "$TEMP_DIR"

echo "----------------------------------------"
echo "Running syntax validation tests..."
pytest tests/test_syntax.py
if [ $? -ne 0 ]; then
  echo "❌ Error: Syntax validation failed!"
  exit 1
fi

echo "Done!"
