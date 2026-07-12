# JKER OS // Developer & Builder Guide

This guide details how to modify custom applications, configure build systems, and compile the UEFI ISO locally.

---

## 1. Modifying Custom Applications

The native JKER applications are built using Python 3 and PyQt6. They are located under the `applications/` directory:
* **BlackVault**: password and key management logic (`applications/blackvault/encryption.py` & `blackvault.py`).
* **SentryOps**: vulnerability diagnostic scans (`applications/sentryops/scanner.py` & `sentryops.py`).
* **Download Center**: system packaging links (`applications/downloadcenter/downloadcenter.py`).
* **Control Center**: personalization settings and system services (`applications/controlcenter/controlcenter.py`).

### Local Development Environment Setup
To run and test these applications locally on an Arch Linux development host, install dependencies:
```bash
sudo pacman -S python-pyqt6 python-cryptography nmap networkmanager
```
Execute any application directly:
```bash
python3 applications/blackvault/blackvault.py
```

---

## 2. Rebuilding the ISO Locally

JKER OS is built using the standard ArchISO profile system. To compile a bootable UEFI ISO image locally, follow these steps:

1. **Install ArchISO tools**:
   ```bash
   sudo pacman -S archiso
   ```
2. **Synchronize configurations**:
   Ensure all configurations and custom binary scripts are placed in the profile directory:
   * System configuration directories inside `archiso/airootfs/etc/skel/`.
   * Applications copied to `/usr/share/jker-apps/` and executable shell wrappers in `/usr/bin/`.
3. **Execute mkarchiso**:
   Run the build script pointing to the profile path and specifying a scratch work directory:
   ```bash
   mkdir -p /tmp/archiso-work
   sudo mkarchiso -v -w /tmp/archiso-work -o ./build ./archiso
   ```

---

## 3. Testing with QEMU

Test the compiled ISO image inside QEMU virtual machine to confirm UEFI booting:
```bash
run_archiso -u -i ./build/jker-os-x86_64.iso
```
* Note: The `-u` flag enables UEFI boot interface variables inside QEMU.
