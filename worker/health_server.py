#!/usr/bin/env python3
"""
Lightweight HTTP health check server for Cloud Run.
Runs alongside Celery worker to respond to Cloud Run health probes.
"""
import os
from http.server import HTTPServer, BaseHTTPRequestHandler


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Respond to health check requests"""
        if self.path in ['/', '/health', '/healthz']:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress request logging to keep logs clean"""
        pass


def run_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f'✅ Health check server listening on port {port}')
    server.serve_forever()


if __name__ == '__main__':
    run_server()

