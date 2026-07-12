#!/usr/bin/env bash
# ==============================================================================
# JKER OS - Release Packager and Hash Calculator (release.sh)
# ==============================================================================

set -euo pipefail

echo "[RELEASE] Initiating distribution release packaging..."

# Create distribution directory
mkdir -p dist

# Verify compiled ISO exists in build/
if [ ! -d build ] || [ -z "$(ls build/jker-os*.iso 2>/dev/null)" ]; then
    echo "[ERROR] Compiled ISO not found in build/ directory. Please run build.sh first."
    exit 1
fi

ISO_FILE=$(ls build/jker-os*.iso | head -n 1)
ISO_NAME=$(basename "$ISO_FILE")

echo "[RELEASE] Copying ISO to distribution folder..."
cp "$ISO_FILE" "dist/$ISO_NAME"

echo "[RELEASE] Computing SHA256 hash validation..."
sha256sum "dist/$ISO_NAME" > "dist/$ISO_NAME.sha256"

echo "=================================================================="
echo "                JKER OS RELEASE PACKAGED SUCCESSFULLY              "
echo "=================================================================="
echo "ISO FILE: dist/$ISO_NAME"
echo "SHA256  : $(cat "dist/$ISO_NAME.sha256")"
echo "=================================================================="
