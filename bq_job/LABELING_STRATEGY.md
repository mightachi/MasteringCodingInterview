# BigQuery Job Labels - Standard Labeling Strategy

## Overview

This document defines the standard labeling strategy for BigQuery jobs to enable consistent tracking, monitoring, and cost attribution across all data projects. This strategy aligns with our GCP Virtual Machine labeling conventions for organizational consistency.

## Core Principles

1. **Required Labels**: Every job MUST have these labels
2. **Optional Labels**: Additional labels for enhanced tracking
3. **Naming Conventions**: Consistent key and value formats aligned with GCP VM labels
4. **Validation**: Ensure labels are applied correctly
5. **Organizational Hierarchy**: Support vertical → tribe → team structure

## Required Labels

### 1. `team` (Required)

**Purpose**: Attribute resource usage to specific teams or departments.

**Format**:
- Key: `team` (lowercase)
- Value: Team name (lowercase, hyphens)

**Examples** (from your data):
- `team:ds-mle`
- `team:ds`
- `team:mle`
- `team:data-engineering`
- `team:analytics`

**Guidelines**:
- Use official team names from your organization
- Keep team names consistent across all projects
- Update when teams are renamed or reorganized
- Must match team values used in GCP VM labels

### 2. `environment` (Required)

**Purpose**: Distinguish between development, staging, and production workloads.

**Format**:
- Key: `environment` (lowercase)
- Value: One of: `dev`, `staging`, `prod`, `test`, `production`

**Examples**:
- `environment:prod`
- `environment:production`
- `environment:dev`
- `environment:test`
- `environment:staging`

**Guidelines**:
- Always use one of the standard values
- Use `prod` or `production` for production workloads (align with VM data)
- Critical for identifying production vs. test workloads
- Must match environment values used in GCP VM labels

## Recommended Labels

### 3. `vertical` (Recommended)

**Purpose**: Identify the vertical/business unit the job belongs to.

**Format**:
- Key: `vertical` (lowercase)
- Value: Vertical identifier (lowercase, hyphens)

**Examples** (from your data):
- `vertical:ds-mle`
- `vertical:data-science`
- `vertical:analytics`

**Guidelines**:
- Use consistent vertical names across the organization
- Align with vertical values in GCP VM labels
- Helps with cross-resource cost attribution

### 4. `tribe` (Recommended)

**Purpose**: Identify the tribe within the vertical.

**Format**:
- Key: `tribe` (lowercase)
- Value: Tribe name (lowercase, hyphens)

**Examples** (from your data):
- `tribe:ml-kubeflow`
- `tribe:ml-platform`
- `tribe:data-engineering`

**Guidelines**:
- Use official tribe names from your organization
- Maintains organizational hierarchy: vertical → tribe → team
- Align with tribe values in GCP VM labels

### 5. `service_type` (Recommended)

**Purpose**: Classify the type of service or workload.

**Format**:
- Key: `service_type` (lowercase, underscore)
- Value: Service type (lowercase, hyphens)

**Examples** (from your data):
- `service_type:python`
- `service_type:elasticsearch`
- `service_type:mongo`
- `service_type:other`
- `service_type:bigquery`
- `service_type:etl`

**Guidelines**:
- Use standard service type values
- Helps categorize different workload types
- Align with service_type values in GCP VM labels

### 6. `service_name` (Recommended)

**Purpose**: Identify the specific service or application.

**Format**:
- Key: `service_name` (lowercase, underscore)
- Value: Service name (lowercase, hyphens)

**Examples** (from your data):
- `service_name:vm-operator`
- `service_name:events-v2-search-esv8-data`
- `service_name:events-v2-inventory`
- `service_name:events-v2-order`
- `service_name:ml-pipeline-ui-artifact`

**Guidelines**:
- Use descriptive service names
- Keep consistent with service naming in other systems
- Helps identify specific applications consuming resources

### 7. `service_group` (Optional)

**Purpose**: Group related services together.

**Format**:
- Key: `service_group` (lowercase, underscore)
- Value: Service group name (lowercase, hyphens)

**Examples** (from your data):
- `service_group:monitoring`
- `service_group:event`
- `service_group:analytics`
- `service_group:ml-pipeline`

**Guidelines**:
- Use to group related services for cost attribution
- Helps with high-level resource grouping
- Align with service_group values in GCP VM labels

## Optional Labels

### 8. `namespace` (Optional)

