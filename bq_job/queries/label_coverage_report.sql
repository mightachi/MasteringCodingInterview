-- Label Coverage Report
-- Check how many jobs have the required labels applied
-- Helps monitor adoption and compliance with labeling strategy

SELECT
  COUNT(*) AS total_jobs,
  -- Required labels
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'project_id'
  )) AS jobs_with_project_id,
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'team'
  )) AS jobs_with_team,
  -- Recommended labels
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'environment'
  )) AS jobs_with_environment,
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'workflow'
  )) AS jobs_with_workflow,
  -- Compliance: jobs with both required labels
  COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'project_id'
  ) AND EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'team'
  )) AS jobs_with_required_labels,
  -- Percentage calculations
  ROUND(100.0 * COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'project_id'
  )) / COUNT(*), 2) AS pct_with_project_id,
  ROUND(100.0 * COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'team'
  )) / COUNT(*), 2) AS pct_with_team,
  ROUND(100.0 * COUNTIF(EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'project_id'
  ) AND EXISTS (
    SELECT 1 FROM UNNEST(labels) WHERE key = 'team'
  )) / COUNT(*), 2) AS pct_with_required_labels
FROM
  `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE';

