import argparse
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
    
    # Get port from config or use default
    port = config.get('port', 9102)
    
    # Create collector
    collector = ACMCertificateCollector(config=config)
    
    # Start server
    start_server(port, collector)


if __name__ == "__main__":
    main()
