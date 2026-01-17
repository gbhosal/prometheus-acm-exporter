from http.server import HTTPServer, BaseHTTPRequestHandler
from prometheus_client import REGISTRY, generate_latest, CONTENT_TYPE_LATEST
import logging

logger = logging.getLogger(__name__)


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
        # Suppress all HTTP access logs
        pass


def start_server(port, collector):
    """Start the HTTP server with metrics and health endpoints."""
    # Configure logging for troubleshooting
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Register the custom collector with Prometheus
    try:
        REGISTRY.register(collector)
        logger.info("Registered ACM certificate collector with Prometheus")
    except Exception as e:
        logger.error(f"Failed to register collector: {e}", exc_info=True)
        raise
    
    # Start a custom HTTP server with metrics and health endpoints
    try:
        httpd = HTTPServer(('', port), MetricsHandler)
        logger.info(f"ACM Exporter started successfully on port {port}")
        logger.info(f"  - Metrics endpoint: http://localhost:{port}/metrics")
        logger.info(f"  - Health endpoint: http://localhost:{port}/health")
        print(f"ACM Exporter is running on port {port}")
        print(f"  - Metrics: http://localhost:{port}/metrics")
        print(f"  - Health: http://localhost:{port}/health")
    except Exception as e:
        logger.error(f"Failed to start HTTP server on port {port}: {e}", exc_info=True)
        raise
    
    # Keep the process alive indefinitely
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        print("\nShutting down...")
        httpd.shutdown()
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise