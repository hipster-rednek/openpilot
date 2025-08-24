#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
MIT Non-Commercial License

Copyright (c) 2019, dragonpilot

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, for non-commercial purposes only, subject to the following conditions:

- The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
- Commercial use (e.g., use in a product, service, or activity intended to generate revenue) is prohibited without explicit written permission from dragonpilot. Contact ricklan@gmail.com for inquiries.
- Any project that uses the Software must visibly mention the following acknowledgment: "This project uses software from dragonpilot and is licensed under a custom license requiring permission for use."

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import os
import signal
import threading
import socket
import math
from datetime import datetime
from urllib.parse import urlparse, parse_qs, quote
from openpilot.system.hardware import PC

HOST = '0.0.0.0'
PORT = 5000
DEFAULT_DIR = os.path.realpath('.' if PC else '/data/media/0/realdata')

def format_file_size(size_bytes):
  """Formats a file size in bytes to a human-readable string (B, KB, MB, GB)."""
  if size_bytes == 0:
    return "0 B"
  size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
  i = int(math.floor(math.log(size_bytes, 1024)))
  p = math.pow(1024, i)
  s = round(size_bytes / p, 1)
  return f"{s} {size_name[i]}"

def get_safe_path(requested_path):
    """Joins the requested path with the base directory and resolves it, ensuring it's safe."""
    combined_path = os.path.join(DEFAULT_DIR, requested_path.lstrip('/'))
    safe_path = os.path.realpath(combined_path)
    if os.path.commonprefix((safe_path, DEFAULT_DIR)) == DEFAULT_DIR:
        return safe_path
    return None

def list_directory(client_socket, path):
  try:
    if not os.path.isdir(path):
      response = "HTTP/1.1 404 Not Found\r\n\r\n"
      client_socket.sendall(response.encode())
      return

    items = []
    for entry in os.listdir(path):
      full_path = os.path.join(path, entry)
      try:
        stat = os.stat(full_path)
        is_dir = os.path.isdir(full_path)
        items.append({
          'name': entry,
          'is_dir': is_dir,
          'mtime': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
          'size': stat.st_size if not is_dir else 0
        })
      except FileNotFoundError:
        continue

    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

    # --- HTML and CSS for the page ---
    content = """
<!DOCTYPE html>
<html>
<head>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<meta charset="UTF-8">
<title>FileServ by dragonpilot</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif; margin: 0; background-color: #f8f9fa; color: #212529; }
  .container { max-width: 960px; margin: 20px auto; padding: 0 10px; }
  h3 { border-bottom: 2px solid #dee2e6; padding-bottom: 10px; margin-top: 0; font-weight: 500; }
  table { width: 100%; border-collapse: collapse; }
  th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #dee2e6; white-space: nowrap; }
  th { background-color: #f1f3f5; font-weight: 600; }
  tr:hover { background-color: #f1f3f5; }
  a { text-decoration: none; color: #007bff; font-weight: 500; }
  a:hover { text-decoration: underline; }
  .play-link { font-weight: bold; color: #28a745; font-size: 1.5em; text-align: center; display: block; }
  th.actions-col, td.actions-col { width: 1%; padding-right: 5px; padding-left: 5px; }
  .name-col { word-break: break-all; white-space: normal; }
  td.size { text-align: right; font-family: "Menlo", "Consolas", "Courier New", monospace; color: #495057; }
  .path-links { margin-bottom: 20px; font-size: 1.1em; word-wrap: break-word; }
  .path-links a { color: #495057; }

  /* Responsive styles for mobile */
  @media screen and (max-width: 600px) {
    .container { margin: 0; padding: 0; }
    h3, .path-links { padding-left: 10px; padding-right: 10px; }
    th, td { padding: 10px 8px; }
    .hide-on-mobile { display: none; }
  }
</style>
</head>
<body>
<div class="container">
"""
    # Breadcrumb navigation
    content += "<h3>FileServ by dragonpilot</h3>"
    content += "<div class='path-links'><strong>Path:</strong> "
    relative_path_from_root = os.path.relpath(path, DEFAULT_DIR)
    content += "<a href='/'>/</a>"
    if relative_path_from_root != ".":
        current_href = ""
        for part in relative_path_from_root.split(os.sep):
            current_href = os.path.join(current_href, part)
            content += f" <a href='/{current_href}/'>{part}</a> /"
    content += "</div>"

    # Table header - Swapped 'hide-on-mobile' from Last Modified to Size
    content += "<table><thead><tr><th class='actions-col'></th><th>Name</th><th>Last Modified</th><th class='size hide-on-mobile'>Size</th></tr></thead><tbody>"

    # Parent directory link
    if path != DEFAULT_DIR:
        content += "<tr><td class='actions-col'></td><td class='name-col'><a href='..'>.. (Parent Directory)</a></td><td></td><td class='size hide-on-mobile'>-</td></tr>"

    # Table rows for directories and files
    for item in items:
        relative_item_path = os.path.relpath(os.path.join(path, item['name']), DEFAULT_DIR)
        encoded_path = quote(relative_item_path)

        size_str = format_file_size(item['size']) if not item['is_dir'] else '-'

        actions_cell = ""
        if not item['is_dir'] and item['name'].endswith('.ts'):
            actions_cell = f"<a href='/play?file={encoded_path}' class='play-link' target='_blank'>▶</a>"

        # Assemble the row with the 'hide-on-mobile' class on the correct cell
        content += f"<tr>"
        content += f"<td class='actions-col'>{actions_cell}</td>"
        content += f"<td class='name-col'><a href='/{encoded_path}{'/' if item['is_dir'] else ''}'>{item['name']}</a></td>"
        content += f"<td>{item['mtime']}</td>"
        content += f"<td class='size hide-on-mobile'>{size_str}</td>"
        content += f"</tr>"


    content += "</tbody></table></div></body></html>"

    body = content.encode("utf-8")
    response_headers = f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {len(body)}\r\n\r\n"
    client_socket.sendall(response_headers.encode())
    client_socket.sendall(body)

  except Exception as e:
    response = f"HTTP/1.1 500 Internal Server Error\r\n\r\n<h3>500 Internal Server Error</h3><p>{e}</p>"
    client_socket.sendall(response.encode())

