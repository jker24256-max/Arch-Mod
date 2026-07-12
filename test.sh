#!/usr/bin/env bash
# ==============================================================================
# JKER OS - Applications Verification Test Suite (test.sh)
# ==============================================================================

set -euo pipefail

echo "[TEST] Running system PyQt6 custom applications verification..."

if command -v python3 &>/dev/null; then
    python3 scripts/test_apps.py
else
    echo "[SKIP] python3 not available to execute verify script."
    exit 0
fi
