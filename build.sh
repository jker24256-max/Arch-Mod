#!/usr/bin/env bash
# ==============================================================================
# JKER OS - Live System Bootable ISO Build Pipeline (build.sh)
# Builds different distribution editions (Lite, Desktop, Dev, Cyber, Enterprise)
# ==============================================================================

set -euo pipefail

# Print distribution headers
echo "=================================================================="
echo "                JKER OS - LINUX DISTRIBUTION BUILD ENGINE          "
echo "=================================================================="

# Parse command line inputs
EDITION="desktop"
IN_CONTAINER=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --edition)
            EDITION="${2,,}"
            shift 2
            ;;
        --in-container)
            IN_CONTAINER=true
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: ./build.sh [--edition lite|desktop|developer|cyber|enterprise]"
            exit 1
            ;;
    esac
done

# Validate edition parameter
VALID_EDITIONS=("lite" "desktop" "developer" "cyber" "enterprise")
if [[ ! " ${VALID_EDITIONS[*]} " =~ " ${EDITION} " ]]; then
    echo "[ERROR] Invalid edition: $EDITION. Valid choices are: ${VALID_EDITIONS[*]}"
    exit 1
fi

echo "[BUILD] Selected system profile: JKER OS (${EDITION^^} EDITION)"

# Host Compatibility Probe
if [ "$IN_CONTAINER" = "false" ] && [ ! -f /etc/arch-release ] && command -v docker &>/dev/null; then
    echo "[COMPAT] Host is not Arch Linux. Rerouting pipeline via Docker container..."
    # Build container call
    docker run --privileged --rm \
        -v "$(pwd)":/workspace \
        -w /workspace \
        archlinux:latest \
        bash -c "pacman -Syu --noconfirm archlinux-keyring && pacman -S --noconfirm archiso rsync parted dosfstools && ./build.sh --edition $EDITION --in-container"
    exit 0
fi

# Run pre-compile tests
echo "[TEST] Verifying application assets integrity..."
if command -v python3 &>/dev/null; then
    python3 scripts/test_apps.py || { echo "[ERROR] Application integrity checks failed."; exit 1; }
fi

# 1. Clean previous build overlay assets
echo "[CLEAN] Purging target overlay directories..."
mkdir -p archiso/airootfs/etc/skel/.config
mkdir -p archiso/airootfs/usr/share/jker-apps
mkdir -p archiso/airootfs/usr/share/sddm/themes/jker-sddm
mkdir -p archiso/airootfs/usr/share/plymouth/themes/jker-spinner
mkdir -p archiso/airootfs/usr/share/grub/themes/jker-grub
mkdir -p archiso/airootfs/usr/share/backgrounds

# 2. Deploy modular configuration files to the live skeleton directory
echo "[SYNC] Deploying user configuration profiles..."
rsync -a --delete configs/hypr/ configs/waybar/ configs/swaync/ configs/kitty/ configs/rofi/ configs/dunst/ archiso/airootfs/etc/skel/.config/

# 3. Deploy application files to shared directories
echo "[SYNC] Syncing custom GUI python applications..."
rsync -a --delete applications/blackvault/ applications/sentryops/ applications/downloadcenter/ applications/controlcenter/ applications/wallpapermanager/ archiso/airootfs/usr/share/jker-apps/

# Copy packages lists so installer can read them
mkdir -p archiso/airootfs/usr/share/jker-apps/packages
rsync -a packages/ archiso/airootfs/usr/share/jker-apps/packages/

# Copy installer code
mkdir -p archiso/airootfs/usr/share/jker-apps/installer
rsync -a installer/ archiso/airootfs/usr/share/jker-apps/installer/

# 4. Deploy branding and desktop themes
echo "[SYNC] Applying tactical bootloader and login manager branding themes..."
rsync -a --delete themes/sddm/jker-sddm/ archiso/airootfs/usr/share/sddm/themes/jker-sddm/
rsync -a --delete themes/plymouth/jker-spinner/ archiso/airootfs/usr/share/plymouth/themes/jker-spinner/
rsync -a --delete themes/grub/jker-grub/ archiso/airootfs/usr/share/grub/themes/jker-grub/
cp branding/backgrounds/camo_red.jpg archiso/airootfs/usr/share/backgrounds/camo_red.jpg

# 5. Compile the dynamically generated packages manifest
echo "[MANIFEST] Assembling Pacman packages manifest list..."
MANIFESTS=("packages/base.list" "packages/installer.list")

if [ "$EDITION" = "lite" ]; then
    MANIFESTS+=("packages/minimal.list")
elif [ "$EDITION" = "desktop" ]; then
    MANIFESTS+=("packages/desktop.list")
elif [ "$EDITION" = "developer" ]; then
    MANIFESTS+=("packages/desktop.list" "packages/developer.list")
elif [ "$EDITION" = "cyber" ]; then
    MANIFESTS+=("packages/desktop.list" "packages/security.list")
elif [ "$EDITION" = "enterprise" ]; then
    MANIFESTS+=("packages/desktop.list" "packages/developer.list" "packages/security.list")
fi

# Join package lists, excluding comments and empty lines
> archiso/packages.x86_64
for manifest in "${MANIFESTS[@]}"; do
    if [ -f "$manifest" ]; then
        grep -v '^#' "$manifest" | grep -v '^$' >> archiso/packages.x86_64 || true
    fi
done

# Ensure package file finishes with single empty line
echo "" >> archiso/packages.x86_64

# 6. Execute archiso compile builder
echo "[COMPILING] Launching mkarchiso generator..."
mkdir -p build
mkdir -p /tmp/archiso-work

# Standard mkarchiso command execution
mkarchiso -v -w /tmp/archiso-work -o build archiso

echo "[SUCCESS] UEFI Bootable ISO compiled successfully."
