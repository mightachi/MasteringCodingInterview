-- Find Peak Contention Periods
-- This query identifies time periods with highest slot usage, grouped by project
-- Helps identify when and which projects cause slot contention

WITH hourly_slot_usage AS (
  SELECT
    TIMESTAMP_TRUNC(creation_time, HOUR) AS hour,
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
    SUM(total_slot_ms) AS total_slot_ms,
    COUNT(*) AS job_count,
    AVG(total_slot_ms) AS avg_slot_ms_per_job,
    MAX(total_slot_ms) AS max_slot_ms_single_job
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
    project_id,
    team,
    environment
),
ranked_hours AS (
  SELECT
    hour,
    project_id,
    team,
    environment,
    total_slot_ms,
    job_count,
    avg_slot_ms_per_job,
    max_slot_ms_single_job,
    -- Convert to slot-hours for interpretation
    total_slot_ms / 1000.0 / 60.0 / 60.0 AS slot_hours,
    ROW_NUMBER() OVER (PARTITION BY hour ORDER BY total_slot_ms DESC) AS rank_in_hour,
    ROW_NUMBER() OVER (PARTITION BY project_id ORDER BY total_slot_ms DESC) AS rank_for_project
  FROM
    hourly_slot_usage
)
SELECT
  hour,
  project_id,
  team,
  environment,
  total_slot_ms,
  slot_hours,
  job_count,
  avg_slot_ms_per_job,
  max_slot_ms_single_job,
  rank_in_hour,
  rank_for_project
FROM
  ranked_hours
WHERE
  -- Show top 3 projects per hour, or top 20 overall
  rank_in_hour <= 3
  OR rank_for_project <= 20
ORDER BY
  hour DESC,
  total_slot_ms DESC;

