#!/bin/bash
set -euo pipefail

DEST=/data/camping/bin
echo "Installing receiver binaries to $DEST"
mkdir -p "$DEST"

copy_if_exists() {
  local src="$1"; local dst_name="$2"
  if [ -x "$src" ]; then
    install -m 0755 "$src" "$DEST/$dst_name"
    echo "installed $(basename "$src") -> $DEST/$dst_name"
  fi
}

# MiracleCast daemons/tools (Miracast-only)
copy_if_exists selfdrive/camping/bin/miracle-wifid miracle-wifid
copy_if_exists selfdrive/camping/bin/miracle-wifictl miracle-wifictl
copy_if_exists selfdrive/camping/bin/miracle-sinkctl miracle-sinkctl

# If /etc/dbus-1/system.d exists and we have a policy file, install it (best effort)
if [ -d /etc/dbus-1/system.d ] && [ -f selfdrive/camping/miracle-wifi.conf ]; then
  echo "Installing DBus policy (requires root)"
  if command -v sudo >/dev/null 2>&1; then
    sudo install -m 0644 selfdrive/camping/miracle-wifi.conf /etc/dbus-1/system.d/miracle-wifi.conf || true
    sudo systemctl reload dbus || true
  else
    install -m 0644 selfdrive/camping/miracle-wifi.conf /etc/dbus-1/system.d/miracle-wifi.conf || true
    systemctl reload dbus || true
  fi
fi

echo "Done. Ensure files exist and are executable on device."
