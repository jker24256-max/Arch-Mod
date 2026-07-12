# JKER OS // Recovery & Troubleshooting Guide

This guide details the diagnostic steps, boot parameters, emergency shell operations, and rescue configurations to restore JKER OS installations.

---

## 1. Recovery Boot Options

JKER OS includes dedicated boot loader recovery entries in both the UEFI boot image and the target system GRUB configuration:

### A. JKER OS Safe Graphics Mode
If your screen flashes black, shows visual artifacts, or halts on loading graphical servers, boot into the safe mode option from the bootloader menu:
*   **Kernel Flags Added**: `nomodeset`
*   **Action**: Disables kernel-mode setting (KMS) drivers, falling back to basic VESA framebuffers. Use this to configure graphics driver parameters or install proprietary packages.

### B. JKER OS Emergency Shell (Console Only)
If services crash or disks fail to mount, boot into the rescue shell:
*   **Kernel Flags Added**: `systemd.unit=multi-user.target` or `single`
*   **Action**: Skips SDDM graphical display services and halts system initialization before loading user environments. You are dropped directly into a root console terminal.

---

## 2. Hard Drive Diagnostic and Repair

If the system crashes during write operations, run manual filesystem checks:

1.  Boot the JKER OS Live ISO.
2.  Open a terminal and identify partition nodes using `lsblk`:
    ```bash
    lsblk -f
    ```
3.  Perform an `fsck` repair sweep on the target partition (ensure it is **unmounted**):
    ```bash
    # Run interactive filesystem check
    sudo fsck.ext4 -v -f /dev/sdX2
    ```
    *Replace `/dev/sdX2` with your root partition path.*

---

## 3. Chrooting to Restore the Bootloader

If the UEFI boot manager is corrupted or the GRUB configuration is missing (e.g. after dual-booting changes), restore it from a live session:

1.  Boot the JKER OS Live ISO.
2.  Mount your target root partition and boot partition to `/mnt`:
    ```bash
    # Mount Root
    sudo mount /dev/sdX2 /mnt
    # Mount EFI System Partition
    sudo mount /dev/sdX1 /mnt/boot
    ```
3.  Enter the system chroot jail environment:
    ```bash
    sudo arch-chroot /mnt
    ```
4.  Re-install the GRUB UEFI bootloader files and regenerate config hooks:
    ```bash
    # Deploy grub binaries
    grub-install --target=x86_64-efi --efi-directory=/boot --bootloader-id=JKER_OS --recheck
    # Generate GRUB configuration
    grub-mkconfig -o /boot/grub/grub.cfg
    ```
5.  Exit chroot and unmount nodes:
    ```bash
    exit
    sudo umount -R /mnt
    sudo reboot
    ```

---

## 4. Graphics Driver Troubleshooting

JKER OS automatically queries components during bootstrap via `/usr/bin/jker-hwdetect`. If you alter graphics cards:

### Blacklisting Nouveau (For NVIDIA users)
If the open-source Nouveau driver conflicts with proprietary NVIDIA modules, ensure Nouveau is blacklisted:
```bash
# Check contents of /etc/modprobe.d/nouveau.conf
blacklist nouveau
options nouveau modeset=0
```

### Modesetting Parameter
If Wayland compositor (Hyprland) doesn't start, ensure modesetting is enabled in the kernel boot options:
```bash
# Append to GRUB_CMDLINE_LINUX_DEFAULT in /etc/default/grub:
nvidia-drm.modeset=1
```
Regenerate grub config: `sudo grub-mkconfig -o /boot/grub/grub.cfg`.

---

## 5. Rollbacks and Snapshot Recovery

If you run Btrfs filesystems or Timeshift system backup daemons:
*   Configure backups regularly using Timeshift to take daily system root snapshots.
*   To restore to a functional snapshot, launch **Timeshift GUI** from the JKER live desktop environment, select the restore target snapshot, and reboot.
