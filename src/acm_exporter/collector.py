import boto3
import yaml
import os
import logging
from datetime import datetime, timezone, timedelta
from prometheus_client.core import GaugeMetricFamily
logger = logging.getLogger(__name__)


def load_config(config_path=None):
    """Load configuration from YAML file."""
    # Default path if not provided
    if config_path is None:
        config_path = '/config/prometheus-acm-exporter.yaml'
    
    if not os.path.exists(config_path):
        logger.warning(f"Config file not found at {config_path}, using defaults")
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f) or {}
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading config file {config_path}: {e}", exc_info=True)
        return {}


def get_aws_session(config):
    """Get AWS session, optionally assuming a role.

    Returns:
        tuple: (session, credentials_expiration). expiration is None when not using
        role assumption; otherwise a timezone-aware datetime when the assumed-role
        credentials expire.
    """
    assume_role_arn = config.get('aws-assume-role-arn')
    assume_role_session = config.get('aws-assume-role-session', 'prometheus-acm-exporter')

    session = boto3.Session()
    expiration = None

    if assume_role_arn:
        try:
            sts_client = session.client('sts')
            assumed_role = sts_client.assume_role(
                RoleArn=assume_role_arn,
                RoleSessionName=assume_role_session
            )
            credentials = assumed_role['Credentials']
            session = boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken']
            )
            exp = credentials.get('Expiration')
            if exp is not None and exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            expiration = exp
            logger.info("Assumed role: %s (expires %s)", assume_role_arn, expiration)
        except Exception as e:
            logger.error("Error assuming role %s: %s", assume_role_arn, e, exc_info=True)
            raise

    return session, expiration


