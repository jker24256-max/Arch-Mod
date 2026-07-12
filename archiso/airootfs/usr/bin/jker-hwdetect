#!/usr/bin/env bash
# ==============================================================================
# JKER OS Hardware Probing and Modesetting Auto-Detection Script
# Detects CPU (Intel/AMD) and GPU (Intel/AMD/Nvidia) to output system configs.
# ==============================================================================

set -euo pipefail

echo "=== JKER OS HARDWARE ANALYSIS START ==="

# 1. CPU Type Identification
cpu_vendor=$(grep -m1 'vendor_id' /proc/cpuinfo | awk '{print $3}')
case "$cpu_vendor" in
    GenuineIntel)
        echo "[CPU] Intel processor detected. Recommending 'intel-ucode'."
        CPU_UCODE="intel-ucode"
        ;;
    AuthenticAMD)
        echo "[CPU] AMD processor detected. Recommending 'amd-ucode'."
        CPU_UCODE="amd-ucode"
        ;;
    *)
        echo "[CPU] Unknown CPU Vendor ($cpu_vendor). Defaulting to standard microcode."
        CPU_UCODE=""
        ;;
esac

# 2. GPU / Graphics Controller Probe
gpu_info=$(lspci | grep -i -E 'vga|3d' || true)
echo "[GPU] PCI Probing details: $gpu_info"

DRIVERS=()
KERNEL_PARAMS=""

if echo "$gpu_info" | grep -iq "nvidia"; then
    echo "[GPU] Nvidia graphics adapter detected."
    DRIVERS+=("nvidia" "nvidia-utils" "nvidia-settings" "lib32-nvidia-utils")
    KERNEL_PARAMS="nvidia-drm.modeset=1"
elif echo "$gpu_info" | grep -iq "amd"; then
    echo "[GPU] AMD GPU detected (Radeon/amdgpu)."
    DRIVERS+=("mesa" "xf86-video-amdgpu" "vulkan-radeon" "lib32-vulkan-radeon")
elif echo "$gpu_info" | grep -iq "intel"; then
    echo "[GPU] Intel Integrated GPU detected."
    DRIVERS+=("mesa" "vulkan-intel" "lib32-vulkan-intel")
else
    echo "[GPU] Generic/Virtual Box/QEMU driver suite applied."
    DRIVERS+=("xf86-video-vesa" "mesa")
fi

echo "=== RECOMMENDED PACKAGES ==="
echo "Microcode: $CPU_UCODE"
echo "Graphics Drivers: ${DRIVERS[*]}"
echo "Kernel Parameters: $KERNEL_PARAMS"

# Output configuration files for installation scripts to parse
mkdir -p /tmp/jker_hw
echo "$CPU_UCODE" > /tmp/jker_hw/ucode
echo "${DRIVERS[*]}" > /tmp/jker_hw/drivers
echo "$KERNEL_PARAMS" > /tmp/jker_hw/kernel_params

echo "=== HARDWARE ANALYSIS COMPLETE ==="
