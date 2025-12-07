-- Project-Level Slot Usage Analysis
-- Comprehensive analysis of slot usage by project with trends and statistics
-- Replace 'region-us' with your BigQuery region if different

WITH project_stats AS (
  SELECT
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
    creation_time,
    total_slot_ms,
    total_bytes_processed,
    job_id,
    query
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
),
project_summary AS (
  SELECT
    project_id,
    team,
    environment,
    COUNT(*) AS total_jobs,
    SUM(total_slot_ms) AS total_slot_ms,
    SUM(total_slot_ms) / 1000.0 / 60.0 / 60.0 AS total_slot_hours,
    AVG(total_slot_ms) AS avg_slot_ms,
    STDDEV(total_slot_ms) AS stddev_slot_ms,
    MIN(total_slot_ms) AS min_slot_ms,
    MAX(total_slot_ms) AS max_slot_ms,
    APPROX_QUANTILES(total_slot_ms, 100)[OFFSET(50)] AS median_slot_ms,
    APPROX_QUANTILES(total_slot_ms, 100)[OFFSET(90)] AS p90_slot_ms,
    APPROX_QUANTILES(total_slot_ms, 100)[OFFSET(95)] AS p95_slot_ms,
    APPROX_QUANTILES(total_slot_ms, 100)[OFFSET(99)] AS p99_slot_ms,
    SUM(total_bytes_processed) AS total_bytes_processed,
    SUM(total_bytes_processed) / POW(10, 12) AS total_tb_processed,
    MIN(creation_time) AS first_job,
    MAX(creation_time) AS last_job,
    TIMESTAMP_DIFF(MAX(creation_time), MIN(creation_time), HOUR) AS time_span_hours
  FROM
    project_stats
  GROUP BY
    project_id,
    team,
    environment
),
top_jobs AS (
  SELECT
    project_id,
    job_id,
    creation_time,
    total_slot_ms,
    total_bytes_processed,
    SUBSTR(query, 1, 200) AS query_preview,
    ROW_NUMBER() OVER (PARTITION BY project_id ORDER BY total_slot_ms DESC) AS rank
  FROM
    project_stats
)
SELECT
  ps.project_id,
  ps.team,
  ps.environment,
  ps.total_jobs,
  ps.total_slot_ms,
  ps.total_slot_hours,
  ps.avg_slot_ms,
  ps.median_slot_ms,
  ps.p90_slot_ms,
  ps.p95_slot_ms,
  ps.p99_slot_ms,
  ps.max_slot_ms,
  ps.total_tb_processed,
  ps.time_span_hours,
  -- Average jobs per hour
  ps.total_jobs / NULLIF(ps.time_span_hours, 0) AS avg_jobs_per_hour,
  -- Average slot-ms per hour
  ps.total_slot_ms / NULLIF(ps.time_span_hours, 0) AS avg_slot_ms_per_hour,
  -- Top job details
  tj.job_id AS top_job_id,
  tj.creation_time AS top_job_time,
  tj.total_slot_ms AS top_job_slot_ms,
  tj.query_preview AS top_job_query
FROM
  project_summary ps
LEFT JOIN
  top_jobs tj
ON
  ps.project_id = tj.project_id
  AND tj.rank = 1
ORDER BY
  ps.total_slot_ms DESC;

