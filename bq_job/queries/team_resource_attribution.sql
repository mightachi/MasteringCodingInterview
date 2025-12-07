-- Team Resource Attribution
-- Analyze slot usage and resource consumption by team
-- Helps with cost allocation and resource planning

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
  (
    SELECT value 
    FROM UNNEST(labels) 
    WHERE key = 'environment'
  ) AS environment,
  -- Job statistics
  COUNT(*) AS total_jobs,
  COUNT(DISTINCT DATE(creation_time)) AS active_days,
  -- Slot usage metrics
  SUM(total_slot_ms) AS total_slot_ms,
  SUM(total_slot_ms) / 1000.0 / 60.0 / 60.0 AS total_slot_hours,
  AVG(total_slot_ms) AS avg_slot_ms,
  APPROX_QUANTILES(total_slot_ms, 100)[OFFSET(50)] AS median_slot_ms,
  APPROX_QUANTILES(total_slot_ms, 100)[OFFSET(95)] AS p95_slot_ms,
  MAX(total_slot_ms) AS max_slot_ms,
  -- Data processing metrics
  SUM(total_bytes_processed) AS total_bytes_processed,
  SUM(total_bytes_processed) / POW(10, 12) AS total_tb_processed,
  AVG(total_bytes_processed) AS avg_bytes_processed,
  -- Time range
  MIN(creation_time) AS first_job_time,
  MAX(creation_time) AS last_job_time,
  -- Efficiency metrics
  AVG(total_slot_ms / NULLIF(total_bytes_processed, 0) * POW(10, 9)) AS avg_slot_ms_per_gb,
  -- Job distribution by day of week
  COUNTIF(EXTRACT(DAYOFWEEK FROM creation_time) = 1) AS sunday_jobs,
  COUNTIF(EXTRACT(DAYOFWEEK FROM creation_time) = 2) AS monday_jobs,
  COUNTIF(EXTRACT(DAYOFWEEK FROM creation_time) = 3) AS tuesday_jobs,
  COUNTIF(EXTRACT(DAYOFWEEK FROM creation_time) = 4) AS wednesday_jobs,
  COUNTIF(EXTRACT(DAYOFWEEK FROM creation_time) = 5) AS thursday_jobs,
  COUNTIF(EXTRACT(DAYOFWEEK FROM creation_time) = 6) AS friday_jobs,
  COUNTIF(EXTRACT(DAYOFWEEK FROM creation_time) = 7) AS saturday_jobs
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
  project_id,
  environment
ORDER BY
  total_slot_ms DESC;

