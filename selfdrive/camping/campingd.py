#!/usr/bin/env python3
import os
import time
import subprocess

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog

"""
Camping mode Miracast receiver launcher.
- Runs offroad only (manager gating), behind Params key `CampingMode`.
- Launches Miracast receiver for screen mirroring from phones/devices.
"""

def main():
  params = Params()
  cloudlog.event("campingd.start")

  # Launch Miracast receiver using MiracleCast only
  proc = None
  sink_proc = None
  try:
    local_bin = "/data/camping/bin"
    wifid = os.path.join(local_bin, "miracle-wifid")
    sinkctl = os.path.join(local_bin, "miracle-sinkctl")
    # Fallback to repo-staged binaries if /data install missing
    if not (os.path.exists(wifid) and os.access(wifid, os.X_OK)):
      repo_bin = os.path.join("/data/openpilot", "selfdrive", "camping", "bin")
      wifid_repo = os.path.join(repo_bin, "miracle-wifid")
      sinkctl_repo = os.path.join(repo_bin, "miracle-sinkctl")
      if os.path.exists(wifid_repo) and os.access(wifid_repo, os.X_OK):
        wifid = wifid_repo
      if os.path.exists(sinkctl_repo) and os.access(sinkctl_repo, os.X_OK):
        sinkctl = sinkctl_repo

    if os.path.exists(wifid) and os.access(wifid, os.X_OK):
      # Prefer dedicated P2P interface when available; fall back to wlan0
      preferred_iface = "p2p0" if os.path.isdir("/sys/class/net/p2p0") else "wlan0"
      # Start miracle-wifid with proper arguments. Requires root; try sudo -n when not root.
      cmd = [wifid, "-i", preferred_iface, "--log-level", "info"]
      if os.geteuid() != 0:
        cmd = ["sudo", "-n", *cmd]
      proc = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      cloudlog.event("campingd.receiver", name="miracle-wifid", interface=preferred_iface)
      
      # Wait a bit for wifid to start
      time.sleep(2)
      
      # Check if process is still running
      if proc.poll() is not None:
        stdout, stderr = proc.communicate(timeout=1)
        cloudlog.event("campingd.wifid_failed", 
                      stdout=stdout.decode('utf-8', errors='ignore'),
                      stderr=stderr.decode('utf-8', errors='ignore'))
        proc = None
      else:
        # If sink control exists, run in auto-accept mode to act as a sink
        if os.path.exists(sinkctl) and os.access(sinkctl, os.X_OK):
          try:
            sink_proc = subprocess.Popen([sinkctl, "-a"],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            cloudlog.event("campingd.sinkctl", name="miracle-sinkctl", args="-a")
          except Exception:
            cloudlog.exception("campingd.sinkctl_start_failed", error=False)
    else:
      cloudlog.event("campingd.receiver", name="miracast_not_found", path=wifid)

    # heartbeat loop
    while True:
      time.sleep(1.0)
      # allow runtime disable
      if not params.get_bool("CampingMode"):
        cloudlog.event("campingd.stop_param")
        break
  except Exception as e:
    cloudlog.exception("campingd.exception", error=True)
  finally:
    if proc and proc.poll() is None:
      proc.terminate()
      try:
        proc.wait(timeout=2)
      except Exception:
        proc.kill()
    cloudlog.event("campingd.exit")

if __name__ == "__main__":
  main()
