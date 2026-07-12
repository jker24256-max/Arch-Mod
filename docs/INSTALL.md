# JKER OS // Installation Guide

This document outlines the requirements and processes to install JKER OS onto physical or virtualized hardware.

---

## 1. System Requirements

* **Processor**: x86_64 compatible CPU (Intel Core i3/AMD Ryzen 3 or higher recommended).
* **Memory**: 4 GB RAM minimum (8 GB recommended for development and security testing).
* **Storage**: 20 GB of free space (SSD strongly recommended).
* **Boot Mode**: UEFI (Legacy BIOS is not supported).
* **Internet**: Active connection required for installation.

---

## 2. Booting the ISO

1. Download the latest `jker-os-x86_64.iso` from GitHub Releases.
2. Flash the ISO to a USB flash drive (8GB+) using `dd` on Linux or `Rufus` (in DD mode) on Windows:
   ```bash
   sudo dd if=jker-os-x86_64.iso of=/dev/sdX bs=4M status=progress oflag=sync
   ```
3. Boot the target machine into UEFI firmware settings, disable Secure Boot, and select the USB drive as the primary boot target.

---

## 3. Launching the Installer

Upon booting, JKER OS will auto-login to the live desktop environment under the user `jker`. Open a terminal (`Super + Q`) and run the custom interactive installation script:

```bash
sudo jker-install
# Or execute manually from the installer directory:
sudo /usr/bin/installer/install.sh
```

---

## 4. Manual Installation Steps (Interactive Installer)

The installation script performs the following actions:
1. **Device Selection**: Discovers connected drives and requests a target disk.
2. **User Creation**: Prompts for system hostname, standard username, and secure passwords.
3. **Partitioning**: Formats a GPT table, creating a 512M FAT32 EFI boot partition and allocating the remaining block sector to an ext4 root partition.
4. **Bootstrap**: Performs `pacstrap` to write base libraries, kernels, and packages.
5. **Configuration**: Configures local clock timings, host networks, enables systemd services (`ufw`, `fail2ban`, `usbguard`, `docker`), and installs the GRUB UEFI bootloader.
6. **JKER Sync**: Transfers all custom applications (BlackVault, SentryOps, Download Center, Control Center) and desktop themes to the target partition.

---

## 5. Post-Installation Setup

Once installation reports successful completion, unmount media, reboot, and boot into the newly deployed drive. The default credentials for login are:
* **Username**: (The username you configured during installation, default is `jker-user`)
* **Password**: (The password you configured during installation)
* **Default Terminal Shell**: Zsh
