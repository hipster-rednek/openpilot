#!/usr/bin/env bash
set -euo pipefail

VENV_PY="/usr/local/venv/bin/python3"
VENV_PIP="/usr/local/venv/bin/pip3"

if [[ ! -x "$VENV_PY" ]]; then
  echo "No /usr/local/venv/python3 found. This script targets comma devices." >&2
  exit 1
fi

# Upgrade pip/setuptools/wheel first
$VENV_PY -m pip install --upgrade pip setuptools wheel

# Try to install required packages. These may pull prebuilt wheels; if building from source is required, it may fail.
REQS=(
  "av==10.0.0"
  "aiortc==1.6.0"
  "PySDL2==0.9.16"
)

for pkg in "${REQS[@]}"; do
  echo "Installing $pkg ..."
  if ! $VENV_PIP install "$pkg"; then
    echo "WARN: failed to install $pkg. You may need prebuilt wheels for aarch64." >&2
  fi
done

# Optional: verify imports
$VENV_PY - <<'PY'
import sys
ok = True
for m in ("av","aiortc","sdl2"):
  try:
    __import__(m)
    print(f"OK: {m}")
  except Exception as e:
    ok = False
    print(f"FAIL: {m} -> {e}")
if not ok:
  sys.exit(1)
PY

echo "Cast deps install attempted. If any FAIL above, casting may not start."
