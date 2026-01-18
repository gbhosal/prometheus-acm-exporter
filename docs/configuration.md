# Configuration Reference

This document describes all configuration options available for the Prometheus ACM Certificate Exporter.

## Configuration File

The exporter is configured via a YAML file. By default, it looks for `/config/prometheus-acm-exporter.yaml`, but you can specify a custom path using the `--config` command-line argument.

**Important:** The exporter only collects certificates with status `ISSUED`. Certificates in other states (PENDING_VALIDATION, VALIDATION_TIMED_OUT, REVOKED, FAILED, etc.) are not included in the metrics.

## Configuration Options

### `region` (string, optional)

Single AWS region to collect certificates from. For backward compatibility, this option is still supported.

**Example:**
```yaml
region: us-east-2
```

**Note:** If both `region` and `regions` are specified, `regions` takes precedence.

### `regions` (list, optional)

List of AWS regions to collect certificates from. If not specified, falls back to `region` or default region.

**Example:**
```yaml
regions:
  - us-east-1
  - us-east-2
  - us-west-2
  - eu-west-1
```

### `port` (integer, optional)

Port number for the metrics HTTP server. Defaults to `9102`.

**Note:** The `PORT` environment variable takes precedence over the config file setting. If `PORT` is set, it will be used instead of the `port` value in the config file.

**Priority order:**
1. `PORT` environment variable (highest priority)
2. `port` in config file
3. Default value `9102` (lowest priority)

**Example (config file):**
```yaml
port: 9102
```

**Example (environment variable):**
```bash
export PORT=8080
python -m src.acm_exporter
```

### `aws-assume-role-arn` (string, optional)

ARN of the IAM role to assume for cross-account access. If not specified, uses the current AWS credentials.

**Example:**
```yaml
aws-assume-role-arn: arn:aws:iam::123456789012:role/PrometheusACMRole
```

### `aws-assume-role-session` (string, optional)

Session name for the assumed role. Defaults to `prometheus-acm-exporter`.

**Example:**
```yaml
aws-assume-role-session: prometheus-acm-exporter
```

### `selected-tags` (list, optional)

List of ACM certificate tag keys to include as Prometheus labels. Tag keys should match exactly as they appear in AWS (case-sensitive). If not specified, all tags with non-empty values are included.

**Example:**
```yaml
selected-tags:
  - Environment
  - APPACCESS
  - COSTCENTER
  - GROUP
```

**Note:** Only tags with non-empty values are included in metrics, regardless of this setting.

## Complete Configuration Example

```yaml
# Multiple regions
regions:
  - us-east-1
  - us-east-2
  - us-west-2

# Port for metrics server
port: 9102

# AWS Role Assumption (optional)
aws-assume-role-arn: arn:aws:iam::123456789012:role/PrometheusACMRole
aws-assume-role-session: prometheus-acm-exporter

# Selected Tags (optional)
selected-tags:
  - Environment
  - APPACCESS
  - COSTCENTER
  - GROUP
```

## Command-Line Arguments

### `--config` (string, optional)

Path to the configuration YAML file. If not specified, defaults to `/config/prometheus-acm-exporter.yaml`.

**Example:**
```bash
python -m src.acm_exporter --config /path/to/custom-config.yaml
```

## Environment Variables

The exporter uses standard AWS SDK environment variables for credentials:

- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_SESSION_TOKEN`: AWS session token (for temporary credentials)
- `AWS_REGION`: Default AWS region (used if no region specified in config)

## Configuration Precedence

1. Command-line arguments (`--config`)
2. Environment variables (`PORT` for port, AWS credentials for authentication)
3. Configuration file settings
4. Default values

**Specific precedence for port:**
- `PORT` environment variable (highest priority)
- `port` in config file
- Default: `9102`

## Multi-Region Configuration

When configuring multiple regions, the exporter will:

1. Create ACM clients for each region
2. Collect certificates from all regions in parallel
3. Include the `region` label in all metrics to identify the source region
4. Continue collecting from other regions if one region fails

**Example:**
```yaml
regions:
  - us-east-1
  - us-east-2
  - us-west-2
```

This will collect certificates from all three regions and expose them with the appropriate `region` label.

## Tag Filtering

The `selected-tags` option allows you to control which ACM certificate tags are included as Prometheus labels. This helps:

- Reduce label cardinality
- Focus on relevant tags
- Improve query performance

**Important Notes:**
- Tag keys are case-sensitive and must match exactly as they appear in AWS
- Only tags with non-empty values are included
- Tags are prefixed with `tags_` in the metric labels
- Tag keys are normalized (hyphens replaced with underscores)

## Role Assumption

When using `aws-assume-role-arn`, the exporter will:

1. Use the current AWS credentials to assume the specified role
2. Use the assumed role credentials for all ACM operations
3. Support cross-account access

**Required IAM Permissions:**
- `sts:AssumeRole` on the target role
- The target role must have ACM read permissions

## Troubleshooting Configuration

### Verify Configuration Loading

The exporter prints configuration loading messages:
```
Loaded configuration from /config/prometheus-acm-exporter.yaml
Initialized ACM client for region: us-east-1
Initialized ACM client for region: us-east-2
```

### Common Configuration Issues

1. **Config file not found**: Check the file path and permissions
2. **Invalid YAML**: Validate your YAML syntax
3. **Region not accessible**: Verify AWS credentials have access to the specified regions
4. **Role assumption fails**: Check IAM permissions and role ARN
5. **No certificates appearing**: Remember that only `ISSUED` certificates are collected. Certificates in PENDING_VALIDATION or other states won't appear in metrics