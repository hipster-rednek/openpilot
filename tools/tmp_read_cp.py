from tools.lib.logreader import LogReader
from collections import Counter
from cereal import car as capnp_car
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "a5205fb7e46c605b_00000074--0e5fb2ebce--0--rlog.zst"

lr = LogReader(path, sort_by_time=True)

# Count messages
c = Counter(m.which() for m in lr)
print("total msgs:", sum(c.values()))
print("top msgs:", c.most_common(10))

# Reset iterator
lr.reset()
cp = None
for m in lr:
  if m.which() == 'carParams':
    cp = m.carParams
    break

if cp is None:
  print('No carParams in rlog')
  sys.exit(0)

has_adas = any(fw.ecu == capnp_car.CarParams.Ecu.adas for fw in cp.carFw)
print('carFingerprint:', cp.carFingerprint)
print('flags:', cp.flags)
print('alphaLongitudinalAvailable:', cp.alphaLongitudinalAvailable)
print('openpilotLongitudinalControl:', cp.openpilotLongitudinalControl)
print('radarUnavailable:', cp.radarUnavailable)
print('has_adas_fw:', has_adas)
print('num_fw_entries:', len(cp.carFw))

# Try to locate a carState to inspect fingerprint buses
lr.reset()
first_cs = None
for m in lr:
  if m.which() == 'carState':
    first_cs = m.carState
    break

if first_cs is None:
  print('No carState found')
else:
  # fingerprint is a list of dicts (capnp Map) by bus index
  fp = {int(k): {int(k2): int(v2) for k2, v2 in v.items()} for k, v in first_cs.fingerprint.items()}
  cam_bus = 2
  ecan_bus = 1
  print('fingerprint buses:', sorted(fp.keys()))
  print('radar start (0x4B0=1200) on ECAN bus:', 1200 in fp.get(ecan_bus, {}))
  print('LKA 0x50 on cam bus:', 0x50 in fp.get(cam_bus, {}))
  print('LKA_ALT 0x110 on cam bus:', 0x110 in fp.get(cam_bus, {}))
