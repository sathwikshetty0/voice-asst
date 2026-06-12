import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class ProxyHandler(BaseHTTPRequestHandler):
    server_version = 'VoiceAssistantProxy/1.0'

    def do_GET(self):
        if self.path.startswith('/api/health'):
            self._send_json(200, {'ok': True, 'service': 'nvidia-proxy'})
            return

        if self.path.startswith('/api/nvidia'):
            self._send_json(405, {'error': 'Use POST for NVIDIA requests.'})
            return

        return self._serve_static()

    def do_POST(self):
        if self.path.startswith('/api/nvidia'):
            self._proxy_nvidia()
            return
        self._send_json(404, {'error': 'Not found.'})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def _proxy_nvidia(self):
        try:
            content_length = int(self.headers.get('Content-Length', '0'))
            body = self.rfile.read(content_length) if content_length > 0 else b'{}'
            payload = json.loads(body.decode('utf-8') or '{}')

            upstream_headers = {
                'Authorization': self.headers.get('Authorization', ''),
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream'
            }
            upstream_headers = {k: v for k, v in upstream_headers.items() if v}

            request = urllib.request.Request(
                'https://integrate.api.nvidia.com/v1/chat/completions',
                data=body,
                headers=upstream_headers,
                method='POST'
            )

            with urllib.request.urlopen(request, timeout=120) as upstream:
                status = int(getattr(upstream, 'status', 200))
                content_type = upstream.headers.get_content_type() or 'text/event-stream'

                self.send_response(status)
                self.send_header('Content-Type', content_type)
                self.send_header('Cache-Control', 'no-cache, no-transform')
                self.send_header('Connection', 'keep-alive')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept')
                self.end_headers()

                while True:
                    chunk = upstream.read(8192)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except Exception as exc:
            try:
                message = str(exc)
                self.send_response(502)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'NVIDIA proxy failed', 'details': message}).encode('utf-8'))
            except Exception:
                pass

    def _serve_static(self):
        path = self.path.split('?', 1)[0]
        if path in ('', '/'):
            file_path = ROOT / 'index.html'
        else:
            file_path = ROOT / path.lstrip('/')

        if not file_path.exists() or file_path.is_dir():
            file_path = ROOT / 'index.html'

        try:
            data = file_path.read_bytes()
            content_type = 'text/html; charset=utf-8'
            if file_path.suffix == '.css':
                content_type = 'text/css; charset=utf-8'
            elif file_path.suffix in ('.js', '.mjs'):
                content_type = 'application/javascript; charset=utf-8'
            elif file_path.suffix == '.json':
                content_type = 'application/json; charset=utf-8'

            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)
        except Exception:
            self._send_json(404, {'error': 'Not found.'})

    def _send_json(self, status_code, payload):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, Accept')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def main():
    host = '127.0.0.1'
    port = int(os.environ.get('PORT', '3000'))
    server = ThreadingHTTPServer((host, port), ProxyHandler)
    print(f'Serving on http://{host}:{port}')
    server.serve_forever()


if __name__ == '__main__':
    main()
