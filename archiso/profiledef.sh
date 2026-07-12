#!/usr/bin/env bash
# ==============================================================================
# JKER OS - ArchISO Build Profile Definition (profiledef.sh)
# Defines metadata, UEFI compatibility modes, and strict system permissions.
# ==============================================================================

iso_name="jker-os"
iso_label="JKER_OS"
iso_publisher="JKER OS Core Developers <https://github.com/jker-os/jker-os>"
iso_application="JKER OS Security & Developer Environment"
iso_version="1.0-Stable"
install_dir="jker"
buildmodes=('iso')
bootmodes=('uefi-x64.grub.esp' 'uefi-x64.grub.eltorito')
arch="x86_64"
pacman_conf="pacman.conf"

# Strict system and executable file permissions configuration
declare -A file_permissions=(
  ["/etc/shadow"]="0:0:0400"
  ["/etc/gshadow"]="0:0:0400"
  ["/etc/sudoers.d"]="0:0:0750"
  ["/etc/sudoers.d/10-wheel-nopasswd"]="0:0:0440"
  ["/usr/bin/blackvault"]="0:0:0755"
  ["/usr/bin/sentryops"]="0:0:0755"
  ["/usr/bin/downloadcenter"]="0:0:0755"
  ["/usr/bin/controlcenter"]="0:0:0755"
  ["/usr/bin/jker-hwdetect"]="0:0:0755"
  ["/usr/bin/jker-optimize"]="0:0:0755"
  ["/usr/bin/jker-syssetup"]="0:0:0755"
)
