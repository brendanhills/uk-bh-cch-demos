#!/bin/bash
# ==============================================================================
# Package Project Monaro Risk Dashboard Minimal Bundle (~500 KB)
# Creates a lightweight zip containing only the standalone UI and active audio.
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

OUTPUT_ZIP="dashboard_bundle.zip"

echo "📦 Packaging Project Monaro Risk Dashboard (Minimal Bundle)..."
rm -f "$OUTPUT_ZIP"

# Include essential standalone files: index.html, all week MP3 podcasts, and docs
zip -9 "$OUTPUT_ZIP" \
    index.html \
    assets/*.mp3 \
    README.md \
    docs/HANDOVER_GUIDE.md

ZIP_SIZE=$(du -h "$OUTPUT_ZIP" | cut -f1)

echo ""
echo "=================================================================="
echo "✅ Minimal Dashboard Packaged: $OUTPUT_ZIP ($ZIP_SIZE)"
echo "=================================================================="
echo "🔗 Sharing options for allowlisted team members:"
echo ""
echo "1️⃣ Direct HTTP Download (from Cloudtop):"
echo "   http://uk-bh-cloudtop.c.googlers.com:9000/$OUTPUT_ZIP"
echo ""
echo "2️⃣ Terminal download via curl:"
echo "   curl -O http://uk-bh-cloudtop.c.googlers.com:9000/$OUTPUT_ZIP"
echo ""
echo "3️⃣ Copy/Attach to Team Google Drive Shared Folder:"
echo "   $SCRIPT_DIR/$OUTPUT_ZIP"
echo "=================================================================="