**Purpose**: Identify the namespace or deployment context (useful for Kubernetes-based deployments).

**Format**:
- Key: `namespace` (lowercase)
- Value: Namespace identifier (lowercase, hyphens)

**Examples** (from your data):
- `namespace:vm`
- `namespace:abdullah-ghifari`
- `namespace:abraham-theodorus`
- `namespace:production`
- `namespace:staging`

**Guidelines**:
- Use for Kubernetes namespace tracking
- Can be used for deployment environment isolation
- Optional but recommended for containerized workloads

### 9. `workflow` (Optional)

**Purpose**: Identify the specific data pipeline or workflow.

**Format**:
- Key: `workflow` (lowercase)
- Value: Workflow/pipeline name (lowercase, hyphens)

**Examples**:
- `workflow:daily-sales-report`
- `workflow:user-segmentation`
- `workflow:inventory-sync`
- `workflow:model-training`
- `workflow:events-v2-etl`

**Guidelines**:
- Use descriptive names that identify the purpose
- Keep consistent with workflow naming in your orchestration tool
- Helps identify which workflows consume the most resources

### 10. `version` (Optional)

**Purpose**: Track which version of code/query is running.

**Format**:
- Key: `version` (lowercase)
- Value: Version identifier (lowercase, hyphens for separators)

**Examples**:
- `version:v1-0-0`
- `version:v2-3-1`
- `version:2024-01-15`
- `version:main`
- `version:abc123def` (git commit hash)

**Guidelines**:
- Use semantic versioning when possible (replace dots with hyphens)
- Can be git commit hash, release tag, or date-based
- Helps track performance changes across versions
- Replace dots (.) with hyphens (-) for consistency

### 11. `cost_center` (Optional)

**Purpose**: For organizations that need cost center attribution.

**Format**:
- Key: `cost_center` (lowercase, underscore)
- Value: Cost center identifier (lowercase, hyphens)

**Examples**:
- `cost_center:eng-001`
- `cost_center:analytics-002`
- `cost_center:ops-003`

**Guidelines**:
- Align with your organization's cost center structure
- Use official cost center codes if available

### 12. `priority` (Optional)

**Purpose**: Indicate job priority for resource allocation decisions.

**Format**:
- Key: `priority` (lowercase)
- Value: One of: `low`, `normal`, `high`, `critical`

**Examples**:
- `priority:low`
- `priority:normal`
- `priority:high`
- `priority:critical`

**Guidelines**:
- Use sparingly - most jobs should be `normal`
- Helps identify which jobs to prioritize during contention

### 13. `resource_name` (Optional)

**Purpose**: Identify the specific resource or deployment name associated with the BigQuery job.

**Format**:
- Key: `resource_name` (lowercase, underscore)
- Value: Resource name (lowercase, hyphens)

**Examples** (from your data):
- `resource_name:vmoperator-victoria-metrics-operator`
- `resource_name:ml-pipeline-ui-artifact`
- `resource_name:ml-pipeline-visualizationserver`
- `resource_name:events-v2-search-esv8-data`
- `resource_name:vm-tk-prod-ms-sea1-events-v2-esv8-data-1`

**Guidelines**:
- Use the exact resource name from your deployment system
- Helps track which specific resources are generating BigQuery jobs
- Useful for correlating BigQuery usage with specific deployments
- Align with resource_name values in GCP VM labels

### 14. `resource_type` (Optional)

**Purpose**: Classify the type of resource that is generating the BigQuery job.

**Format**:
- Key: `resource_type` (lowercase, underscore)
- Value: Resource type (lowercase, hyphens)

**Examples** (from your data):
- `resource_type:deployments`
- `resource_type:virtual-machine`
- `resource_type:kubernetes-pod`
- `resource_type:cloud-function`
- `resource_type:dataflow-job`

**Guidelines**:
- Use standard resource type values
- Helps categorize the source of BigQuery jobs
- Useful for understanding which resource types generate the most BigQuery usage
- Align with resource_type values in GCP VM labels

## Label Format Specifications

### Key Requirements

- **Case**: All lowercase
- **Characters**: Letters, numbers, hyphens (`-`), underscores (`_`)
- **Length**: Maximum 63 characters
- **Uniqueness**: Each key must be unique per job
- **Separator**: Use underscores (`_`) for multi-word keys (e.g., `service_name`, `service_group`)

### Value Requirements

