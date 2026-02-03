# Publishing Helm Chart to Repository

This guide explains how to publish the Prometheus ACM Exporter Helm chart to a Helm repository. For a short quick start, see [HELM_PUBLISHING.md](../HELM_PUBLISHING.md).

## Option 1: GitHub Pages (Recommended - Free & Automated)

GitHub Pages is the easiest and most common way to host a Helm repository for public GitHub repositories.

### Prerequisites

- GitHub repository (public or private with GitHub Pages enabled)
- GitHub Actions enabled for your repository

### Automated Publishing (Recommended)

We've set up a GitHub Actions workflow (`.github/workflows/publish-helm-chart.yml`) that automatically:

1. Lints the Helm chart
2. Packages the chart
3. Merges with existing `index.yaml` to preserve all versions
4. Publishes to GitHub Pages

**Version Management:**
- All chart versions are preserved in the repository
- Each new release adds to the existing versions (doesn't replace them)
- Users can install specific versions or use the latest
- The `index.yaml` file maintains a complete history of all published versions

#### Setup Steps:

1. **Enable GitHub Pages**:
   - Go to your repository → Settings → Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages` (will be created automatically)
   - Folder: `/ (root)`
   - Click Save

2. **Push the workflow file** (already created):
   ```bash
   git add .github/workflows/publish-helm-chart.yml
   git commit -m "Add Helm chart publishing workflow"
   git push
   ```

3. **Trigger the workflow**:
   - The workflow runs automatically on pushes to `main`/`master` that change Helm files
   - Or manually trigger via: Actions → Publish Helm Chart → Run workflow

4. **Verify**:
   - After the workflow completes, check: `https://<your-username>.github.io/<repo-name>/charts/index.yaml`
   - You should see the chart index

### Manual Publishing (Alternative)

If you prefer to publish manually:

```bash
# Package the chart
helm package helm/prometheus-acm-exporter --destination ./charts

# Create/update index
helm repo index ./charts --url https://<your-username>.github.io/<repo-name>/charts

# Commit and push to gh-pages branch
git checkout --orphan gh-pages
git add charts/
git commit -m "Publish Helm chart"
git push origin gh-pages
```

### Using the Published Chart

Once published, users can add your repository:

```bash
# Add the repository
helm repo add prometheus-acm-exporter https://<your-username>.github.io/<repo-name>/charts

# Update repository index
helm repo update

# Install the latest version
helm install my-release prometheus-acm-exporter/prometheus-acm-exporter

# Install a specific version
helm install my-release prometheus-acm-exporter/prometheus-acm-exporter --version 0.1.0

# List all available versions
helm search repo prometheus-acm-exporter/prometheus-acm-exporter --versions
```

## Option 2: OCI Registry (Modern Approach)

Helm 3.8+ supports OCI registries (like Docker registries) for storing charts.

### Publishing to OCI Registry

```bash
# Login to your OCI registry (e.g., GHCR, Docker Hub, etc.)
helm registry login <registry-url>

# Package and push
helm package helm/prometheus-acm-exporter
helm push prometheus-acm-exporter-*.tgz oci://<registry-url>/<namespace>
```

### Using from OCI Registry

```bash
helm install my-release oci://<registry-url>/<namespace>/prometheus-acm-exporter --version <version>
```

## Option 3: ChartMuseum (Self-Hosted)

ChartMuseum is a Helm chart repository server.

### Using ChartMuseum

```bash
# Install ChartMuseum (example with Docker)
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/charts:/charts \
  chartmuseum/chartmuseum:latest \
  --storage=local \
  --storage-local-rootdir=/charts

# Add repository
helm repo add chartmuseum http://localhost:8080

# Push chart
curl --data-binary "@prometheus-acm-exporter-0.1.0.tgz" http://localhost:8080/api/charts
```

## Option 4: Artifact Hub (For Discovery)

Artifact Hub is a web-based application that helps you find, install and publish packages and configurations for CNCF projects, including Helm charts.

### Publishing to Artifact Hub

1. **Ensure your chart is published** (GitHub Pages, OCI, etc.)

2. **Add Artifact Hub annotation** to your `Chart.yaml`:
   ```yaml
   annotations:
     artifacthub.io/changes: |
       - Initial release
     artifacthub.io/images: |
       - name: prometheus-acm-exporter
         image: <your-image>:<tag>
   ```

3. **Submit your repository**:
   - Go to https://artifacthub.io/
   - Sign in with GitHub
   - Click "Add repository"
   - Provide your Helm repository URL

## Versioning Best Practices

1. **Semantic Versioning**: Follow semver (MAJOR.MINOR.PATCH)
   - MAJOR: Breaking changes
   - MINOR: New features (backward compatible)
   - PATCH: Bug fixes

2. **Update Chart.yaml**: Always update the `version` field in `Chart.yaml` before publishing
   - Each version must be unique
   - Versions cannot be downgraded (Helm requirement)
   - Once published, a version cannot be republished

3. **Multiple Versions**: The workflow automatically preserves all versions
   - Old versions remain available for users who need them
   - New versions are added without removing old ones
   - The `index.yaml` file tracks all versions

4. **Tag Releases**: Create GitHub releases for chart versions:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```

5. **Version History**: View all published versions:
   ```bash
   # After adding the repo
   helm search repo prometheus-acm-exporter/prometheus-acm-exporter --versions
   ```

### Managing Multiple Chart Versions

The workflow automatically manages multiple chart versions:

- **First Release**: Creates initial `index.yaml` and publishes the chart
- **Subsequent Releases**: 
  - Merges new chart package with existing packages
  - Updates `index.yaml` to include the new version
  - Preserves all previous versions
  - All `.tgz` files are kept in the `charts/` directory

**Example version history:**
```
charts/
  ├── prometheus-acm-exporter-0.1.0.tgz
  ├── prometheus-acm-exporter-0.1.1.tgz
  ├── prometheus-acm-exporter-0.2.0.tgz
  └── index.yaml  (contains metadata for all versions)
```

**Users can install any version:**
```bash
# Install latest
helm install my-release prometheus-acm-exporter/prometheus-acm-exporter

# Install specific version
helm install my-release prometheus-acm-exporter/prometheus-acm-exporter --version 0.1.0

# Upgrade to newer version
helm upgrade my-release prometheus-acm-exporter/prometheus-acm-exporter --version 0.2.0
```

## Troubleshooting

### GitHub Pages not updating
- Check GitHub Actions workflow logs
- Verify GitHub Pages is enabled in repository settings
- Ensure `gh-pages` branch exists and has content

### Chart not found after adding repo
- Run `helm repo update` after adding
- Verify the repository URL is correct
- Check that `index.yaml` exists at the repository URL

### Authentication issues
- For private repositories, use GitHub Personal Access Token
- For OCI registries, ensure you're logged in

## Repository URL Examples

After publishing, your repository URL will be:
- **GitHub Pages**: `https://<username>.github.io/<repo-name>/charts`
- **GitHub Pages (custom domain)**: `https://charts.yourdomain.com`
- **OCI (GHCR)**: `ghcr.io/<username>/charts`
- **OCI (Docker Hub)**: `docker.io/<username>/charts`

## Next Steps

1. ✅ Set up GitHub Pages
2. ✅ Push the workflow file
3. ✅ Test the workflow
4. ✅ Update Chart.yaml version
5. ✅ Create a GitHub release
6. ✅ (Optional) Submit to Artifact Hub