def serve_player(client_socket, file_path):
    encoded_path = quote(file_path)
    html = f"""
<!DOCTYPE html><html><head><title>HLS Player</title><style>body,html{{margin:0;padding:0;height:100%;background-color:#000}}#video{{width:100%;height:100%}}</style><script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script></head><body><video id="video" controls autoplay></video><script>var v=document.getElementById('video'),s='/manifest.m3u8?file={encoded_path}';if(Hls.isSupported()){{var h=new Hls();h.loadSource(s);h.attachMedia(v)}}else if(v.canPlayType('application/vnd.apple.mpegurl')){{v.src=s}}</script></body></html>"""
    body = html.encode('utf-8')
    headers = f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {len(body)}\r\n\r\n"
    client_socket.sendall(headers.encode())
    client_socket.sendall(body)

def serve_manifest(client_socket, file_path):
    encoded_path = quote(file_path)
    manifest = f"""#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:60\n#EXT-X-PLAYLIST-TYPE:VOD\n#EXTINF:60.0,\n/{encoded_path}\n#EXT-X-ENDLIST\n"""
    body = manifest.encode('utf-8')
    headers = f"HTTP/1.1 200 OK\r\nContent-Type: application/vnd.apple.mpegurl\r\nContent-Length: {len(body)}\r\n\r\n"
    client_socket.sendall(headers.encode())
    client_socket.sendall(body)

def handle_request(client_socket):
  try:
    request = client_socket.recv(1024).decode('utf-8')
    if not request: return

    first_line = request.split('\r\n')[0]
    parts = first_line.split()
    if len(parts) < 2: return

    method, full_path = parts[0], parts[1]
    url = urlparse(full_path)
    path_qs = parse_qs(url.query)

    file_param = path_qs.get('file', [None])[0]

    if url.path == '/play' and file_param:
        serve_player(client_socket, file_param)
        return
    if url.path == '/manifest.m3u8' and file_param:
        serve_manifest(client_socket, file_param)
        return

    safe_path = get_safe_path(url.path)
    if not safe_path:
        client_socket.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\nAccess denied.")
        return

    if os.path.isfile(safe_path):
      file_extension = os.path.splitext(safe_path)[1].lower()
      content_type = "application/octet-stream"
      if file_extension == '.ts':
        content_type = "video/mp2t"

      file_size = os.path.getsize(safe_path)
      response = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {file_size}\r\n\r\n"
      client_socket.sendall(response.encode())

      with open(safe_path, 'rb') as f:
        while chunk := f.read(8192):
          try:
            client_socket.sendall(chunk)
          except BrokenPipeError:
            break

    elif os.path.isdir(safe_path):
      list_directory(client_socket, safe_path)

    else:
      client_socket.sendall(b"HTTP/1.1 404 Not Found\r\n\r\nNot Found.")

  except Exception:
    pass
  finally:
    client_socket.close()


def start_server():
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  server_socket.bind((HOST, PORT))
  server_socket.listen(5)

  while True:
    try:
      client_socket, _ = server_socket.accept()
      threading.Thread(target=handle_request, args=(client_socket,)).start()
    except KeyboardInterrupt:
      break
  server_socket.close()

def main():
  print(f"Server starting on http://{HOST}:{PORT}")

  server_thread = threading.Thread(target=start_server)
  server_thread.daemon = True
  server_thread.start()

  signal.signal(signal.SIGINT, lambda s, f: os._exit(0))
  signal.signal(signal.SIGTERM, lambda s, f: os._exit(0))

  server_thread.join()

if __name__ == "__main__":
  main()