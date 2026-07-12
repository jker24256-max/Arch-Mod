# JKER OS // System Installation Guide

This document describes how to boot JKER OS and deploy it persistently onto target physical or virtual hardware.

---

## 1. System Requirements

*   **Processor**: 64-bit x86_64 compatible CPU (Intel Core i3 / AMD Ryzen 3 or higher recommended).
*   **Memory**: 4 GB RAM minimum (8 GB recommended for multitasking and cyber audits).
*   **Storage**: 20 GB of free space (SSD strongly recommended for rapid execution).
*   **Boot Mode**: UEFI (Legacy BIOS is not supported by JKER OS).
*   **Internet**: Required only for *Online Installation* mode (offline installs are self-contained).

---

## 2. Preparing Boot Media

1.  Download the latest `jker-os-x86_64.iso` and `jker-os-x86_64.iso.sha256` from GitHub Releases.
2.  Verify the download integrity:
    ```bash
    sha256sum -c jker-os-x86_64.iso.sha256
    ```
3.  Write the ISO to a USB flash drive (8GB+ size) using `dd` on Linux:
    ```bash
    sudo dd if=jker-os-x86_64.iso of=/dev/sdX bs=4M status=progress oflag=sync
    ```
    *Replace `/dev/sdX` with your target raw USB disk path.*
4.  Boot the target machine into UEFI firmware settings, disable **Secure Boot**, and select the USB drive as the primary boot target.

---

## 3. Launching the Graphical Installer

Upon booting, JKER OS automatically logs into a live desktop session under the user account `jker`. The system will prompt you with the custom JKER Graphical Installer, which can also be launched manually:

*   **Terminal Shortcut**: Open a terminal (`Super + Q`) and run:
    ```bash
    sudo jker-install
    ```
*   **Rofi Menu**: Press `Super + R`, type `Installer`, and press `Enter` (runs with elevated privileges via `pkexec`).

---

## 4. Graphical Installer Wizards

The installer guides you through a multi-step installation workflow:

### Step 1: Welcome & Mode Selection
*   **Target Hardware**: Optimizes system settings. Choosing **SSD** enables daily SSD `fstrim` scheduling and sets non-rotational scheduling policies. Choosing **USB** limits disk writeback aggression to prevent sector wear.
*   **Installation Mode**:
    *   *Offline (SquashFS Clone)*: Copies the live environment image files directly to the disk target. This is extremely fast (takes under 2 minutes) and does not require internet, guaranteeing an identical setup to the live environment.
    *   *Online (Pacstrap)*: Performs a bootstrap download from the Arch Linux mirrorlists, pulling the latest security updates.

### Step 2: Locales & Timezone
*   Select your system locale (e.g., `en_US.UTF-8`), keyboard keymap layout (e.g., `us`), and region timezone.

### Step 3: User Accounts
*   Set a custom system **Hostname** (e.g., `my-jker-pc`).
*   Define a standard user **Username** and configure a secure login password.

### Step 4: Storage Partitioning
*   Select your target hard drive (e.g., `/dev/sda` or `/dev/nvme0n1`).
*   **Automatic Partitioning (Recommended)**: Erases the disk, initializes a GPT partition table, structures a 512MB EFI System Partition (FAT32 formatted), and mounts the remaining disk sectors as an ext4 root partition.
*   **Manual Partitioning**: Allows choosing pre-existing partitions (e.g., using `/dev/sda1` for EFI and `/dev/sda2` for root).

### Step 5: Summary & Deployment
*   Review all configured settings. Click **DEPLOY JKER OS** to start the installation.
*   The installer will spawn a background progress worker, formatting disks, mounting directories, extracting/installing package assets, configuring locales/user accounts, setting up NetworkManager network setups, and writing the GRUB UEFI bootloader to target sectors. Progress outputs are piped to the scrolling log terminal console.

---

## 5. Post-Installation Reboot

1.  When the success window displays, close the installer.
2.  Open a terminal and run `reboot` or select restart from the power menu.
3.  Remove the installation USB drive.
4.  Boot into the GRUB boot menu and enter your user password configured during install!