- **Case**: All lowercase
- **Characters**: Letters, numbers, hyphens (`-`)
- **Length**: Maximum 63 characters
- **Format**: Use hyphens (`-`) for multi-word values (kebab-case)
- **No underscores**: Use hyphens instead of underscores in values for consistency

### Examples of Valid Labels

```
✅ team:ds-mle
✅ environment:prod
✅ vertical:ds-mle
✅ tribe:ml-kubeflow
✅ service_type:python
✅ service_name:events-v2-inventory
✅ service_group:monitoring
✅ namespace:vm
✅ workflow:daily-report
✅ version:v1-2-3
✅ cost_center:eng-001
✅ priority:high
✅ resource_name:ml-pipeline-ui-artifact
✅ resource_type:deployments
```

### Examples of Invalid Labels

```
❌ Team:ds-mle  (uppercase key)
❌ team:DS-MLE  (uppercase value)
❌ service-name:python  (hyphen in key - use underscore)
❌ service_name:events_v2_inventory  (underscore in value - use hyphen)
❌ environment:Production  (uppercase value)
❌ vertical:ds_mle  (underscore in value - use hyphen)
```

## Organizational Hierarchy

Labels support the following organizational hierarchy:

```
Vertical (e.g., ds-mle)
  └── Tribe (e.g., ml-kubeflow)
      └── Team (e.g., ds-mle, ds, mle)
          └── Service Type (e.g., python, elasticsearch)
              └── Service Name (e.g., events-v2-inventory)
                  └── Service Group (e.g., event, monitoring)
```

This hierarchy enables:
- Cost attribution at multiple organizational levels
- Filtering and grouping by any level
- Alignment with GCP VM resource labels
- Consistent resource tracking across infrastructure

## Implementation Guidelines

### 1. Label Application Checklist

When creating a BigQuery job, ensure:

- [ ] `team` is set
- [ ] `environment` is set
- [ ] `vertical` is set (if applicable)
- [ ] `tribe` is set (if applicable)
- [ ] `service_type` is set (if applicable)
- [ ] `service_name` is set (if applicable)
- [ ] `service_group` is set (if applicable)
- [ ] `resource_name` is set (if applicable)
- [ ] `resource_type` is set (if applicable)
- [ ] All label keys are lowercase
- [ ] All label values follow naming conventions (lowercase, hyphens)
- [ ] No duplicate keys

### 2. Code Integration

#### Python Example

```python
def get_standard_labels(
    team: str,
    environment: str,
    vertical: Optional[str] = None,
    tribe: Optional[str] = None,
    service_type: Optional[str] = None,
    service_name: Optional[str] = None,
    service_group: Optional[str] = None,
    resource_name: Optional[str] = None,
    resource_type: Optional[str] = None,
    workflow: Optional[str] = None,
    version: Optional[str] = None
) -> Dict[str, str]:
    """
    Get standard labels for BigQuery jobs aligned with GCP VM labeling.
    
    Args:
        team: Team name (required)
        environment: Environment (prod, dev, staging, test)
        vertical: Vertical/business unit (optional)
        tribe: Tribe name (optional)
        service_type: Type of service (optional)
        service_name: Service name (optional)
        service_group: Service group (optional)
        resource_name: Resource/deployment name (optional)
        resource_type: Type of resource (optional)
        workflow: Workflow/pipeline name (optional)
        version: Version identifier (optional)
        
    Returns:
        Dictionary of standardized labels
    """
    labels = {
        'team': _normalize_value(team),
        'environment': environment.lower()
    }
    
    if vertical:
        labels['vertical'] = _normalize_value(vertical)
    
    if tribe:
        labels['tribe'] = _normalize_value(tribe)
    
    if service_type:
        labels['service_type'] = _normalize_value(service_type)
    
    if service_name:
        labels['service_name'] = _normalize_value(service_name)
    
    if service_group:
        labels['service_group'] = _normalize_value(service_group)
    
    if resource_name:
        labels['resource_name'] = _normalize_value(resource_name)
    
    if resource_type:
        labels['resource_type'] = _normalize_value(resource_type)
    
    if workflow:
        labels['workflow'] = _normalize_value(workflow)
    
    if version:
        # Replace dots and underscores with hyphens for version
        labels['version'] = _normalize_value(version.replace('.', '-').replace('_', '-'))
    
    return labels


def _normalize_value(value: str) -> str:
    """
    Normalize label value to standard format.
    
    Rules:
    - Convert to lowercase
    - Replace underscores with hyphens
    - Replace spaces with hyphens
    - Remove special characters (keep alphanumeric and hyphens)
    - Remove consecutive hyphens
    - Enforce max length of 63 characters
    """
    normalized = value.lower()
    normalized = normalized.replace('_', '-')
    normalized = normalized.replace(' ', '-')
    # Remove any characters that aren't alphanumeric or hyphens
    normalized = ''.join(c if c.isalnum() or c == '-' else '' for c in normalized)
    # Remove consecutive hyphens
    normalized = '-'.join(filter(None, normalized.split('-')))
    return normalized[:63]  # Enforce max length


def validate_labels(labels: Dict[str, str]) -> None:
    """
    Validate that labels meet BigQuery and naming convention requirements.
    """
    required_labels = ['team', 'environment']
    
    for key in required_labels:
        if key not in labels:
            raise ValueError(f"Required label '{key}' is missing")
    
    for key, value in labels.items():
        # Validate key format
        if not key.islower():
            raise ValueError(f"Label key '{key}' must be lowercase")
        
        if not all(c.islower() or c.isdigit() or c in ['-', '_'] for c in key):
            raise ValueError(f"Label key '{key}' contains invalid characters (use lowercase, digits, hyphens, underscores only)")
        
        if len(key) > 63:
            raise ValueError(f"Label key '{key}' exceeds 63 characters")
        
        # Validate value format
        if not value.islower():
            raise ValueError(f"Label value '{value}' must be lowercase")
        
        if not all(c.islower() or c.isdigit() or c == '-' for c in value):
            raise ValueError(f"Label value '{value}' contains invalid characters (use lowercase, digits, hyphens only)")
        
        if len(value) > 63:
            raise ValueError(f"Label value '{value}' exceeds 63 characters")
    
    return True
```

