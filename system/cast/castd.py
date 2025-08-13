#!/usr/bin/env python3
import asyncio
import os
import socket
import json
from aiohttp import web

# Minimal offroad screen-cast signaling and receiver stub.
# Park-only gating is enforced by checking Params 'IsOnroad'.

from openpilot.common.params import Params

# Optional deps for full receiver
_AIORTC_OK = True
try:
  from aiortc import RTCPeerConnection, RTCSessionDescription
  from aiortc.contrib.media import MediaBlackhole
except Exception:
  _AIORTC_OK = False

_AV_OK = True
try:
  import av  # PyAV for frame decoding
except Exception:
  _AV_OK = False

_SDL_OK = True
try:
  import sdl2
  import sdl2.ext
except Exception:
  _SDL_OK = False

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

class VideoRenderer:
  def __init__(self):
    self.initialized = False
    self.window = None
    self.surface = None
    self.renderer = None
    self.texture = None
    self.size = (0, 0)

  def init(self, w: int, h: int):
    if not _SDL_OK:
      return
    if self.initialized and (w, h) == self.size:
      return
    if not self.initialized:
      sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
      flags = sdl2.SDL_WINDOW_FULLSCREEN if os.environ.get('CAST_FULLSCREEN', '1') == '1' else 0
      self.window = sdl2.SDL_CreateWindow(b"comma cast", sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED, w, h, flags)
      self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, 0)
      self.initialized = True
    self.size = (w, h)
    if self.texture is not None:
      sdl2.SDL_DestroyTexture(self.texture)
    self.texture = sdl2.SDL_CreateTexture(self.renderer, sdl2.SDL_PIXELFORMAT_RGB24, sdl2.SDL_TEXTUREACCESS_STREAMING, w, h)

  def draw_rgb(self, rgb_bytes: bytes, w: int, h: int):
    if not _SDL_OK:
      # fallback: drop frame
      return
    self.init(w, h)
    pitch = w * 3
    sdl2.SDL_UpdateTexture(self.texture, None, rgb_bytes, pitch)
    sdl2.SDL_RenderClear(self.renderer)
    sdl2.SDL_RenderCopy(self.renderer, self.texture, None, None)
    sdl2.SDL_RenderPresent(self.renderer)


renderer = VideoRenderer()


async def offer(request: web.Request):
  if not (_AIORTC_OK and _AV_OK):
    return web.Response(status=500, text='aiortc/av not available')

  # Park-only gate
  p = Params()
  if p.get_bool('IsOnroad'):
    return web.Response(status=403, text='onroad')

  sdp = await request.text()
  pc = RTCPeerConnection()

  @pc.on("track")
  def on_track(track):
    if track.kind == "video":
      async def reader():
        while True:
          frame = await track.recv()
          # frame is av.VideoFrame
          img = frame.to_ndarray(format='rgb24')
          h, w, _ = img.shape
          renderer.draw_rgb(img.tobytes(), w, h)
      asyncio.create_task(reader())
    else:
      # ignore audio; keep audio on phone -> car BT
      asyncio.create_task(MediaBlackhole().recv(track))

  await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type='offer'))
  answer = await pc.createAnswer()
  await pc.setLocalDescription(answer)
  return web.Response(text=pc.localDescription.sdp, content_type='application/sdp')

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