class ACMCertificateCollector:
    """Custom collector to fetch ACM certificate data on each scrape."""

    # Refresh assumed-role credentials this many minutes before expiry
    _REFRESH_MARGIN_MINUTES = 5

    def __init__(self, config=None):
        """Initialize collector with configuration."""
        if config is None:
            config = {}
        self._config = config

        # Get AWS session (with optional role assumption); expiration is set when using assume role
        session, self._session_expiration = get_aws_session(config)

        # Support both 'region' (single, backward compatible) and 'regions' (list)
        regions = config.get('regions', [])
        if not regions:
            single_region = config.get('region')
            if single_region:
                regions = [single_region]
            else:
                regions = [session.region_name or 'us-east-1']
        self._regions = list(regions)
        self.primary_region = self._regions[0]

        self._set_clients_from_session(session)

        # Get selected tags configuration (list of tag keys to include)
        selected_tags = config.get('selected-tags', [])
        if selected_tags:
            self.selected_tags = {tag.strip() for tag in selected_tags if tag.strip()}
            logger.info("Filtering tags to include only: %s", sorted(self.selected_tags))
        else:
            self.selected_tags = None

    def _set_clients_from_session(self, session, log_regions=True):
        """Build ACM and STS clients from the given session. Used at init and on credential refresh."""
        self.acm_clients = {
            region: session.client('acm', region_name=region)
            for region in self._regions
        }
        self.sts_client = session.client('sts', region_name=self.primary_region)
        try:
            self.aws_account = self.sts_client.get_caller_identity().get('Account', 'unknown')
        except Exception as e:
            logger.warning("Error getting AWS account ID: %s", e, exc_info=True)
            self.aws_account = 'unknown'
        if log_regions:
            for region in self._regions:
                logger.info("Initialized ACM client for region: %s", region)

    def _refresh_session(self):
        """Re-assume the role and rebuild clients. Called when assumed-role credentials are near expiry."""
        session, self._session_expiration = get_aws_session(self._config)
        self._set_clients_from_session(session, log_regions=False)
        logger.info("Refreshed assumed role credentials (expires %s)", self._session_expiration)

    def collect(self):
        """Collect metrics from all configured regions."""
        # Refresh assumed-role credentials before they expire
        if self._session_expiration is not None:
            now = datetime.now(timezone.utc)
            refresh_at = self._session_expiration - timedelta(minutes=self._REFRESH_MARGIN_MINUTES)
            if now >= refresh_at:
                try:
                    self._refresh_session()
                except Exception as e:
                    logger.error("Failed to refresh assumed role credentials: %s", e, exc_info=True)
                    # Continue with existing clients; next scrape may succeed after manual fix

        metrics_data = []
        now = datetime.now(timezone.utc)

        # Collect certificates from all regions
        for region, acm_client in self.acm_clients.items():
            try:
                # Fetch all issued certificates from ACM (handle pagination)
                certs = []
                try:
                    # Use paginator to get all certificates across all pages
                    paginator = acm_client.get_paginator('list_certificates')
                    page_iterator = paginator.paginate(CertificateStatuses=['ISSUED'])
                    
                    for page in page_iterator:
                        certs.extend(page.get('CertificateSummaryList', []))
                except Exception as e:
                    err_msg = str(e)
                    error_code = getattr(e, 'response', {}).get('Error', {}).get('Code', '') if isinstance(e, ClientError) else ''
                    is_credential_error = (
                        error_code == 'UnrecognizedClientException'
                        or ('invalid' in err_msg.lower() and 'token' in err_msg.lower())
                    )
                    if is_credential_error:
                        logger.error(
                            "Error listing certificates in region %s: %s. "
                            "Credentials may be invalid or expired. Check AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, "
                            "AWS_SESSION_TOKEN (if using temporary credentials), and that credentials are passed into "
                            "the container. See docs/configuration.md#troubleshooting.",
                            region, err_msg
                        )
                    else:
                        logger.error(f"Error listing certificates in region {region}: {e}", exc_info=True)
                    continue  # Continue with other regions
                
                # Process certificates from this region
                for cert in certs:
                    arn = cert.get('CertificateArn')
                    domain = cert.get('DomainName')
                    not_after = cert.get('NotAfter')
                    if not arn or not domain or not not_after:
                        continue  # skip if any key info is missing

                    # Extract certificate ID from ARN
                    # ARN format: arn:aws:acm:region:account-id:certificate/certificate-id
                    certificate_id = ''
                    if arn:
                        try:
                            # Split ARN and get the part after 'certificate/'
                            certificate_id = arn.split('/')[-1] if '/' in arn else arn.split(':')[-1]
                        except Exception:
                            certificate_id = arn  # Fallback to full ARN if parsing fails

                    # Extract Type, RenewalEligibility, and ExportOption from certificate summary
                    cert_type = cert.get('Type', '')
                    renewal_eligibility = cert.get('RenewalEligibility', '')
                    # ExportOption might be in the cert summary - check for it
                    export_option = cert.get('ExportOption', '')
                    # If ExportOption is not directly available, check for Exported field
                    if not export_option:
                        exported = cert.get('Exported', None)
                        if exported is not None:
                            export_option = 'EXPORTED' if exported else 'NOT_EXPORTED'

                    # Calculate days until expiration
                    # Ensure both dates are timezone-aware for subtraction
                    exp_datetime = not_after
                    if exp_datetime.tzinfo is None:
                        exp_datetime = exp_datetime.replace(tzinfo=timezone.utc)
                    days_remaining = (exp_datetime - now).days

                    # Get tags for the certificate (only include tags with non-empty values and selected tags)
                    tags = {}
                    try:
                        tag_response = acm_client.list_tags_for_certificate(CertificateArn=arn)
                        for tag in tag_response.get('Tags', []):
                            key = tag.get('Key', '')
                            value = tag.get('Value', '')
                            # Check if tag should be included:
                            # 1. Must have non-empty key and value
                            # 2. If selected_tags is configured, key must be in the list
                            if key and value and value.strip():
                                # Check if this tag is in the selected tags list (if configured)
                                if self.selected_tags is None or key in self.selected_tags:
                                    # Normalize tag key to valid label name (preserve case, replace hyphens with underscores)
                                    # Prefix with "tags_" to distinguish tag-derived labels
                                    label_name = 'tags_' + key.strip().replace('-', '_')
                                    tags[label_name] = value.strip()
                    except Exception as e:
                        logger.warning(f"Error fetching tags for {arn} in region {region}: {e}", exc_info=True)

                    # Always add certificate to metrics_data, even if it has no tags
                    # Certificates without tags will have an empty tags dict {}
                    metrics_data.append({
                        'region': region,  # Store region per certificate
                        'certificate_id': certificate_id,
                        'domain': domain,
                        'days_remaining': days_remaining,
                        'type': cert_type,
                        'renewal_eligibility': renewal_eligibility,
                        'export_option': export_option,
                        'tags': tags
                    })
            except Exception as e:
                logger.error(f"Error collecting from region {region}: {e}", exc_info=True)
                continue  # Continue with other regions

        # Group certificates by their tag key sets to avoid empty label values
        # Each group will have its own GaugeMetricFamily with only the tags that have values
        # Certificates with no tags will be grouped together (frozenset())
        tag_key_groups = {}
        for item in metrics_data:
            # Get the set of tag keys for this certificate
            # If certificate has no tags, this will be frozenset() (empty set)
            tag_keys = frozenset(item['tags'].keys())
            if tag_keys not in tag_key_groups:
                tag_key_groups[tag_keys] = []
            tag_key_groups[tag_keys].append(item)
        
        # Create a separate GaugeMetricFamily for each unique set of tag keys
        # This ensures no empty label values - each group only has tags that exist for all certs in that group
        for tag_keys, group_items in tag_key_groups.items():
            # Only include tag keys that are present (and non-empty) for this group
            # For certificates with no tags, sorted_tag_keys will be an empty list []
            sorted_tag_keys = sorted(tag_keys)
            label_names = ['region', 'aws_account', 'certificate_id', 'domain', 'type', 'renewal_eligibility', 'export_option'] + sorted_tag_keys
            
            gauge = GaugeMetricFamily(
                'acm_certificate_expiry_duration_days',
                'Number of days until ACM certificate expires',
                labels=label_names
            )
            
            # Add metrics for all certificates in this group
            # This includes certificates with no tags (they'll just have no tag labels)
            for item in group_items:
                # Construct labels - only include tags that exist (all are non-empty)
                # For certificates with no tags, tag_labels will be an empty list []
                tag_labels = [item['tags'][tag_key] for tag_key in sorted_tag_keys]
                labels = [
                    item['region'],  # Use region from item, not self.region
                    self.aws_account,
                    item['certificate_id'],
                    item['domain'],
                    item['type'],
                    item['renewal_eligibility'],
                    item['export_option']
                ] + tag_labels
                gauge.add_metric(labels, item['days_remaining'])
            
            yield gauge

    def describe(self):
        # Optionally implement describe to avoid initial collect on registration (no preset metrics)
        return []
