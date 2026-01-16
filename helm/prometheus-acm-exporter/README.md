# Prometheus ACM Exporter Helm Chart

This Helm chart deploys the Prometheus ACM Certificate Exporter to Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Prometheus Operator (for ServiceMonitor support)

## Installation

### Basic Installation

```bash
helm install prometheus-acm-exporter ./helm/prometheus-acm-exporter \
  --set config.region=us-east-2
```

### Installation with AWS Role Assumption

```bash
helm install prometheus-acm-exporter ./helm/prometheus-acm-exporter \
  --set config.region=us-east-2 \
  --set config.awsAssumeRoleArn=arn:aws:iam::123456789012:role/PrometheusACMRole \
  --set config.awsAssumeRoleSession=prometheus-acm-exporter
```

### Installation with Custom Values

```bash
helm install prometheus-acm-exporter ./helm/prometheus-acm-exporter \
  -f custom-values.yaml
```

## Configuration

The following table lists the configurable parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Container image repository | `prometheus-acm-exporter` |
| `image.tag` | Container image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `serviceAccount.create` | Create service account | `true` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `9102` |
| `config.region` | AWS region | `""` |
| `config.port` | Metrics server port | `9102` |
| `config.awsAssumeRoleArn` | AWS role ARN to assume | `""` |
| `config.awsAssumeRoleSession` | AWS role session name | `prometheus-acm-exporter` |
| `serviceMonitor.enabled` | Enable ServiceMonitor | `true` |
| `serviceMonitor.interval` | Scrape interval | `30s` |
| `serviceMonitor.scrapeTimeout` | Scrape timeout | `10s` |
| `resources.limits.cpu` | CPU limit | `200m` |
| `resources.limits.memory` | Memory limit | `256Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |

## AWS IAM Permissions

The service account or IAM role needs the following permissions:

- `acm:ListCertificates`
- `acm:ListTagsForCertificate`
- `sts:GetCallerIdentity`
- `sts:AssumeRole` (if using role assumption)

## ServiceMonitor

The chart includes a ServiceMonitor resource for Prometheus Operator. Make sure to configure the `serviceMonitor.selector` labels to match your Prometheus instance's serviceMonitorSelector.

Example:
```yaml
serviceMonitor:
  enabled: true
  selector:
    release: prometheus
```

## Building the Docker Image

```bash
docker build -t prometheus-acm-exporter:latest .
```

## Uninstallation

```bash
helm uninstall prometheus-acm-exporter
```
