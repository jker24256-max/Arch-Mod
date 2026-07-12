#!/usr/bin/env bash
# ==============================================================================
# JKER OS - Advanced Backend Installation Engine (install_helper.sh)
# Executes low-level partitioning, installation, and environment sync.
# ==============================================================================

set -euo pipefail

echo "=== JKER OS SYSTEM INSTALLER BACKEND INITIATED ==="

# Inputs from environment variables
TARGET_DISK="${TARGET_DISK:-}"
INSTALL_MODE="${INSTALL_MODE:-offline}" # offline or online
HOSTNAME="${HOSTNAME:-jker-host}"
USERNAME="${USERNAME:-jker-user}"
PASSWORD="${PASSWORD:-jker}"
TIMEZONE="${TIMEZONE:-UTC}"
LOCALE="${LOCALE:-en_US.UTF-8}"
KEYMAP="${KEYMAP:-us}"
PARTITION_MODE="${PARTITION_MODE:-auto}" # auto or manual
EFI_PART="${EFI_PART:-}"
ROOT_PART="${ROOT_PART:-}"
EDITION="${EDITION:-desktop}"

if [ -z "$TARGET_DISK" ] && [ "$PARTITION_MODE" = "auto" ]; then
    echo "[ERROR] Target disk must be specified for auto partitioning."
    exit 1
fi

DISK_PATH="/dev/$TARGET_DISK"

# 1. Partitioning Phase
if [ "$PARTITION_MODE" = "auto" ]; then
    echo "[DISK] Auto partitioning target device $DISK_PATH..."
    # Create GPT label and partitions
    parted -s "$DISK_PATH" mklabel gpt
    parted -s "$DISK_PATH" mkpart ESP fat32 1MiB 513MiB
    parted -s "$DISK_PATH" set 1 esp on
    parted -s "$DISK_PATH" mkpart primary ext4 513MiB 100%

    # Determine partition paths
    if [[ "$TARGET_DISK" =~ nvme || "$TARGET_DISK" =~ mmcblk || "$TARGET_DISK" =~ loop ]]; then
        BOOT_PART="${DISK_PATH}p1"
        ROOT_PART="${DISK_PATH}p2"
    else
        BOOT_PART="${DISK_PATH}1"
        ROOT_PART="${DISK_PATH}2"
    fi
else
    echo "[DISK] Manual partitioning active. Using boot: $EFI_PART, root: $ROOT_PART"
    BOOT_PART="$EFI_PART"
    ROOT_PART="$ROOT_PART"
fi

# 2. Formatting Phase
echo "[DISK] Formatting partitions..."
mkfs.vfat -F 32 "$BOOT_PART"
mkfs.ext4 -F "$ROOT_PART"

# 3. Mount Target Filesystem
echo "[DISK] Mounting target filesystem..."
mount "$ROOT_PART" /mnt
mkdir -p /mnt/boot
mount "$BOOT_PART" /mnt/boot

# 4. Bootstrap Target Filesystem
if [ "$INSTALL_MODE" = "offline" ]; then
    echo "[OFFLINE] Copying live environment image (SquashFS clone) to target partition..."
    # Sync live filesystem, excluding virtual directories
    rsync -aAX --info=progress2 \
        --exclude={"/dev/*","/proc/*","/sys/*","/tmp/*","/run/*","/mnt/*","/media/*","/lost+found","/var/lib/pacman/sync/*"} \
        / /mnt/
    
    # Recreate virtual directory paths
    mkdir -p /mnt/{dev,proc,sys,tmp,run,mnt,media}
    chmod 1777 /mnt/tmp
