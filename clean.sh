#!/usr/bin/env bash
# ==============================================================================
# JKER OS - Build Cache & Workspace Cleaner (clean.sh)
# ==============================================================================

set -euo pipefail

echo "[CLEAN] Wiping build outputs and cache directories..."

# Remove local build caches
rm -rf build/
rm -rf dist/
rm -rf /tmp/archiso-work/

# Clear live overlay directories
rm -rf archiso/airootfs/etc/skel/.config/*
rm -rf archiso/airootfs/usr/share/jker-apps/*
rm -rf archiso/airootfs/usr/share/sddm/themes/jker-sddm/*
rm -rf archiso/airootfs/usr/share/plymouth/themes/jker-spinner/*
rm -rf archiso/airootfs/usr/share/grub/themes/jker-grub/*
rm -f archiso/airootfs/usr/share/backgrounds/camo_red.jpg
rm -f archiso/packages.x86_64

echo "[CLEAN] All workspaces cleared."
