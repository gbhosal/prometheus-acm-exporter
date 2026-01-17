# Prometheus ACM Exporter Helm Chart

This Helm chart deploys the Prometheus ACM Certificate Exporter to Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Prometheus Operator (for ServiceMonitor support)

## Installation

### Basic Installation

```bash
# Update image.repository with your GitHub username/organization
helm install prometheus-acm-exporter ./helm/prometheus-acm-exporter \
  --set image.repository=ghcr.io/<owner>/prometheus-acm-exporter \
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
| `image.repository` | Container image repository | `ghcr.io/<owner>/prometheus-acm-exporter` |
| `image.tag` | Container image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `serviceAccount.create` | Create service account | `true` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `9102` |
| `config.region` | AWS region | `""` |
| `config.port` | Metrics server port | `9102` |
| `config.awsAssumeRoleArn` | AWS role ARN to assume | `""` |
| `config.awsAssumeRoleSession` | AWS role session name | `prometheus-acm-exporter` |
| `env` | Plain environment variables (key-value pairs) | `{}` |
| `envFrom.secretRef` | Load all keys from Secrets as env vars | `[]` |
| `envFrom.configMapRef` | Load all keys from ConfigMaps as env vars | `[]` |
| `envValueFrom` | Individual keys from Secrets/ConfigMaps | `[]` |
| `serviceMonitor.enabled` | Enable ServiceMonitor | `true` |
| `serviceMonitor.interval` | Scrape interval | `30s` |
| `serviceMonitor.scrapeTimeout` | Scrape timeout | `10s` |
| `resources.limits.cpu` | CPU limit | `200m` |
| `resources.limits.memory` | Memory limit | `256Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |

## Environment Variables

The Helm chart supports flexible and secure injection of environment variables into the container. This is useful for AWS credentials, custom configuration, or any other environment-specific settings.

### Method 1: Plain Environment Variables

For non-sensitive configuration values:

```yaml
env:
  AWS_REGION: us-east-1
  LOG_LEVEL: INFO
  PORT: 8080  # Overrides config.port if set (takes precedence)
  CUSTOM_SETTING: value
```

**Note:** The `PORT` environment variable takes precedence over the `config.port` setting. This is useful for containerized deployments where you want to configure the port without modifying the config file.

### Method 2: Environment Variables from Secrets (envFrom)

Load all keys from a Secret as environment variables:

```yaml
envFrom:
  secretRef:
    - name: aws-credentials
      optional: false
```

This will load all keys from the `aws-credentials` Secret as environment variables.

### Method 3: Environment Variables from ConfigMaps (envFrom)

Load all keys from a ConfigMap as environment variables:

```yaml
envFrom:
  configMapRef:
    - name: app-config
      optional: false
```

### Method 4: Individual Secret/ConfigMap Keys (valueFrom)

Reference specific keys from Secrets or ConfigMaps:

```yaml
envValueFrom:
  - name: AWS_ACCESS_KEY_ID
    secretKeyRef:
      name: aws-credentials
      key: access-key-id
      optional: false
  - name: AWS_SECRET_ACCESS_KEY
    secretKeyRef:
      name: aws-credentials
      key: secret-access-key
      optional: false
  - name: AWS_SESSION_TOKEN
    secretKeyRef:
      name: aws-credentials
      key: session-token
      optional: true
  - name: CONFIG_VALUE
    configMapKeyRef:
      name: app-config
      key: config-key
      optional: false
```

### Complete Example: Using AWS Credentials from a Secret

1. Create a Secret with AWS credentials:

```bash
kubectl create secret generic aws-credentials \
  --from-literal=AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE \
  --from-literal=AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
  --from-literal=AWS_SESSION_TOKEN=optional-session-token
```

2. Configure the Helm chart to use the Secret:

```yaml
envFrom:
  secretRef:
    - name: aws-credentials
      optional: false
```

Or use individual keys:

```yaml
envValueFrom:
  - name: AWS_ACCESS_KEY_ID
    secretKeyRef:
      name: aws-credentials
      key: AWS_ACCESS_KEY_ID
  - name: AWS_SECRET_ACCESS_KEY
    secretKeyRef:
      name: aws-credentials
      key: AWS_SECRET_ACCESS_KEY
```

### Example: Using IRSA (IAM Roles for Service Accounts)

If using IRSA, you typically don't need to inject AWS credentials. Instead, annotate the service account:

```yaml
serviceAccount:
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/prometheus-acm-exporter-role
```

### Security Best Practices

1. **Never use plain environment variables for secrets** - Always use Secrets
2. **Use IRSA when possible** - Prefer IAM Roles for Service Accounts over static credentials
3. **Set `optional: false` for required secrets** - This ensures the pod fails fast if secrets are missing
4. **Use specific keys with `valueFrom`** - Instead of loading entire secrets, reference only the keys you need
5. **Rotate credentials regularly** - Update secrets periodically for better security

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

## Container Image

### Using Published Images (Recommended)

The chart is configured to use images published to GitHub Container Registry (GHCR). Images are automatically published when GitHub releases are created.

**Default image location:**
```
ghcr.io/<owner>/prometheus-acm-exporter:latest
```

Replace `<owner>` with your GitHub username or organization name.

**Multi-Architecture Support:**
Images are built for both `linux/amd64` (x86_64) and `linux/arm64` (ARM64) architectures. Docker and Kubernetes will automatically select the correct image for your node's architecture.

**Using a specific version:**
```yaml
image:
  repository: ghcr.io/<owner>/prometheus-acm-exporter
  tag: v1.0.0  # or 1.0.0, or latest
```

**Using a different registry:**
```yaml
image:
  repository: your-registry.com/prometheus-acm-exporter
  tag: latest
```

### Building the Docker Image Locally

To build the image locally for development:

```bash
docker build -t prometheus-acm-exporter:latest .
```

For production, use the published images from GHCR. See [Docker Publishing Guide](../../docs/docker-publishing.md) for details on the publishing process.

## Uninstallation

```bash
helm uninstall prometheus-acm-exporter
```
