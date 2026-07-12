#!/usr/bin/env bash
# ==============================================================================
# JKER OS - System Installer Script (CLI)
# Performs disk partitioning, formatting, bootstrap, and config deployment.
# ==============================================================================

set -euo pipefail

echo "=== JKER OS SYSTEM INSTALLER INITIATED ==="

# 1. Select disk
echo "Available storage devices:"
lsblk -d -n -o NAME,SIZE,MODEL
echo ""
read -rp "Enter target disk name (e.g. sda, nvme0n1): " TARGET_DISK

DISK_PATH="/dev/$TARGET_DISK"
if [ ! -b "$DISK_PATH" ]; then
    echo "[ERROR] Invalid block device path: $DISK_PATH"
    exit 1
fi

# 2. Collect configurations
read -rp "Enter system hostname [jker-host]: " HOSTNAME
HOSTNAME=${HOSTNAME:-jker-host}

read -rp "Enter username [jker-user]: " USERNAME
USERNAME=${USERNAME:-jker-user}

read -rsp "Enter password for $USERNAME: " PASSWORD
echo ""
read -rsp "Confirm password: " PASSWORD_CONFIRM
echo ""

if [ "$PASSWORD" != "$PASSWORD_CONFIRM" ]; then
    echo "[ERROR] Passwords do not match!"
    exit 1
fi

# 3. Partitioning (GPT, 512M EFI, rest Root)
echo "[DISK] Partitioning target device $DISK_PATH..."
parted -s "$DISK_PATH" mklabel gpt
parted -s "$DISK_PATH" mkpart ESP fat32 1MiB 513MiB
parted -s "$DISK_PATH" set 1 esp on
parted -s "$DISK_PATH" mkpart primary ext4 513MiB 100%

# Determine partition names (e.g. sda1 vs nvme0n1p1)
if [[ "$TARGET_DISK" =~ nvme ]]; then
    BOOT_PART="${DISK_PATH}p1"
    ROOT_PART="${DISK_PATH}p2"
else
    BOOT_PART="${DISK_PATH}1"
    ROOT_PART="${DISK_PATH}2"
fi

# 4. Format partitions
echo "[DISK] Formatting partitions..."
mkfs.vfat -F 32 "$BOOT_PART"
mkfs.ext4 -F "$ROOT_PART"

# 5. Mount partitions
echo "[DISK] Mounting partitions..."
mount "$ROOT_PART" /mnt
mkdir -p /mnt/boot
mount "$BOOT_PART" /mnt/boot

# 6. Bootstrap core packages
echo "[PACSTRAP] Deploying Arch Linux packages..."
pacstrap /mnt base base-devel linux linux-firmware grub efibootmgr networkmanager network-manager-applet python python-pyqt6 python-cryptography neovim zsh git kitty waybar hyprland sddm ufw fail2ban usbguard docker

# 7. Generate Fstab
echo "[FSTAB] Writing file system table..."
genfstab -U /mnt >> /mnt/etc/fstab

# 8. Configure System (Chroot Phase)
echo "[CHROOT] Configuring network, localization, and user privileges..."
arch-chroot /mnt /usr/bin/bash <<EOF
set -euo pipefail

# Timezone and Locales
ln -sf /usr/share/zoneinfo/UTC /etc/localtime
hwclock --systohc
echo "en_US.UTF-8 UTF-8" > /etc/locale.gen
locale-gen
echo "LANG=en_US.UTF-8" > /etc/locale.conf

# Hostname
echo "$HOSTNAME" > /etc/hostname

# Users & Passwords
echo "root:root" | chpasswd
useradd -m -g users -G wheel,audio,video,optical,storage,docker -s /bin/zsh "$USERNAME"
echo "$USERNAME:$PASSWORD" | chpasswd

# Sudoers Configuration
echo "%wheel ALL=(ALL:ALL) ALL" > /etc/sudoers.d/10-wheel

# Install Bootloader
grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=JKER_OS --recheck
grub-mkconfig -o /boot/grub/grub.cfg

# Enable System Services
systemctl enable NetworkManager.service
systemctl enable sddm.service
systemctl enable ufw.service
systemctl enable fail2ban.service
systemctl enable usbguard.service
systemctl enable docker.service
EOF

# 9. Sync JKER OS Specific Configurations & Binaries
echo "[CONFIGS] Deploying JKER custom configs & custom applications..."
# Sync Applications
mkdir -p /mnt/usr/share/jker-apps
rsync -a /usr/share/jker-apps/ /mnt/usr/share/jker-apps/
rsync -a /usr/bin/blackvault /usr/bin/sentryops /usr/bin/downloadcenter /usr/bin/controlcenter /mnt/usr/bin/
rsync -a /usr/bin/jker-hwdetect /usr/bin/jker-optimize /usr/bin/jker-syssetup /mnt/usr/bin/

# Sync Skel configs for the user
rsync -a /etc/skel/ /mnt/home/"$USERNAME"/
chown -R "$USERNAME":users /mnt/home/"$USERNAME"/

# Unmount
echo "[CLEANUP] Unmounting target volumes..."
umount -R /mnt

echo "=== JKER OS INSTALLED SUCCESSFULLY! REBOOT TO LAUNCH ==="
EOF
