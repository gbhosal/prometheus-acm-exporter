import argparse
import os
from .collector import ACMCertificateCollector, load_config
from .server import start_server


def main():
    """Main entry point for the ACM Prometheus Exporter."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Prometheus ACM Certificate Exporter')
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration YAML file (default: /config/prometheus-acm-exporter.yaml)'
    )
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(config_path=args.config)
    
    # Get port from environment variable, config file, or use default
    # Priority: PORT env var > config file > default (9102)
    port = 9102  # Default port
    port_source = "default"
    
    if 'PORT' in os.environ:
        try:
            port = int(os.environ['PORT'])
            port_source = "PORT environment variable"
        except ValueError:
            raise ValueError(f"Invalid PORT environment variable value: {os.environ['PORT']}. Must be a valid integer.")
    elif 'port' in config:
        port = config.get('port')
        port_source = "config file"
    
    # Log port source for debugging (logging will be configured in start_server)
    print(f"Using port {port} (from {port_source})")
    
    # Create collector
    collector = ACMCertificateCollector(config=config)
    
    # Start server
    start_server(port, collector)


if __name__ == "__main__":
    main()
