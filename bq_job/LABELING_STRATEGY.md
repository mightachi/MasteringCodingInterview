# BigQuery Job Labels - Standard Labeling Strategy

## Overview

This document proposes a standard labeling strategy for BigQuery jobs to enable consistent tracking, monitoring, and cost attribution across all data projects.

## Core Principles

1. **Required Labels**: Every job MUST have these labels
2. **Optional Labels**: Additional labels for enhanced tracking
3. **Naming Conventions**: Consistent key and value formats
4. **Validation**: Ensure labels are applied correctly

## Required Labels

### 1. `project_id` (Required)

**Purpose**: Identify which project/application the job belongs to.

**Format**: 
- Key: `project_id` (lowercase, underscore)
- Value: Project identifier (lowercase, hyphens)

**Examples**:
- `project_id:analytics-platform`
- `project_id:data-warehouse`
- `project_id:ml-training`
- `project_id:etl-pipeline`

**Guidelines**:
- Use a consistent naming scheme across the organization
- Should match your project tracking system
- Keep it concise but descriptive

### 2. `team` (Required)

**Purpose**: Attribute resource usage to specific teams or departments.

**Format**:
- Key: `team` (lowercase)
- Value: Team name (lowercase, hyphens)

**Examples**:
- `team:data-engineering`
- `team:analytics`
- `team:ml-platform`
- `team:data-science`
- `team:business-intelligence`

**Guidelines**:
- Use official team names from your organization
- Keep team names consistent across all projects
- Update when teams are renamed or reorganized

## Optional Labels

### 3. `environment` (Recommended)

**Purpose**: Distinguish between development, staging, and production workloads.

**Format**:
- Key: `environment` (lowercase)
- Value: One of: `dev`, `staging`, `prod`, `test`

**Examples**:
- `environment:dev`
- `environment:staging`
- `environment:prod`
- `environment:test`

**Guidelines**:
- Always use one of the standard values
- Helps with cost allocation and debugging
- Critical for identifying production vs. test workloads

### 4. `workflow` (Recommended)

**Purpose**: Identify the specific data pipeline or workflow.

**Format**:
- Key: `workflow` (lowercase)
- Value: Workflow/pipeline name (lowercase, hyphens)

**Examples**:
- `workflow:daily-sales-report`
- `workflow:user-segmentation`
- `workflow:inventory-sync`
- `workflow:model-training`

**Guidelines**:
- Use descriptive names that identify the purpose
- Keep consistent with workflow naming in your orchestration tool
- Helps identify which workflows consume the most resources

### 5. `version` (Optional)

**Purpose**: Track which version of code/query is running.

**Format**:
- Key: `version` (lowercase)
- Value: Version identifier (semantic versioning recommended)

**Examples**:
- `version:v1.0.0`
- `version:v2.3.1`
- `version:2024.01.15`
- `version:main`

**Guidelines**:
- Use semantic versioning when possible
- Can be git commit hash, release tag, or date-based
- Helps track performance changes across versions

### 6. `cost-center` (Optional)

**Purpose**: For organizations that need cost center attribution.

**Format**:
- Key: `cost_center` (lowercase, underscore)
- Value: Cost center identifier

**Examples**:
- `cost_center:eng-001`
- `cost_center:analytics-002`
- `cost_center:ops-003`

**Guidelines**:
- Align with your organization's cost center structure
- Use official cost center codes if available

### 7. `priority` (Optional)

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

## Label Format Specifications

### Key Requirements

- **Case**: All lowercase
- **Characters**: Letters, numbers, hyphens (`-`), underscores (`_`)
- **Length**: Maximum 63 characters
- **Uniqueness**: Each key must be unique per job

### Value Requirements

- **Case**: Recommended lowercase for consistency
- **Characters**: Any valid string
- **Length**: Maximum 63 characters
- **Format**: Use hyphens for multi-word values

### Examples of Valid Labels

