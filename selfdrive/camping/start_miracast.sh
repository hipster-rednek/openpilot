#!/bin/bash
# Start Miracast services for camping mode
# This runs independently of Python/openpilot

CAMPING_BIN="/data/camping/bin"
WIFID="$CAMPING_BIN/miracle-wifid"
SINKCTL="$CAMPING_BIN/miracle-sinkctl"

# Check if binaries exist
if [ ! -x "$WIFID" ]; then
  echo "miracle-wifid not found at $WIFID"
  exit 1
fi

echo "Starting Miracast WiFi Direct daemon..."

# Enable p2p0 interface
ip link set p2p0 up 2>/dev/null || echo "Could not bring up p2p0"

# Try p2p0 first, fall back to wlan0
INTERFACE="p2p0"
# Consider interface available if it exists at all; it may be brought up by wifid
if [ ! -d "/sys/class/net/p2p0" ]; then
  echo "p2p0 not available, using wlan0"
  INTERFACE="wlan0"
fi

echo "Using interface: $INTERFACE"

# Start miracle-wifid in background (bind to chosen interface)
"$WIFID" -i "$INTERFACE" --log-level info &
WIFID_PID=$!

# Wait for wifid to initialize
sleep 3

# Check if wifid is still running
if ! kill -0 $WIFID_PID 2>/dev/null; then
  echo "miracle-wifid failed to start"
  exit 1
fi

echo "miracle-wifid started (PID: $WIFID_PID)"

# Start sinkctl if available
if [ -x "$SINKCTL" ]; then
  echo "Starting Miracast sink controller..."
  # Run sinkctl with proper commands
  # First set managed, then run/bind on selected interface
  (
    sleep 5  # Wait for wifid to initialize
    echo "set-managed $INTERFACE yes"
    echo "bind $INTERFACE"
    echo "run $INTERFACE"
    # Keep it running
    while true; do
      sleep 60
      echo "list"
    done
  ) | "$SINKCTL" --log-level info &
  SINKCTL_PID=$!
  echo "miracle-sinkctl started (PID: $SINKCTL_PID)"
fi

echo "Miracast services started successfully"
echo "Your device should now be discoverable for screen mirroring"

# Keep running and monitor
while true; do
  if ! kill -0 $WIFID_PID 2>/dev/null; then
    echo "miracle-wifid stopped, restarting..."
    "$WIFID" -i "$INTERFACE" --log-level info &
    WIFID_PID=$!
  fi
  sleep 10
done