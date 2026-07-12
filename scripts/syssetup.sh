#!/usr/bin/env bash
# ==============================================================================
# JKER OS Live Setup and User Provisioner
# Sets up live users, file privileges, services, and sddm auto-login properties.
# ==============================================================================

set -euo pipefail

echo "=== INITIATING JKER LIVE SESSION PROVISIONER ==="

# 1. Verify / Create User 'jker'
if ! id "jker" &>/dev/null; then
    echo "[USER] Creating live distribution user: jker"
    useradd -m -g users -G wheel,audio,video,optical,storage,docker,network -s /bin/zsh jker
    # Set default password to 'jker'
    echo "jker:jker" | chpasswd
else
    echo "[USER] User jker already exists."
fi

# 2. Configure passwordless sudo for the live environment
echo "[SUDO] Configuring wheel group passwordless authorization..."
mkdir -p /etc/sudoers.d
echo "%wheel ALL=(ALL:ALL) NOPASSWD: ALL" > /etc/sudoers.d/10-wheel-nopasswd
chmod 440 /etc/sudoers.d/10-wheel-nopasswd

# 3. Synchronize Skeleton Dotfiles to 'jker' Home
echo "[HOME] Syncing dotfiles and configuration directories..."
rsync -a --no-owner --no-group /etc/skel/ /home/jker/
chown -R jker:users /home/jker/

# 4. Enable Systemd Hardening and Boot Services
echo "[SERVICES] Enabling core system services..."
SERVICES=(
    "NetworkManager.service"
    "sddm.service"
    "bluetooth.service"
    "ufw.service"
    "fail2ban.service"
    "docker.service"
)

for srv in "${SERVICES[@]}"; do
    if systemctl list-unit-files | grep -q "$srv"; then
        systemctl enable "$srv"
        echo "[SERVICES] Enabled service: $srv"
    else
        echo "[SERVICES] Service not found (skipping): $srv"
    fi
done

# 5. Lock USB controller via USBGuard
echo "[SECURITY] Configuring USBGuard initial device policy..."
if command -v usbguard &>/dev/null; then
    usbguard generate-policy > /etc/usbguard/usbguard-daemon.conf || true
    systemctl enable usbguard.service || true
fi

echo "=== LIVE PROVISIONER COMPLETED ==="
