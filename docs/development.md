# Development Guide

This guide helps you set up a development environment for the Prometheus ACM Certificate Exporter.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- pip
- Git
- AWS credentials (for testing)
- Docker (optional, for testing container builds)

### Initial Setup

1. **Clone the repository** (if contributing, fork the repo first and use your fork’s URL instead):
```bash
git clone https://github.com/gbhosal/prometheus-acm-exporter.git
cd prometheus-acm-exporter
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install development dependencies (if any):**
```bash
pip install -r requirements-dev.txt  # If you create one
```

## Project Structure

```
acm-prometheus-exporter/
├── src/
│   └── acm_exporter/
│       ├── __init__.py      # Main entry point
│       ├── collector.py     # ACMCertificateCollector class
│       └── server.py        # HTTP server and handler
├── examples/
│   └── config.yaml          # Example configuration
├── docs/                     # Documentation
├── tests/                    # Test files
├── helm/                     # Helm chart
└── Dockerfile               # Container build file
```

## Running Locally

### Basic Run

```bash
python -m src.acm_exporter --config examples/config.yaml
```

### With Custom Config

```bash
python -m src.acm_exporter --config /path/to/your/config.yaml
```

## Code Structure

### `src/acm_exporter/collector.py`

Contains the `ACMCertificateCollector` class which:
- Initializes AWS clients for configured regions
- Collects ACM certificate data
- Processes and groups certificates
- Yields Prometheus metrics

### `src/acm_exporter/server.py`

Contains the HTTP server components:
- `MetricsHandler`: Handles `/metrics` and `/health` endpoints
- `start_server()`: Starts the HTTP server

### `src/acm_exporter/__init__.py`

Main entry point that:
- Parses command-line arguments
- Loads configuration
- Creates the collector
- Starts the server

## Testing

### Manual Testing

1. **Set up AWS credentials:**
```bash
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_REGION=us-east-1
```

2. **Create a test config:**
```yaml
regions:
  - us-east-1
port: 9102  # Can also be set via PORT environment variable
```

3. **Run the exporter:**
```bash
# Using config file
python -m src.acm_exporter --config test-config.yaml

# Or using PORT environment variable (takes precedence)
export PORT=8080
python -m src.acm_exporter --config test-config.yaml
```

4. **Test endpoints:**
```bash
# Default port 9102, or use PORT env var value
curl http://localhost:9102/health  # or /healthz
curl http://localhost:9102/metrics
```

**Note:** Only certificates with status `ISSUED` will appear in metrics. Certificates in other states are excluded.

### Unit Testing

Create test files in the `tests/` directory:

```python
# tests/test_collector.py
import unittest
from src.acm_exporter.collector import ACMCertificateCollector

class TestCollector(unittest.TestCase):
    def test_initialization(self):
        # Test collector initialization
        pass
```

Run tests:
```bash
python -m pytest tests/
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to all functions and classes
- Maximum line length: 100 characters
- Use meaningful variable names

## Building Docker Image

```bash
docker build -t prometheus-acm-exporter:dev .
```

Test the image:
```bash
# Using default port
docker run -p 9102:9102 \
  -v $(pwd)/examples/config.yaml:/config/prometheus-acm-exporter.yaml \
  prometheus-acm-exporter:dev

# Using custom port via environment variable
docker run -p 8080:8080 \
  -e PORT=8080 \
  -v $(pwd)/examples/config.yaml:/config/prometheus-acm-exporter.yaml \
  prometheus-acm-exporter:dev
```

## Debugging

### Enable Verbose Logging

Add print statements or use Python's logging module:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test with Mock Data

Create mock AWS responses for testing without actual AWS access:

```python
from unittest.mock import Mock, patch

@patch('boto3.client')
def test_collector(mock_client):
    # Mock AWS responses
    pass
```

## Common Development Tasks

### Adding a New Metric

1. Update `collector.py` to collect the new data
2. Add the metric to `GaugeMetricFamily` or create a new one
3. Update documentation
4. Add tests

### Adding a New Configuration Option

1. Update `load_config()` in `collector.py`
2. Update `ACMCertificateCollector.__init__()` to use the option
3. Update `docs/configuration.md`
4. Update `examples/config.yaml`
5. Update Helm chart `values.yaml` if applicable

### Modifying Helm Chart

1. Edit files in `helm/prometheus-acm-exporter/`
2. Test with `helm template`:
```bash
helm template test ./helm/prometheus-acm-exporter
```
3. Test installation in a test cluster
4. Update `helm/prometheus-acm-exporter/README.md`

## Submitting Changes

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Update documentation
5. Ensure code follows style guidelines
6. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for more details.

## Resources

- [Prometheus Client Library](https://github.com/prometheus/client_python)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS ACM API Reference](https://docs.aws.amazon.com/acm/latest/APIReference/)
