#!/bin/bash
# Install DBus policy for Miracast services
# This needs to run with root privileges

POLICY_FILE="/data/openpilot/selfdrive/camping/miracle-wifi.conf"
DEST_DIR="/etc/dbus-1/system.d"

if [ ! -f "$POLICY_FILE" ]; then
  echo "Policy file not found: $POLICY_FILE"
  exit 1
fi

# Check if we need to remount
if mount | grep -q "on / type.*[(,]ro[,)]"; then
  echo "Remounting / as read-write..."
  mount -o remount,rw /
  REMOUNT_RO=1
fi

# Install the policy
echo "Installing DBus policy..."
cp "$POLICY_FILE" "$DEST_DIR/" || exit 1

# Reload DBus
echo "Reloading DBus..."
systemctl reload dbus

# Remount read-only if we changed it
if [ "$REMOUNT_RO" = "1" ]; then
  echo "Remounting / as read-only..."
  mount -o remount,ro /
fi

echo "DBus policy installed successfully"