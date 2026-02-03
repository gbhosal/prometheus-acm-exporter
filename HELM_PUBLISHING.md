# Quick Start: Publishing Helm Chart

> For a longer guide with manual publishing, OCI, and troubleshooting, see [docs/helm-repository.md](docs/helm-repository.md).

## 🚀 Quick Setup (5 minutes)

### Step 1: Enable GitHub Pages

1. Go to your GitHub repository
2. Navigate to **Settings** → **Pages**
3. Under **Source**, select:
   - **Branch**: `gh-pages`
   - **Folder**: `/ (root)`
4. Click **Save**

> Note: The `gh-pages` branch will be created automatically by the GitHub Actions workflow.

### Step 2: Push the Workflow

The GitHub Actions workflow is already created at `.github/workflows/publish-helm-chart.yml`. Just commit and push:

```bash
git add .github/workflows/publish-helm-chart.yml
git commit -m "Add Helm chart publishing workflow"
git push
```

### Step 3: Trigger the Workflow

The workflow will automatically run when:
- You push changes to `main`/`master` that modify Helm chart files
- You create a GitHub release
- You manually trigger it via **Actions** → **Publish Helm Chart** → **Run workflow**

### Step 4: Verify Publishing

After the workflow completes (check the Actions tab):

1. **Check the repository URL**: 
   ```
   https://<your-username>.github.io/prometheus-acm-exporter/charts/index.yaml
   ```

2. **Test adding the repository**:
   ```bash
   helm repo add prometheus-acm-exporter https://<your-username>.github.io/prometheus-acm-exporter/charts
   helm repo update
   helm search repo prometheus-acm-exporter
   ```

### Step 5: Update Chart Version (Before Each Release)

Before publishing a new version:

1. Update `helm/prometheus-acm-exporter/Chart.yaml`:
   ```yaml
   version: 0.1.1  # Increment version (must be unique and higher than previous)
   appVersion: "1.0.0"  # Update if application version changed
   ```

2. Commit and push:
   ```bash
   git add helm/prometheus-acm-exporter/Chart.yaml
   git commit -m "Bump chart version to 0.1.1"
   git push
   ```

3. The workflow will automatically:
   - Package the new version
   - Merge it with existing versions (preserving all previous versions)
   - Update the index.yaml to include the new version
   - Publish to GitHub Pages

**Important:** All chart versions are preserved. Users can install any version they need.

## 📦 Using Your Published Chart

Once published, anyone can use your chart:

```bash
# Add repository
helm repo add prometheus-acm-exporter https://<your-username>.github.io/prometheus-acm-exporter/charts

# Update
helm repo update

# Install latest version
helm install my-release prometheus-acm-exporter/prometheus-acm-exporter \
  --set config.regions[0]=us-east-1

# Install specific version
helm install my-release prometheus-acm-exporter/prometheus-acm-exporter \
  --version 0.1.0 \
  --set config.regions[0]=us-east-1

# List all available versions
helm search repo prometheus-acm-exporter/prometheus-acm-exporter --versions
```

## 🔍 Troubleshooting

### Workflow fails with "Permission denied"
- Ensure GitHub Pages is enabled in repository settings
- Check that Actions have write permissions (Settings → Actions → General → Workflow permissions)

### Chart not found after adding repo
- Run `helm repo update` after adding
- Verify the URL: `https://<username>.github.io/<repo-name>/charts/index.yaml` is accessible
- Check the Actions tab to ensure the workflow completed successfully

### GitHub Pages not updating
- Check the `gh-pages` branch exists and has the `charts/` directory
- Verify the workflow completed successfully in the Actions tab
- Wait a few minutes for GitHub Pages to rebuild

## 📚 More Information

For detailed information, see [docs/helm-repository.md](docs/helm-repository.md)

## 🎯 Next Steps

1. ✅ Enable GitHub Pages
2. ✅ Push the workflow file
3. ✅ Test the workflow
4. ✅ Share your repository URL with users
5. (Optional) Submit to [Artifact Hub](https://artifacthub.io/) for discovery
