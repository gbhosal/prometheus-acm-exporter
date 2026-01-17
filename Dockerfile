FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and project metadata
COPY pyproject.toml .
COPY src/ ./src/

# Install the package in editable mode
RUN pip install --no-cache-dir -e .

# Create config directory
RUN mkdir -p /config

# Run as non-root user
RUN useradd -m -u 1000 prometheus && \
    chown -R prometheus:prometheus /app /config

USER prometheus

# Expose metrics port
EXPOSE 9102

# Health check - use lightweight /health endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9102/health')" || exit 1

# Run the exporter
# Use ENTRYPOINT so arguments passed to docker run are appended
ENTRYPOINT ["python", "-m", "acm_exporter"]
