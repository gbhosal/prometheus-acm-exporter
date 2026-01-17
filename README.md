# Prometheus ACM Certificate Exporter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Prometheus exporter for AWS Certificate Manager (ACM) that collects certificate expiration metrics across multiple regions and exposes them for monitoring and alerting.

## Features

- **Multi-Region Support**: Collect certificates from multiple AWS regions in a single exporter instance
- **Comprehensive Metrics**: Track certificate expiration, type, renewal eligibility, and export options
- **Tag Filtering**: Selectively include ACM certificate tags as Prometheus labels
- **Role Assumption**: Support for cross-account access via IAM role assumption
- **Kubernetes Ready**: Includes Helm chart for easy deployment
- **Lightweight Health Checks**: Efficient `/health` endpoint for container health checks
- **Pagination Support**: Automatically handles pagination for accounts with many certificates
- **Multi-Architecture Support**: Docker images support both x86_64 (amd64) and ARM64 architectures

## Quick Start

### Docker

#### Using Published Image (Recommended)

Pull and run the published image from GitHub Container Registry:

```bash
# Pull the image (replace <owner> with your GitHub username/organization)
docker pull ghcr.io/<owner>/prometheus-acm-exporter:latest

# Run the container
docker run -p 9102:9102 \
  -v /path/to/config.yaml:/config/prometheus-acm-exporter.yaml \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  ghcr.io/<owner>/prometheus-acm-exporter:latest
```

> **Note**: Images are automatically published to GHCR when GitHub releases are created. See [Docker Publishing Guide](docs/docker-publishing.md) for details.

#### Building Locally

To build the image locally:

```bash
docker build -t prometheus-acm-exporter:latest .
docker run -p 9102:9102 \
  -v /path/to/config.yaml:/config/prometheus-acm-exporter.yaml \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  prometheus-acm-exporter:latest
```

### Kubernetes/Helm

#### Using the Helm Chart from Repository

```bash
# Add the Helm repository (after publishing)
helm repo add prometheus-acm-exporter https://<your-username>.github.io/prometheus-acm-exporter/charts
helm repo update

# Install from repository
helm install my-release prometheus-acm-exporter/prometheus-acm-exporter \
  --set config.regions[0]=us-east-1 \
  --set config.regions[1]=us-east-2
```

#### Using the Local Helm Chart

```bash
helm install prometheus-acm-exporter ./helm/prometheus-acm-exporter \
  --set config.regions[0]=us-east-1 \
  --set config.regions[1]=us-east-2
```

> **Note**: See [docs/helm-repository.md](docs/helm-repository.md) for instructions on publishing the Helm chart to a repository.

### Local Development

```bash
pip install -r requirements.txt
python -m src.acm_exporter --config examples/config.yaml
```

## Installation

See [docs/installation.md](docs/installation.md) for detailed installation instructions.

## Configuration

The exporter is configured via a YAML file. See [docs/configuration.md](docs/configuration.md) for all configuration options.

### Example Configuration

```yaml
# Single region (backward compatible)
region: us-east-2

# Multiple regions
regions:
  - us-east-1
  - us-east-2
  - us-west-2

# Port for metrics server (can also be set via PORT environment variable)
port: 9102

# AWS Role Assumption (optional)
aws-assume-role-arn: arn:aws:iam::123456789012:role/PrometheusACMRole
aws-assume-role-session: prometheus-acm-exporter

# Selected Tags (optional - if not provided, all tags are included)
selected-tags:
  - Environment
  - APPACCESS
  - COSTCENTER
  - GROUP
```

## Metrics

The exporter exposes the following metric:

### `acm_certificate_expiry_duration_days`

The number of days until an ACM certificate expires.

**Labels:**
- `region`: AWS region where the certificate is located
- `aws_account`: AWS account ID
- `certificate_id`: ACM certificate ID
- `domain`: Certificate domain name
- `type`: Certificate type (AMAZON_ISSUED, IMPORTED, PRIVATE)
- `renewal_eligibility`: Renewal eligibility status (ELIGIBLE, INELIGIBLE)
- `export_option`: Export option (EXPORTED, NOT_EXPORTED)
- `tags_*`: Dynamic labels for selected ACM certificate tags (prefixed with `tags_`)

**Example:**
```
acm_certificate_expiry_duration_days{
  aws_account="123456789012",
  certificate_id="abc123-def456-ghi789",
  domain="example.com",
  region="us-east-1",
  type="AMAZON_ISSUED",
  renewal_eligibility="ELIGIBLE",
  export_option="NOT_EXPORTED",
  tags_Environment="production",
  tags_APPACCESS="myapp"
} 45.0
```

## Endpoints

- `/metrics`: Prometheus metrics endpoint
- `/health`: Health check endpoint (returns 200 OK)

## AWS IAM Permissions

The exporter requires the following IAM permissions:

- `acm:ListCertificates`
- `acm:ListTagsForCertificate`
- `sts:GetCallerIdentity`
- `sts:AssumeRole` (if using role assumption)

## Development

See [docs/development.md](docs/development.md) for development setup and guidelines.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [Installation Guide](docs/installation.md)
- [Configuration Reference](docs/configuration.md)
- [Development Guide](docs/development.md)
- [Helm Chart Documentation](helm/prometheus-acm-exporter/README.md)
