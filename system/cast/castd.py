#!/usr/bin/env python3
import asyncio
import os
import socket
from aiohttp import web

# Minimal offroad screen-cast signaling and receiver stub.
# Park-only gating is enforced by checking Params 'IsOnroad'.

from openpilot.common.params import Params

HTML_SEND = """
<!doctype html>
<meta name=viewport content="width=device-width, initial-scale=1">
<title>comma cast - sender</title>
<style>body{font-family:sans-serif;padding:16px} video{max-width:100%;background:#000}</style>
<h2>Comma cast (sender)</h2>
<p>Tap Share Screen to send your display to the device. Keep your phone/laptop paired to the car for audio.</p>
<button id=btn>Share Screen</button>
<video id=preview autoplay playsinline muted></video>
<script>
(async () => {
  const btn = document.getElementById('btn');
  const preview = document.getElementById('preview');
  let pc;
  async function start(){
    btn.disabled = true;
    const stream = await navigator.mediaDevices.getDisplayMedia({video: {frameRate: {ideal: 30}}, audio: false});
    preview.srcObject = stream;
    pc = new RTCPeerConnection();
    stream.getTracks().forEach(t => pc.addTrack(t, stream));

    pc.onconnectionstatechange = () => console.log('pc state', pc.connectionState);

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    const r = await fetch('/offer', {method:'POST', headers:{'content-type':'application/sdp'}, body: offer.sdp});
    const ans = await r.text();
    await pc.setRemoteDescription({type:'answer', sdp: ans});
  }
  btn.onclick = start;
})();
</script>
"""

async def index(request: web.Request):
  return web.Response(text=HTML_SEND, content_type='text/html')

async def offer(request: web.Request):
  # For now, we don't instantiate a real receiver pipeline here to keep footprint small.
  # We just respond with a dummy answer that will fail to connect until receiver is implemented.
  # This is a scaffolding point: integrate aiortc + PyAV + DRM/KMS here.
  sdp = await request.text()
  # TODO: replace with real SDP answer from aiortc
  return web.Response(text="", content_type='application/sdp')

async def guard_middleware(app, handler):
  async def middleware_handler(request):
    # Park-only: refuse when onroad
    try:
      p = Params()
      if p.get_bool('IsOnroad'):
        return web.Response(text='Casting disabled while onroad', status=403)
    except Exception:
      pass
    return await handler(request)
  return middleware_handler

async def main():
  app = web.Application(middlewares=[guard_middleware])
  app.router.add_get('/', index)
  app.router.add_get('/send', index)
  app.router.add_post('/offer', offer)

  # Bind to device IP
  port = int(os.environ.get('CAST_PORT', '8080'))
  runner = web.AppRunner(app)
  await runner.setup()
  site = web.TCPSite(runner, '0.0.0.0', port)
  await site.start()
  print(f'castd listening on http://{{get_ip()}}:{port}/send')
  while True:
    await asyncio.sleep(3600)

def get_ip():
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip
  except Exception:
    return 'device'

if __name__ == '__main__':
  asyncio.run(main())
