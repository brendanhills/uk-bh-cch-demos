#!/bin/bash
# ==============================================================================
# Package Project Monaro Risk Dashboard Bundle
# Creates a standalone zip containing index.html, assets, data, and docs.
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

OUTPUT_ZIP="dashboard_bundle.zip"

echo "📦 Packaging Project Monaro Risk Dashboard..."
rm -f "$OUTPUT_ZIP"

# Create zip bundle with core standalone files
zip -r "$OUTPUT_ZIP" \
    index.html \
    assets/ \
    data/ \
    src/ \
    HANDOVER_GUIDE.md \
    README.md \
    -x "*.DS_Store" "*__pycache__*" "*.git*"

ZIP_SIZE=$(du -h "$OUTPUT_ZIP" | cut -f1)

echo ""
echo "=================================================================="
echo "✅ Dashboard packaged successfully: $OUTPUT_ZIP ($ZIP_SIZE)"
echo "=================================================================="
echo "🔗 Ways to share with team members:"
echo ""
echo "1️⃣ Direct HTTP Download (from corp network / Cloudtop):"
echo "   http://uk-bh-cloudtop.c.googlers.com:9000/$OUTPUT_ZIP"
echo ""
echo "2️⃣ Download via curl on another machine/Cloudtop:"
echo "   curl -O http://uk-bh-cloudtop.c.googlers.com:9000/$OUTPUT_ZIP"
echo ""
echo "3️⃣ Local file path on this Cloudtop:"
echo "   $SCRIPT_DIR/$OUTPUT_ZIP"
echo "=================================================================="
