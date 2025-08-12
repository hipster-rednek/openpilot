from tools.lib.logreader import LogReader
import sys

path = sys.argv[1]

lr = LogReader(path, sort_by_time=True)

interesting_addrs = {0x738: 'ADAS(0x730)', 0x7B8: 'Camera(0x7B0)', 0x7D8: 'Unknown(0x7D0)'}
replies = []
negatives = []
pending = []

for m in lr:
  if m.which() != 'can':
    continue
  for pkt in m.can:
    addr = pkt.address
    if addr in interesting_addrs:
      dat = bytes(pkt.dat)
      if len(dat) >= 2:
        # Single frame positive
        if dat[0] in (0x02, 0x03, 0x04) and dat[1] == 0x62:
          replies.append((pkt.src, addr, dat.hex()))
        # Negative response
        if dat[0] in (0x03, 0x04) and dat[1] == 0x7F:
          negatives.append((pkt.src, addr, dat.hex()))
        # Response pending (0x7F 0x22 0x78) often appears in multi-frame
        if dat[1:4] == b"\x7f\x22\x78":
          pending.append((pkt.src, addr, dat.hex()))

print('Positive RDBI single-frame replies:', len(replies))
for i in replies[:20]:
  print(i)
print('Negative replies:', len(negatives))
for i in negatives[:20]:
  print(i)
print('Response pending indications:', len(pending))
for i in pending[:20]:
  print(i)
