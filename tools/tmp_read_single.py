from tools.lib.logreader import _LogFileReader
from cereal import car as capnp_car
from collections import Counter
import sys

path = sys.argv[1]

lr = _LogFileReader(path, sort_by_time=True)
# Count top messages
c = Counter(m.which() for m in lr)
print("total msgs:", sum(c.values()))
print("top msgs:", c.most_common(10))

# Reset and search for carParams
lr = _LogFileReader(path, sort_by_time=True)
cp = None
for m in lr:
  if m.which() == 'carParams':
    cp = m.carParams
    break

print('has carParams:', bool(cp))
if not cp:
  sys.exit(0)

has_adas = any(fw.ecu == capnp_car.CarParams.Ecu.adas for fw in cp.carFw)
print('carFingerprint:', cp.carFingerprint)
print('flags:', cp.flags)
print('alphaLongitudinalAvailable:', cp.alphaLongitudinalAvailable)
print('openpilotLongitudinalControl:', cp.openpilotLongitudinalControl)
print('radarUnavailable:', cp.radarUnavailable)
print('has_adas_fw:', has_adas)
print('num_fw_entries:', len(cp.carFw))
