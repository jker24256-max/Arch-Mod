# JKER OS // ISO Compilation Guide

This document describes how to compile, clean, package, and verify the bootable JKER OS UEFI ISO image.

---

## 1. Prerequisites

To build the ISO locally on an Arch Linux host, install the build tools:
```bash
sudo pacman -S archiso rsync parted dosfstools
```

### Building on Ubuntu / Debian / GitHub Actions
If you are compiling on a non-Arch host system, the build script `build.sh` automatically detects this and executes the build inside a privileged Arch Linux Docker container. Ensure **Docker** is installed and running on your host system:
```bash
# Verify docker access
docker ps
```

---

## 2. Using the Build Pipeline

The pipeline is split into four simple shell execution scripts located in the root of the repository:

### A. Cleaning the Cache (`./clean.sh`)
Purges existing compiled files, temporary folders, and generated pacman manifests to prevent cache collisions:
```bash
./clean.sh
```

### B. Verification Tests (`./test.sh`)
Validates that all PyQt6 custom distribution applications (BlackVault, SentryOps, Download Center, Control Center, Wallpaper Manager, Graphical Installer) compile, import their libraries, and run without crashes:
```bash
./test.sh
```

### C. Building the ISO (`./build.sh`)
Compiles the ISO image based on the selected edition. It compiles package manifests and copies desktop settings, applications, and themes into the live filesystem overlay.
```bash
./build.sh --edition [lite | desktop | developer | cyber | enterprise]
```
*   **Arguments**:
    *   `--edition`: Specifies the target system profile. (Default is `desktop`).
*   **Arch host execution**: Runs `mkarchiso` directly on your host system.
*   **Non-Arch host execution**: Spawns an `archlinux:latest` Docker container automatically and executes the compilation within it.

### D. Packaging the Release (`./release.sh`)
Copies the compiled ISO to the `dist/` directory and generates a validation checksum file (`.sha256`):
```bash
./release.sh
```

---

## 3. Automated End-to-End Build Example

To clean, verify, build, and package the JKER OS **Cyber** edition:
```bash
# 1. Clean workspaces
./clean.sh

# 2. Compile and package the Cyber ISO
./build.sh --edition cyber

# 3. Hash and move to distribution folder
./release.sh
```
The resulting files will be located in the `dist/` directory:
*   `dist/jker-os-cyber-x86_64.iso`
*   `dist/jker-os-cyber-x86_64.iso.sha256`

---

## 4. Local VM Verification (QEMU)

Verify that the compiled ISO boots successfully in UEFI mode using the Archiso QEMU tool:
```bash
# Run ISO inside UEFI emulation virtual machine
run_archiso -u -i dist/jker-os-desktop-x86_64.iso
```
*   The `-u` parameter forces UEFI boot mode emulation.
*   Confirm the system loads SDDM and automatically logs into Hyprland.
