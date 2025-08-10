#!/bin/bash
set -euo pipefail

# Build script for Miraclecast on agnos OS (aarch64)
# Requires (on device/agnos): meson, ninja, pkg-config, glib2, systemd-dev, readline, gstreamer devs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIRACAST_DIR="$SCRIPT_DIR/miraclecast"
BUILD_DIR="$MIRACAST_DIR/build"
OUTPUT_DIR="$SCRIPT_DIR/bin"

# Check for required build tools
if ! command -v meson &> /dev/null || ! command -v ninja &> /dev/null; then
  echo "WARNING: meson or ninja not found. Skipping MiracleCast build."
  echo "To build MiracleCast, install: meson ninja-build"
  exit 0
fi

# Check if submodule is initialized
if [ ! -d "$MIRACAST_DIR" ] || [ ! -f "$MIRACAST_DIR/meson.build" ]; then
  echo "Initializing miraclecast submodule..."
  cd "$(dirname "$MIRACAST_DIR")"
  if [ ! -d miraclecast ]; then
    git clone https://github.com/albfan/miraclecast.git miraclecast
  fi
  cd "$SCRIPT_DIR"
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Clean previous build
if [ -d "$BUILD_DIR" ]; then
  rm -rf "$BUILD_DIR"
fi

echo "Configuring MiracleCast..."
cd "$MIRACAST_DIR"
# Prefer native build on device; fallback to cross if present
MESON_ARGS=(
  "${BUILD_DIR}"
  "--prefix=/usr"
  "--buildtype=release"
  "-Drely-udev=false"
  "-Dbuild-tests=false"
  "-Denable-systemd=false"
)
if [ -f /usr/local/share/meson/cross/aarch64-linux-gnu.txt ]; then
  MESON_ARGS+=("--cross-file=/usr/local/share/meson/cross/aarch64-linux-gnu.txt")
fi
meson setup "${MESON_ARGS[@]}"

# Build
echo "Building MiracleCast..."
ninja -C "$BUILD_DIR"

# Copy binaries to output directory
echo "Copying binaries to $OUTPUT_DIR..."
cp "$BUILD_DIR/src/wifi/miracle-wifid" "$OUTPUT_DIR/"
cp "$BUILD_DIR/src/ctl/miracle-wfdctl" "$OUTPUT_DIR/"
cp "$BUILD_DIR/src/ctl/miracle-sinkctl" "$OUTPUT_DIR/"

# Make binaries executable
chmod +x "$OUTPUT_DIR"/*

echo "Build complete! Binaries are in $OUTPUT_DIR"
echo "Run scripts/install_camping_receiver.sh to install on device"