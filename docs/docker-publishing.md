# Docker Image Publishing Guide

This guide explains how Docker images for the Prometheus ACM Exporter are built and published to GitHub Container Registry (GHCR).

## Overview

Docker images are automatically built and published to GitHub Container Registry when GitHub releases are created. The publishing process is fully automated via GitHub Actions.

## Image Location

Images are published to:
```
ghcr.io/<owner>/prometheus-acm-exporter
```

Where `<owner>` is your GitHub username or organization name.

## Publishing Process

### Automatic Publishing

Images are automatically published when you create a GitHub release:

1. **Update version numbers** (if needed):
   - Update `version` in `pyproject.toml`
   - Update `version` and `appVersion` in `helm/prometheus-acm-exporter/Chart.yaml`

2. **Commit and push changes**:
   ```bash
   git add pyproject.toml helm/prometheus-acm-exporter/Chart.yaml
   git commit -m "Bump version to 1.0.0"
   git push
   ```

3. **Create and push a Git tag**:
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

4. **Create a GitHub release**:
   - Go to your repository on GitHub
   - Click "Releases" → "Create a new release"
   - Select the tag you just created (e.g., `v1.0.0`)
   - Fill in release title and description
   - Click "Publish release"

5. **GitHub Actions workflow triggers automatically**:
   - The workflow builds the Docker image
   - Publishes it to GHCR with multiple tags:
     - `v1.0.0` (full tag name)
     - `1.0.0` (version without 'v' prefix)
     - `latest` (always points to most recent release)

### Manual Publishing (Alternative)

If you need to build and publish manually:

```bash
# Build the image
docker build -t ghcr.io/<owner>/prometheus-acm-exporter:v1.0.0 .

# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u <username> --password-stdin

# Tag and push
docker tag ghcr.io/<owner>/prometheus-acm-exporter:v1.0.0 \
           ghcr.io/<owner>/prometheus-acm-exporter:latest
docker push ghcr.io/<owner>/prometheus-acm-exporter:v1.0.0
docker push ghcr.io/<owner>/prometheus-acm-exporter:latest
```

## Pulling Images

### Public Images

If your repository is public, images are public by default and can be pulled without authentication:

```bash
docker pull ghcr.io/<owner>/prometheus-acm-exporter:latest
docker pull ghcr.io/<owner>/prometheus-acm-exporter:v1.0.0
```

### Private Images

If your repository is private, you need to authenticate:

1. **Create a Personal Access Token (PAT)**:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate a token with `read:packages` scope

2. **Login to GHCR**:
   ```bash
   echo $GITHUB_TOKEN | docker login ghcr.io -u <username> --password-stdin
   ```

3. **Pull the image**:
   ```bash
   docker pull ghcr.io/<owner>/prometheus-acm-exporter:latest
   ```

### Using in Kubernetes

For Kubernetes deployments, you may need to create an image pull secret:

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<username> \
  --docker-password=<token> \
  --docker-email=<email>
```

Then reference it in your deployment or Helm values:

```yaml
imagePullSecrets:
  - name: ghcr-secret
```

## Versioning Strategy

### Tag Format

Images are tagged with:
- **Full tag**: `v1.0.0` (matches Git tag exactly)
- **Version tag**: `1.0.0` (without 'v' prefix)
- **Latest tag**: `latest` (always points to most recent release)

### Semantic Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality
- **PATCH** version for backwards-compatible bug fixes

Examples:
- `v1.0.0` - Initial release
- `v1.0.1` - Bug fix release
- `v1.1.0` - New feature release
- `v2.0.0` - Breaking change release

## Image Details

### Base Image
- **Base**: `python:3.11-slim`
- **Size**: ~150-200MB (optimized)

### Image Structure
- Application code in `/app`
- Configuration directory at `/config`
- Runs as non-root user (`prometheus`, UID 1000)
- Exposes port `9102` for metrics

### Health Check
The image includes a health check that uses the `/health` endpoint:
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9102/health')" || exit 1
```

## Using Published Images

### Docker Run

```bash
docker run -d \
  --name prometheus-acm-exporter \
  -p 9102:9102 \
  -v /path/to/config.yaml:/config/prometheus-acm-exporter.yaml \
  -e AWS_ACCESS_KEY_ID=your-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret \
  ghcr.io/<owner>/prometheus-acm-exporter:latest
```

### Docker Compose

```yaml
version: '3.8'
services:
  prometheus-acm-exporter:
    image: ghcr.io/<owner>/prometheus-acm-exporter:latest
    ports:
      - "9102:9102"
    volumes:
      - ./config.yaml:/config/prometheus-acm-exporter.yaml
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
```

### Kubernetes/Helm

The Helm chart is configured to use GHCR images by default. Update the repository in `values.yaml`:

```yaml
image:
  repository: ghcr.io/<owner>/prometheus-acm-exporter
  tag: latest
```

Or override during installation:

```bash
helm install prometheus-acm-exporter ./helm/prometheus-acm-exporter \
  --set image.repository=ghcr.io/<owner>/prometheus-acm-exporter \
  --set image.tag=v1.0.0
```

## Troubleshooting

### Workflow fails with "permission denied"
- Ensure the workflow has `packages: write` permission
- Check that `GITHUB_TOKEN` is available (automatically provided)

### Image not found after publishing
- Verify the release was created successfully
- Check the Actions tab to ensure the workflow completed
- Wait a few minutes for GHCR to process the image
- Verify the image name matches your GitHub username/organization

### Authentication issues when pulling
- For private repositories, ensure you have a PAT with `read:packages` scope
- Verify you're logged in: `docker login ghcr.io`
- Check that your token hasn't expired

### Image pull errors in Kubernetes
- Create an image pull secret with your GHCR credentials
- Reference the secret in your deployment or Helm values
- For public images, image pull secrets are not required

## Viewing Published Images

You can view all published images in the GitHub Packages section:
- Go to your repository
- Click "Packages" in the right sidebar
- Or visit: `https://github.com/<owner>?tab=packages`

## Best Practices

1. **Always tag releases**: Use semantic versioning tags (e.g., `v1.0.0`)
2. **Update versions**: Keep `pyproject.toml` and `Chart.yaml` versions in sync
3. **Test before releasing**: Test the image locally before creating a release
4. **Use specific tags in production**: Avoid `latest` tag in production, use version tags
5. **Keep images updated**: Regularly update base images for security patches

## Related Documentation

- [Installation Guide](installation.md)
- [Configuration Reference](configuration.md)
- [Helm Chart Documentation](../helm/prometheus-acm-exporter/README.md)
