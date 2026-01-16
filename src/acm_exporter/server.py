from http.server import HTTPServer, BaseHTTPRequestHandler
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST


class MetricsHandler(BaseHTTPRequestHandler):
    """Custom HTTP handler for metrics and health endpoints."""
    
    def do_GET(self):
        if self.path == '/health' or self.path == '/healthz':
            # Simple health check endpoint
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        elif self.path == '/metrics':
            # Prometheus metrics endpoint
            self.send_response(200)
            self.send_header('Content-type', CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(generate_latest(REGISTRY))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        # Suppress default logging for health checks
        if self.path not in ['/health', '/healthz']:
            super().log_message(format, *args)


def start_server(port, collector):
    """Start the HTTP server with metrics and health endpoints."""
    # Register the custom collector with Prometheus
    REGISTRY.register(collector)
    
    # Start a custom HTTP server with metrics and health endpoints
    httpd = HTTPServer(('', port), MetricsHandler)
    print(f"ACM Exporter is running on port {port}")
    print(f"  - Metrics: http://localhost:{port}/metrics")
    print(f"  - Health: http://localhost:{port}/health")
    
    # Keep the process alive indefinitely
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        httpd.shutdown()