#### Example Usage

```python
# Example 1: Production ML Pipeline
labels = get_standard_labels(
    team='ds-mle',
    environment='prod',
    vertical='ds-mle',
    tribe='ml-kubeflow',
    service_type='python',
    service_name='ml-pipeline-ui-artifact',
    service_group='ml-pipeline',
    workflow='daily-model-training',
    version='v1-2-3'
)

# Example 2: Events Service
labels = get_standard_labels(
    team='ds',
    environment='production',
    vertical='ds-mle',
    tribe='ml-kubeflow',
    service_type='mongo',
    service_name='events-v2-inventory',
    service_group='event'
)

# Example 3: Monitoring Service
labels = get_standard_labels(
    team='ds-mle',
    environment='prod',
    service_type='other',
    service_name='vm-operator',
    service_group='monitoring',
    namespace='vm',
    resource_name='vmoperator-victoria-metrics-operator',
    resource_type='deployments'
)

# Example 4: ML Pipeline with Resource Information
labels = get_standard_labels(
    team='ds-mle',
    environment='prod',
    vertical='ds-mle',
    tribe='ml-kubeflow',
    service_type='python',
    service_name='ml-pipeline-ui-artifact',
    service_group='ml-pipeline',
    resource_name='ml-pipeline-ui-artifact',
    resource_type='deployments',
    workflow='daily-model-training'
)
```

### 3. Validation

Create validation functions to ensure labels are correct:

```python
def validate_labels(labels: Dict[str, str]) -> None:
    """Validate that labels meet requirements."""
    required = ['team', 'environment']
    
    for key in required:
        if key not in labels:
            raise ValueError(f"Required label '{key}' is missing")
    
    # Validate environment value
    valid_environments = ['dev', 'staging', 'prod', 'production', 'test']
    if 'environment' in labels:
        if labels['environment'] not in valid_environments:
            raise ValueError(f"Invalid environment value: {labels['environment']}. Must be one of: {valid_environments}")
    
    for key, value in labels.items():
        if not key.islower():
            raise ValueError(f"Label key '{key}' must be lowercase")
        if len(key) > 63:
            raise ValueError(f"Label key '{key}' exceeds 63 characters")
        if len(value) > 63:
            raise ValueError(f"Label value '{value}' exceeds 63 characters")
        if not value.islower():
            raise ValueError(f"Label value '{value}' must be lowercase")
        # Check value doesn't contain underscores (use hyphens instead)
        if '_' in value:
            raise ValueError(f"Label value '{value}' should use hyphens, not underscores")
    
    return True
```

## Migration Strategy