```
✅ project_id:analytics-platform
✅ team:data-engineering
✅ environment:prod
✅ workflow:daily-report
✅ version:v1.2.3
✅ cost_center:eng-001
```

### Examples of Invalid Labels

```
❌ Project_ID:analytics-platform  (uppercase key)
❌ project-id:analytics-platform  (hyphen in key - use underscore)
❌ project_id:Analytics Platform  (uppercase and space in value)
❌ project_id:analytics_platform  (underscore in value - use hyphen)
```

## Implementation Guidelines

### 1. Label Application Checklist

When creating a BigQuery job, ensure:

- [ ] `project_id` is set
- [ ] `team` is set
- [ ] `environment` is set (if applicable)
- [ ] `workflow` is set (if applicable)
- [ ] All label keys are lowercase
- [ ] All label values follow naming conventions
- [ ] No duplicate keys

### 2. Code Integration

#### Python Example
```python
def get_standard_labels(project_id, team, environment='prod', workflow=None):
    """Get standard labels for BigQuery jobs."""
    labels = {
        'project_id': project_id.lower().replace('_', '-'),
        'team': team.lower().replace('_', '-'),
        'environment': environment.lower()
    }
    
    if workflow:
        labels['workflow'] = workflow.lower().replace('_', '-')
    
    return labels
```

#### Java Example
```java
public Map<String, String> getStandardLabels(
    String projectId, 
    String team, 
    String environment
) {
    Map<String, String> labels = new HashMap<>();
    labels.put("project_id", projectId.toLowerCase().replace("_", "-"));
    labels.put("team", team.toLowerCase().replace("_", "-"));
    labels.put("environment", environment.toLowerCase());
    return labels;
}
```

### 3. Validation

Create validation functions to ensure labels are correct:

```python
def validate_labels(labels):
    """Validate that labels meet requirements."""
    required = ['project_id', 'team']
    
    for key in required:
        if key not in labels:
            raise ValueError(f"Required label '{key}' is missing")
    
    for key, value in labels.items():
        if not key.islower():
            raise ValueError(f"Label key '{key}' must be lowercase")
        if len(key) > 63:
            raise ValueError(f"Label key '{key}' exceeds 63 characters")
        if len(value) > 63:
            raise ValueError(f"Label value '{value}' exceeds 63 characters")
    
    return True
```

## Migration Strategy

### Phase 1: Establish Standards (Week 1-2)
- Document and communicate labeling strategy
- Create helper functions/libraries
- Update documentation

### Phase 2: Pilot Implementation (Week 3-4)
- Apply labels to new jobs in one project
- Test INFORMATION_SCHEMA queries
- Gather feedback

### Phase 3: Rollout (Week 5-8)
- Apply labels to all new jobs
- Update existing pipelines gradually
- Monitor adoption

### Phase 4: Enforcement (Week 9+)
- Add validation checks
- Create alerts for jobs without required labels
- Regular audits

## Monitoring and Compliance

### 1. Label Coverage Report

Query to check label coverage:

```sql
SELECT
  COUNT(*) AS total_jobs,
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'project_id'
  )) AS jobs_with_project_id,
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'team'
  )) AS jobs_with_team,
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'environment'
  )) AS jobs_with_environment,
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'project_id'
  ) AND EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'team'
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

## Best Practices Summary

1. **Always apply required labels**: `project_id` and `team`
2. **Use consistent naming**: Lowercase, hyphens for values
3. **Validate before submission**: Check label format and required keys
4. **Document exceptions**: If a label can't be applied, document why
5. **Regular audits**: Check label coverage and compliance
6. **Update as needed**: Evolve strategy based on organizational needs

## Questions and Support

For questions about this labeling strategy:
- Review the main documentation: `DOCUMENTATION.md`
- Check example implementations in `scripts/`
- Contact the data platform team

## Version History

- **v1.0** (Initial): Core required labels (`project_id`, `team`) and optional labels
- Future versions will be documented here as the strategy evolves

