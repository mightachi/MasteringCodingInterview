-- Label Value Distribution
-- See what label values are being used across all jobs
-- Helps identify inconsistencies and validate labeling strategy

SELECT
  label.key AS label_key,
  label.value AS label_value,
  COUNT(*) AS usage_count,
  COUNT(DISTINCT job_id) AS unique_jobs,
  SUM(total_slot_ms) AS total_slot_ms,
  SUM(total_slot_ms) / 1000.0 / 60.0 / 60.0 AS total_slot_hours
FROM
  `region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`,
  UNNEST(labels) AS label
WHERE
  creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND job_type = 'QUERY'
  AND state = 'DONE'
GROUP BY
  label.key,
  label.value
ORDER BY
  label.key,
  usage_count DESC;