### Phase 1: Establish Standards (Week 1-2)
- Document and communicate labeling strategy
- Create helper functions/libraries
- Update documentation
- Align with existing GCP VM labels

### Phase 2: Pilot Implementation (Week 3-4)
- Apply labels to new jobs in one project
- Test INFORMATION_SCHEMA queries
- Gather feedback
- Validate alignment with VM labels

### Phase 3: Rollout (Week 5-8)
- Apply labels to all new jobs
- Update existing pipelines gradually
- Monitor adoption
- Ensure consistency with VM labeling

### Phase 4: Enforcement (Week 9+)
- Add validation checks
- Create alerts for jobs without required labels
- Regular audits
- Cross-resource cost attribution reports

## Monitoring and Compliance

### 1. Label Coverage Report

Query to check label coverage:

```sql
SELECT
  COUNT(*) AS total_jobs,
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'team'
  )) AS jobs_with_team,
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'environment'
  )) AS jobs_with_environment,
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'vertical'
  )) AS jobs_with_vertical,
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'tribe'
  )) AS jobs_with_tribe,
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'service_type'
  )) AS jobs_with_service_type,
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'service_name'
  )) AS jobs_with_service_name,
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'team'
  ) AND EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'environment'
  )) AS jobs_with_required_labels
FROM
  `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY';
```

### 2. Label Value Distribution

Query to see what label values are being used:

```sql
SELECT
  label.key,
  label.value,
  COUNT(*) AS usage_count
FROM
  `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`,
  UNNEST(labels) AS label
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
GROUP BY
  label.key,
  label.value
ORDER BY
  label.key,
  usage_count DESC;
```

### 3. Organizational Hierarchy Analysis

Query to analyze resource usage by organizational hierarchy:

```sql
SELECT
  (
    SELECT value FROM UNNEST(labels) WHERE key = 'vertical'
  ) AS vertical,
  (
    SELECT value FROM UNNEST(labels) WHERE key = 'tribe'
  ) AS tribe,
  (
    SELECT value FROM UNNEST(labels) WHERE key = 'team'
  ) AS team,
  (
    SELECT value FROM UNNEST(labels) WHERE key = 'service_type'
  ) AS service_type,
  COUNT(*) AS job_count,
  SUM(total_slot_ms) AS total_slot_ms,
  SUM(total_bytes_processed) AS total_bytes_processed
FROM
  `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
GROUP BY
  vertical,
  tribe,
  team,
  service_type
ORDER BY
  total_slot_ms DESC;
```

## Alignment with GCP VM Labels

This BigQuery labeling strategy is designed to align with your GCP Virtual Machine labels:

| GCP VM Field | BigQuery Label Key | Notes |
|--------------|-------------------|-------|
| `team` | `team` | Direct mapping |
| `environment` | `environment` | Direct mapping (use `prod` or `production`) |
| `vertical` | `vertical` | Direct mapping |
| `tribe` | `tribe` | Direct mapping |
| `service_type` | `service_type` | Direct mapping |
| `service_name` | `service_name` | Direct mapping |
| `service_group` | `service_group` | Direct mapping |
| `resource_name` | `resource_name` | Direct mapping |
| `resource_type` | `resource_type` | Direct mapping |

This alignment enables:
- Cross-resource cost attribution (VMs + BigQuery)
- Unified resource tracking
- Consistent organizational hierarchy
- Simplified reporting and monitoring
- Correlation between resource deployments and BigQuery job usage

## Best Practices Summary

1. **Always apply required labels**: `team` and `environment`
2. **Use consistent naming**: Lowercase, hyphens for values, underscores for multi-word keys
3. **Align with VM labels**: Use same values for team, vertical, tribe, service_type, etc.
4. **Validate before submission**: Check label format and required keys
5. **Document exceptions**: If a label can't be applied, document why
6. **Regular audits**: Check label coverage and compliance
7. **Organizational hierarchy**: Use vertical → tribe → team structure when applicable
8. **Update as needed**: Evolve strategy based on organizational needs

## Questions and Support

For questions about this labeling strategy:
- Review the main documentation: `DOCUMENTATION.md`
- Check example implementations in `scripts/`
- Contact the data platform team
- Reference GCP VM labeling documentation for consistency

## Version History

- **v2.0** (Current): Aligned with GCP VM labeling convention, added organizational hierarchy labels
- **v1.0** (Initial): Core required labels (`project_id`, `team`) and optional labels

