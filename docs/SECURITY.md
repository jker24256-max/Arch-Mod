# JKER OS // Security Hardening Guidelines

This document details the security frameworks, policies, and parameters enabled by default in JKER OS.

---

## 1. USBGuard Hardening

USBGuard protects systems against rogue USB devices (like rubber duckies, bad USBs, or malicious storage blocks) by scanning device descriptors and applying verification policies.

* **Daemon Service**: `usbguard.service`
* **Configuration Path**: `/etc/usbguard/usbguard-daemon.conf`
* **Default Behavior**: Blocks all newly connected USB devices unless authorized by rules.
* **Generating Rules**:
  To authorize all currently connected devices during install or live booted stages, run:
  ```bash
  sudo usbguard generate-policy > /etc/usbguard/rules.conf
  ```
* **Managing Authorization**:
  Authorize a specific device dynamically:
  ```bash
  # List connected USB interfaces
  sudo usbguard list-devices
  # Allow device ID
  sudo usbguard allow-device <ID>
  ```

---

## 2. Intrusion Shielding (Fail2Ban)

Fail2Ban monitors log files (such as systemd journal, auth.log, sshd logs) for repeating authentication failures and automatically adds temporary bans to the local firewall rules.

* **Daemon Service**: `fail2ban.service`
* **Configuration Path**: `/etc/fail2ban/jail.local`
* **Default Settings**:
  * `bantime`: 10 minutes (banned hosts cannot query ports).
  * `findtime`: 10 minutes (window of scanning).
  * `maxretry`: 5 failures.

---

## 3. Host Firewall (UFW)

Uncomplicated Firewall (UFW) manages rules for incoming and outgoing socket packets.

* **Daemon Service**: `ufw.service`
* **Default Rules**:
  * Incoming: Block/Deny all traffic.
  * Outgoing: Allow all traffic.
* **Basic Configuration**:
  To verify status:
  ```bash
  sudo ufw status verbose
  ```
  To authorize specific ports (e.g., SSH port 22):
  ```bash
  sudo ufw allow 22/tcp
  ```

---

## 4. Kernel Protections & Process Isolation

Optimizations applied via sysctl to limit kernel manipulation exploits:
* **Memory Protections**: `vm.max_map_count=1048576` limits memory map overflow exposures.
* **Dmesg Restrictions**: Default kernel configs block access to dmesg logs for unprivileged accounts (`kernel.dmesg_restrict=1`) to prevent kernel address leak exploits.
