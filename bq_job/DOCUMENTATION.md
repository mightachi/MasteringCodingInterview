# BigQuery Job Labels - Comprehensive Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [What are Job Labels?](#what-are-job-labels)
3. [How Job Labels Work](#how-job-labels-work)
4. [Querying Job Labels via INFORMATION_SCHEMA](#querying-job-labels-via-information_schema)
5. [Analyzing Slot Usage with Labels](#analyzing-slot-usage-with-labels)
6. [Best Practices](#best-practices)
7. [Limitations and Considerations](#limitations-and-considerations)

## Introduction

BigQuery Job Labels are key-value pairs that you can attach to BigQuery jobs (queries, load jobs, copy jobs, etc.) to add metadata for tracking, monitoring, and cost attribution. This documentation explains how to use Job Labels to analyze slot contention and resource consumption.

## What are Job Labels?

Job Labels are metadata tags that:
- Are attached to BigQuery jobs at job creation time
- Consist of key-value pairs (both strings)
- Can be used to filter and group jobs in monitoring queries
- Help attribute resource usage to specific projects, teams, or environments
- Are visible in INFORMATION_SCHEMA for analysis

### Key Characteristics

- **Keys**: Must be lowercase letters, numbers, hyphens, or underscores
- **Values**: Can contain any characters
- **Format**: `key:value` pairs
- **Maximum**: 64 labels per job
- **Key length**: Up to 63 characters
- **Value length**: Up to 63 characters

## How Job Labels Work

### 1. Applying Labels to Jobs

Labels are applied when creating a BigQuery job. The method depends on how you're running the query:

#### Using bq CLI
```bash
bq query \
  --label=project_id:analytics \
  --label=team:data-engineering \
  --label=environment:prod \
  "SELECT COUNT(*) FROM \`project.dataset.table\`"
```

#### Using Python Client Library
```python
from google.cloud import bigquery

client = bigquery.Client(project='your-project')

job_config = bigquery.QueryJobConfig()
job_config.labels = {
    'project_id': 'analytics',
    'team': 'data-engineering',
    'environment': 'prod'
}

query_job = client.query(
    "SELECT COUNT(*) FROM `project.dataset.table`",
    job_config=job_config
)
```

#### Using SQL (via BigQuery API)
```sql
-- Labels are applied via the API, not in SQL itself
-- But you can reference them in INFORMATION_SCHEMA queries
```

### 2. Where Labels Appear

Once applied, labels are visible in:
- **INFORMATION_SCHEMA.JOBS_BY_PROJECT**: For querying job metadata
- **INFORMATION_SCHEMA.JOBS_BY_USER**: For user-specific jobs
- **INFORMATION_SCHEMA.JOBS_BY_ORGANIZATION**: For organization-wide view
- **BigQuery Console**: In the job details page
- **BigQuery API**: In job metadata responses

## Querying Job Labels via INFORMATION_SCHEMA

### Basic Query Structure

The `INFORMATION_SCHEMA.JOBS_BY_PROJECT` view contains job metadata including labels:

```sql
SELECT
  job_id,
  creation_time,
  job_type,
  state,
  total_slot_ms,
  labels,
  query
FROM
  `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
ORDER BY
  creation_time DESC
LIMIT 100;
```

### Accessing Labels

Labels are stored as an array of structs with `key` and `value` fields:

```sql
SELECT
  job_id,
  creation_time,
  -- Extract specific label values
  (
    SELECT value 
    FROM UNNEST(labels) 
    WHERE key = 'project_id'
  ) AS project_id,
  (
    SELECT value 
    FROM UNNEST(labels) 
    WHERE key = 'team'
  ) AS team,
  (
    SELECT value 
    FROM UNNEST(labels) 
    WHERE key = 'environment'
  ) AS environment,
  total_slot_ms,
  total_bytes_processed
FROM
  `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
  AND job_type = 'QUERY'
ORDER BY
  total_slot_ms DESC;
```

### Filtering by Labels

To filter jobs by specific labels:

```sql
SELECT
  job_id,
  creation_time,
  total_slot_ms,
  query
FROM
  `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
  AND job_type = 'QUERY'
  AND EXISTS (
    SELECT 1 
    FROM UNNEST(labels) AS label
    WHERE label.key = 'project_id' 
      AND label.value = 'analytics'
  )
ORDER BY
  total_slot_ms DESC;
```

## Analyzing Slot Usage with Labels

### 1. Slot Usage by Project

```sql
SELECT
  (
    SELECT value 
    FROM UNNEST(labels) 
    WHERE key = 'project_id'
  ) AS project_id,
  COUNT(*) AS job_count,
  SUM(total_slot_ms) AS total_slot_ms,
  AVG(total_slot_ms) AS avg_slot_ms,
  MAX(total_slot_ms) AS max_slot_ms,
  SUM(total_bytes_processed) AS total_bytes_processed
FROM
  `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
  AND EXISTS (
    SELECT 1 
    FROM UNNEST(labels) AS label
    WHERE label.key = 'project_id'
  )
GROUP BY
  project_id
ORDER BY
  total_slot_ms DESC;
```

### 2. Peak Contention Analysis

Identify time periods with highest slot usage by project:

```sql
SELECT
  TIMESTAMP_TRUNC(creation_time, HOUR) AS hour,
  (
    SELECT value 
    FROM UNNEST(labels) 
    WHERE key = 'project_id'
  ) AS project_id,
  SUM(total_slot_ms) AS total_slot_ms,
  COUNT(*) AS job_count,
  AVG(total_slot_ms) AS avg_slot_ms_per_job
FROM
  `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
  AND EXISTS (
    SELECT 1 
    FROM UNNEST(labels) AS label
    WHERE label.key = 'project_id'
  )
GROUP BY
  hour,
  project_id
ORDER BY
  hour DESC,
  total_slot_ms DESC;
```

### 3. Team-Level Resource Attribution

```sql
SELECT
  (
    SELECT value 
    FROM UNNEST(labels) 
    WHERE key = 'team'
  ) AS team,
  (
    SELECT value 
    FROM UNNEST(labels) 
    WHERE key = 'project_id'
  ) AS project_id,
  COUNT(*) AS job_count,
  SUM(total_slot_ms) AS total_slot_ms,
  SUM(total_slot_ms) / 1000.0 / 60.0 / 60.0 AS total_slot_hours,
  SUM(total_bytes_processed) / POW(10, 12) AS total_tb_processed
FROM
  `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
  AND EXISTS (
    SELECT 1 
    FROM UNNEST(labels) AS label
    WHERE label.key = 'team'
  )
GROUP BY
  team,
  project_id
ORDER BY
  total_slot_ms DESC;
```

### 4. Environment-Based Analysis

Compare resource usage across environments:

```sql
SELECT
  (
    SELECT value 
    FROM UNNEST(labels) 
    WHERE key = 'environment'
  ) AS environment,
  (
    SELECT value 
    FROM UNNEST(labels) 
    WHERE key = 'project_id'
  ) AS project_id,
  COUNT(*) AS job_count,
  SUM(total_slot_ms) AS total_slot_ms,
  AVG(total_slot_ms) AS avg_slot_ms,
  PERCENTILE_CONT(total_slot_ms, 0.95) OVER (PARTITION BY (
    SELECT value FROM UNNEST(labels) WHERE key = 'environment'
  )) AS p95_slot_ms
FROM
  `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
  AND EXISTS (
    SELECT 1 
    FROM UNNEST(labels) AS label
    WHERE label.key = 'environment'
  )
GROUP BY
  environment,
  project_id
ORDER BY
  environment,
  total_slot_ms DESC;
```

### 5. Identifying Bottleneck Jobs

Find the most resource-intensive jobs during peak times:

```sql
WITH peak_hours AS (
  SELECT
    TIMESTAMP_TRUNC(creation_time, HOUR) AS hour,
    SUM(total_slot_ms) AS hourly_slot_ms
  FROM
    `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
  WHERE
    creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
    AND job_type = 'QUERY'
    AND state = 'DONE'
  GROUP BY
    hour
  ORDER BY
    hourly_slot_ms DESC
  LIMIT 10
)
SELECT
  j.job_id,
  j.creation_time,
  (
    SELECT value 
    FROM UNNEST(j.labels) 
    WHERE key = 'project_id'
  ) AS project_id,
  (
    SELECT value 
    FROM UNNEST(j.labels) 
    WHERE key = 'team'
  ) AS team,
  j.total_slot_ms,
  j.total_bytes_processed,
  SUBSTR(j.query, 1, 200) AS query_preview
FROM
  `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT` j
INNER JOIN
  peak_hours p
ON
  TIMESTAMP_TRUNC(j.creation_time, HOUR) = p.hour
WHERE
  j.job_type = 'QUERY'
  AND j.state = 'DONE'
ORDER BY
  j.total_slot_ms DESC
LIMIT 50;
```

## Best Practices

### 1. Consistent Label Keys

Use standardized label keys across all projects:
- `project_id`: Identifier for the project/application
- `team`: Team or department name
- `environment`: dev, staging, prod
- `workflow`: Name of the data pipeline or workflow
- `version`: Version of the code/query

### 2. Label Values

- Use lowercase for consistency
- Use hyphens instead of underscores for readability
- Keep values concise but descriptive
- Avoid special characters that might cause issues

### 3. Always Apply Core Labels

Make it a requirement to apply at least:
- `project_id`: For project-level attribution
- `team`: For team-level cost tracking

### 4. Query Performance

- Use `EXISTS` clauses for label filtering (more efficient)
- Consider partitioning by time for large-scale analysis
- Use appropriate time ranges to limit data scanned

### 5. Monitoring Integration

- Set up scheduled queries to track slot usage trends
- Create dashboards using the analysis queries
- Set up alerts for unusual slot consumption patterns

## Limitations and Considerations

### 1. Historical Data

- Labels only apply to jobs created after you start using them
- Historical jobs won't have labels
- Consider this when analyzing trends over time

### 2. INFORMATION_SCHEMA Retention

- Job metadata is retained for 180 days in INFORMATION_SCHEMA
- Plan your analysis windows accordingly

### 3. Label Application

- Labels must be applied at job creation time
- Cannot be added or modified after job creation
- Ensure all query execution paths apply labels

### 4. Slot Usage Calculation

- `total_slot_ms` represents cumulative slot milliseconds
- For concurrent queries, this doesn't directly show peak slot usage
- Use time-based aggregation to understand peak contention

### 5. Cost Attribution

- Slot usage is a measure of compute resources
- Combine with bytes processed for complete cost picture
- Consider both on-demand and reservation pricing models

## Conclusion

BigQuery Job Labels provide a powerful mechanism for tracking and analyzing slot contention. By consistently applying labels and using INFORMATION_SCHEMA queries, you can:

- Identify which projects consume the most resources
- Track team-level resource usage
- Find bottlenecks during peak times
- Attribute costs accurately
- Make data-driven decisions about resource allocation

The key to success is:
1. Establishing a standard labeling strategy
2. Consistently applying labels to all jobs
3. Regularly analyzing slot usage patterns
4. Using insights to optimize resource consumption