else
    echo "[ONLINE] Syncing package manifests and bootstrapping via pacstrap..."
    # Build package list dynamically from manifestations
    PKG_LIST=()
    
    # Read manifests
    MANIFESTS=("/usr/share/jker-apps/packages/base.list" "/usr/share/jker-apps/packages/desktop.list" "/usr/share/jker-apps/packages/installer.list")
    
    # Edition-specific lists
    if [ "$EDITION" = "cyber" ] || [ "$EDITION" = "enterprise" ]; then
        MANIFESTS+=("/usr/share/jker-apps/packages/security.list")
    fi
    if [ "$EDITION" = "developer" ] || [ "$EDITION" = "enterprise" ]; then
        MANIFESTS+=("/usr/share/jker-apps/packages/developer.list")
    fi
    
    for manifest in "${MANIFESTS[@]}"; do
        if [ -f "$manifest" ]; then
            while IFS= read -r pkg || [ -n "$pkg" ]; do
                # Ignore comments and empty lines
                if [[ ! "$pkg" =~ ^# ]] && [ -n "$pkg" ]; then
                    PKG_LIST+=("$pkg")
                fi
            done < "$manifest"
        fi
    done
    
    echo "[PACSTRAP] Installing packages: ${PKG_LIST[*]}"
    pacstrap -K /mnt "${PKG_LIST[@]}"
fi

# 5. Generate Fstab
echo "[FSTAB] Generating filesystem table..."
genfstab -U /mnt >> /mnt/etc/fstab

# 6. Target Chroot Configurations
echo "[CHROOT] Initiating configuration phase inside jail..."
cat <<EOF > /mnt/tmp/chroot_setup.sh
#!/bin/bash
set -euo pipefail

# Timezone & Hardware Clock
ln -sf /usr/share/zoneinfo/$TIMEZONE /etc/localtime
hwclock --systohc

# Locale & Keyboard
echo "$LOCALE UTF-8" > /etc/locale.gen
locale-gen
echo "LANG=$LOCALE" > /etc/locale.conf
echo "KEYMAP=$KEYMAP" > /etc/vconsole.conf

# Hostname
echo "$HOSTNAME" > /etc/hostname

# Root credentials
echo "root:root" | chpasswd

# Create User
if ! id "$USERNAME" &>/dev/null; then
    useradd -m -g users -G wheel,audio,video,optical,storage,docker,network -s /bin/zsh "$USERNAME"
fi
echo "$USERNAME:$PASSWORD" | chpasswd

# Sudoers privilege assignment
mkdir -p /etc/sudoers.d
echo "%wheel ALL=(ALL:ALL) ALL" > /etc/sudoers.d/10-wheel
chmod 440 /etc/sudoers.d/10-wheel

# Configure GRUB UEFI Bootloader
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=JKER_OS --recheck
grub-mkconfig -o /boot/grub/grub.cfg

# Enable Crucial Daemons
SERVICES=(
    "NetworkManager.service"
    "sddm.service"
    "bluetooth.service"
    "ufw.service"
    "fail2ban.service"
    "docker.service"
)
for srv in "\${SERVICES[@]}"; do
    if systemctl list-unit-files | grep -q "\$srv"; then
        systemctl enable "\$srv"
    fi
done

# Enable optimization timer if SSD
systemctl enable fstrim.timer || true

EOF

chmod +x /mnt/tmp/chroot_setup.sh
arch-chroot /mnt /tmp/chroot_setup.sh
rm -f /mnt/tmp/chroot_setup.sh

# 7. Final Configuration Sync (Ensuring themes and apps are fully deployed)
echo "[CONFIGS] Syncing latest desktop themes, custom apps, and configurations..."
# Sync Applications
mkdir -p /mnt/usr/share/jker-apps
rsync -a /usr/share/jker-apps/ /mnt/usr/share/jker-apps/

# Copy wrappers
rsync -a /usr/bin/blackvault /usr/bin/sentryops /usr/bin/downloadcenter /usr/bin/controlcenter /usr/bin/wallpapermanager /usr/bin/jker-install /mnt/usr/bin/
rsync -a /usr/bin/jker-hwdetect /usr/bin/jker-optimize /usr/bin/jker-syssetup /mnt/usr/bin/

# Copy SDDM theme
mkdir -p /mnt/usr/share/sddm/themes
rsync -a /usr/share/sddm/themes/ /mnt/usr/share/sddm/themes/

# Copy Grub theme
mkdir -p /mnt/boot/grub/themes
rsync -a /usr/share/grub/themes/ /mnt/boot/grub/themes/ || true

# Setup skeleton dotfiles in new user home folder
mkdir -p /mnt/home/"$USERNAME"
rsync -a /etc/skel/ /mnt/home/"$USERNAME"/
chown -R "$USERNAME":users /mnt/home/"$USERNAME"/

# 8. Unmount & Cleanup
echo "[DISK] Dismounting volume nodes..."
umount -R /mnt

echo "=== JKER OS SYSTEM INSTALLED SUCCESSFULLY ==="
