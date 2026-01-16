# Installation Guide

This guide covers different methods to install and run the Prometheus ACM Certificate Exporter.

## Prerequisites

- AWS credentials configured (via environment variables, IAM role, or credentials file)
- Python 3.11+ (for local installation)
- Docker (for containerized installation)
- Kubernetes and Helm 3.0+ (for Kubernetes installation)

## Installation Methods

### Docker

#### Build the Image

```bash
docker build -t prometheus-acm-exporter:latest .
```

#### Run the Container

```bash
docker run -d \
  --name acm-exporter \
  -p 9102:9102 \
  -v /path/to/config.yaml:/config/prometheus-acm-exporter.yaml \
  -e AWS_ACCESS_KEY_ID=your-access-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret-key \
  -e AWS_REGION=us-east-1 \
  prometheus-acm-exporter:latest
```

#### Using AWS IAM Role (EC2/ECS)

If running on EC2 or ECS with an IAM role:

```bash
docker run -d \
  --name acm-exporter \
  -p 9102:9102 \
  -v /path/to/config.yaml:/config/prometheus-acm-exporter.yaml \
  prometheus-acm-exporter:latest
```

The container will automatically use the instance's IAM role.

### Kubernetes/Helm

#### Basic Installation

```bash
helm install prometheus-acm-exporter ./helm/prometheus-acm-exporter \
  --set config.region=us-east-2
```

#### Multi-Region Installation

```bash
helm install prometheus-acm-exporter ./helm/prometheus-acm-exporter \
  --set config.regions[0]=us-east-1 \
  --set config.regions[1]=us-east-2 \
  --set config.regions[2]=us-west-2
```

#### With Role Assumption

```bash
helm install prometheus-acm-exporter ./helm/prometheus-acm-exporter \
  --set config.regions[0]=us-east-1 \
  --set config.awsAssumeRoleArn=arn:aws:iam::123456789012:role/PrometheusACMRole \
  --set config.awsAssumeRoleSession=prometheus-acm-exporter
```

#### Using Custom Values File

```bash
helm install prometheus-acm-exporter ./helm/prometheus-acm-exporter \
  -f my-values.yaml
```

See the [Helm chart README](../helm/prometheus-acm-exporter/README.md) for all available configuration options.

### Local Development

#### Using pip

```bash
pip install -r requirements.txt
python -m src.acm_exporter --config examples/config.yaml
```

#### Using Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m src.acm_exporter --config examples/config.yaml
```

## Configuration

Create a configuration file (see `examples/config.yaml` for a template):

```yaml
regions:
  - us-east-1
  - us-east-2
port: 9102
```

## AWS Credentials Setup

### Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=us-east-1
```

### AWS Credentials File

Create `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
```

Create `~/.aws/config`:

```ini
[default]
region = us-east-1
```

### IAM Role (EC2/ECS)

Attach an IAM role to your EC2 instance or ECS task with the required permissions. The exporter will automatically use the role credentials.

## Verification

After installation, verify the exporter is working:

```bash
# Check health endpoint
curl http://localhost:9102/health

# Check metrics endpoint
curl http://localhost:9102/metrics
```

You should see Prometheus metrics output with ACM certificate data.

## Troubleshooting

### Common Issues

1. **No metrics appearing**: Check AWS credentials and IAM permissions
2. **Connection errors**: Verify network connectivity to AWS APIs
3. **Permission denied**: Ensure IAM role/user has required ACM permissions
4. **Config file not found**: Verify the config file path is correct

### Debug Mode

Run with verbose logging to troubleshoot:

```bash
python -m src.acm_exporter --config examples/config.yaml
```

Check the console output for initialization messages and any errors.

## Next Steps

- See [Configuration Reference](configuration.md) for detailed configuration options
- See [Development Guide](development.md) for contributing to the project
