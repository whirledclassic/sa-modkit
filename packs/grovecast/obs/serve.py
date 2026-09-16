# -*- coding: utf-8 -*-
from __future__ import print_function
import json, os, sys
try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.abspath(os.path.dirname(__file__))
PORT = 8099

def find_cast_ini():
    candidates = [
        os.path.abspath(os.path.join(HERE, os.pardir, "cast.ini")),
        os.path.join(HERE, "cast.ini"),
    ]
    kit = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir, os.pardir))
    remembered = os.path.join(kit, "GTA_DIR.txt")
    if os.path.isfile(remembered):
        try:
            folder = open(remembered, "r").read().strip()
            candidates.append(os.path.join(folder, "CLEO", "GroveLink", "cast.ini"))
        except Exception:
            pass
    for folder in (
        r"C:\GTA San Andreas", r"D:\GTA San Andreas", r"E:\GTA San Andreas",
        r"C:\Program Files (x86)\Rockstar Games\GTA San Andreas",
        r"C:\Program Files\Rockstar Games\GTA San Andreas",
    ):
        candidates.append(os.path.join(folder, "CLEO", "GroveLink", "cast.ini"))
    for path in candidates:
        if os.path.isfile(path):
            return path
    return candidates[0]

def read_ini(path):
    data, current = {}, None
    if not path or not os.path.isfile(path):
        return data
    try:
        fh = open(path, "r")
        try:
            for raw in fh:
                line = raw.strip()
                if line.startswith("[") and line.endswith("]"):
                    current = line[1:-1]
                elif current == "cast" and "=" in line:
                    key, val = line.split("=", 1)
                    data[key.strip()] = val.strip()
        finally:
            fh.close()
    except Exception:
        return data
    return data

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return
    def _send(self, body, mime, code=200):
        if not isinstance(body, bytes):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/obs", "/index.html"):
            html = os.path.join(HERE, "index.html")
            try:
                body = open(html, "r").read()
            except Exception:
                body = "<html><body>missing index.html</body></html>"
            self._send(body, "text/html; charset=utf-8")
            return
        if path == "/cast.json":
            ini = find_cast_ini()
            payload = read_ini(ini)
            payload["_ini"] = ini
            payload["_ok"] = "1" if os.path.isfile(ini) else "0"
            self._send(json.dumps(payload), "application/json")
            return
        self.send_error(404)

def main():
    print("GroveCast OBS  http://127.0.0.1:%s/obs" % PORT)
    print("cast.ini       %s" % find_cast_ini())
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopped.")

if __name__ == "__main__":
    main()
