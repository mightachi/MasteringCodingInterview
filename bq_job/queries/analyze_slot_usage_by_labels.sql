-- Analyze Slot Usage by Labels
-- This query shows slot consumption grouped by project_id and team labels
-- Replace 'region-us' with your BigQuery region if different

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
  COUNT(*) AS job_count,
  SUM(total_slot_ms) AS total_slot_ms,
  -- Convert slot-ms to slot-hours for easier interpretation
  SUM(total_slot_ms) / 1000.0 / 60.0 / 60.0 AS total_slot_hours,
  AVG(total_slot_ms) AS avg_slot_ms,
  MAX(total_slot_ms) AS max_slot_ms,
  PERCENTILE_CONT(total_slot_ms, 0.5) OVER (PARTITION BY (
    SELECT value FROM UNNEST(labels) WHERE key = 'project_id'
  )) AS median_slot_ms,
  PERCENTILE_CONT(total_slot_ms, 0.95) OVER (PARTITION BY (
    SELECT value FROM UNNEST(labels) WHERE key = 'project_id'
  )) AS p95_slot_ms,
  -- Data processing metrics
  SUM(total_bytes_processed) AS total_bytes_processed,
  SUM(total_bytes_processed) / POW(10, 12) AS total_tb_processed,
  -- Time metrics
  MIN(creation_time) AS first_job_time,
  MAX(creation_time) AS last_job_time
FROM
  `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
  -- Only include jobs with required labels
  AND EXISTS (
    SELECT 1 
    FROM UNNEST(labels) AS label
    WHERE label.key = 'project_id'
  )
  AND EXISTS (
    SELECT 1 
    FROM UNNEST(labels) AS label
    WHERE label.key = 'team'
  )
GROUP BY
  project_id,
  team,
  environment
ORDER BY
  total_slot_ms DESC;

