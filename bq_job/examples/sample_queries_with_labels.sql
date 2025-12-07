-- Sample Queries with Labels
-- These are example queries that demonstrate different use cases
-- In practice, labels would be applied via the BigQuery API/CLI, not in SQL

-- Example 1: Simple aggregation query
-- Labels: project_id:analytics, team:data-engineering, environment:prod
SELECT
  DATE(created_at) AS date,
  COUNT(*) AS event_count,
  COUNT(DISTINCT user_id) AS unique_users
FROM
  `project.dataset.events`
WHERE
  created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY
  date
ORDER BY
  date DESC;

-- Example 2: Data transformation query
-- Labels: project_id:data-warehouse, team:analytics, environment:prod, workflow:daily-aggregation
WITH daily_metrics AS (
  SELECT
    DATE(timestamp) AS date,
    user_id,
    SUM(revenue) AS daily_revenue,
    COUNT(*) AS event_count
  FROM
    `project.dataset.user_events`
  WHERE
    timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  GROUP BY
    date,
    user_id
)
SELECT
  date,
  COUNT(DISTINCT user_id) AS active_users,
  SUM(daily_revenue) AS total_revenue,
  AVG(daily_revenue) AS avg_revenue_per_user,
  SUM(event_count) AS total_events
FROM
  daily_metrics
GROUP BY
  date
ORDER BY
  date DESC;

-- Example 3: Join and aggregation
-- Labels: project_id:ml-platform, team:data-science, environment:prod, workflow:feature-engineering
SELECT
  u.user_id,
  u.signup_date,
  COUNT(DISTINCT e.event_id) AS total_events,
  SUM(e.revenue) AS total_revenue,
  MAX(e.timestamp) AS last_event_time
FROM
  `project.dataset.users` u
LEFT JOIN
  `project.dataset.events` e
ON
  u.user_id = e.user_id
WHERE
  u.signup_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY
  u.user_id,
  u.signup_date
HAVING
  total_events > 0
ORDER BY
  total_revenue DESC
LIMIT
  1000;

-- Example 4: Window function analysis
-- Labels: project_id:analytics, team:business-intelligence, environment:prod, workflow:user-segmentation
WITH user_activity AS (
  SELECT
    user_id,
    DATE(timestamp) AS activity_date,
    COUNT(*) AS daily_events
  FROM
    `project.dataset.events`
  WHERE
    timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  GROUP BY
    user_id,
    activity_date
),
user_stats AS (
  SELECT
    user_id,
    COUNT(DISTINCT activity_date) AS active_days,
    SUM(daily_events) AS total_events,
    AVG(daily_events) AS avg_daily_events,
    STDDEV(daily_events) AS stddev_daily_events
  FROM
    user_activity
  GROUP BY
    user_id
)
SELECT
  CASE
    WHEN active_days >= 20 THEN 'highly_active'
    WHEN active_days >= 10 THEN 'moderately_active'
    WHEN active_days >= 5 THEN 'occasionally_active'
    ELSE 'rarely_active'
  END AS activity_segment,
  COUNT(*) AS user_count,
  AVG(total_events) AS avg_total_events,
  AVG(active_days) AS avg_active_days
FROM
  user_stats
GROUP BY
  activity_segment
ORDER BY
  avg_active_days DESC;

-- Example 5: Time series analysis
-- Labels: project_id:analytics, team:data-engineering, environment:prod, workflow:hourly-metrics
SELECT
  TIMESTAMP_TRUNC(timestamp, HOUR) AS hour,
  COUNT(*) AS event_count,
  COUNT(DISTINCT user_id) AS unique_users,
  SUM(revenue) AS total_revenue,
  AVG(revenue) AS avg_revenue
FROM
  `project.dataset.events`
WHERE
  timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY
  hour
ORDER BY
  hour DESC;

-- Example 6: Complex aggregation with multiple CTEs
-- Labels: project_id:data-warehouse, team:analytics, environment:staging, workflow:test-pipeline
WITH raw_data AS (
  SELECT
    user_id,
    event_type,
    timestamp,
    revenue,
    country
  FROM
    `project.dataset.events`
  WHERE
    timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
),
user_summary AS (
  SELECT
    user_id,
    country,
    COUNT(*) AS event_count,
    SUM(revenue) AS total_revenue,
    COUNT(DISTINCT event_type) AS unique_event_types
  FROM
    raw_data
  GROUP BY
    user_id,
    country
),
country_summary AS (
  SELECT
    country,
    COUNT(DISTINCT user_id) AS unique_users,
    SUM(event_count) AS total_events,
    SUM(total_revenue) AS total_revenue,
    AVG(total_revenue) AS avg_revenue_per_user
  FROM
    user_summary
  GROUP BY
    country
)
SELECT
  country,
  unique_users,
  total_events,
  total_revenue,
  avg_revenue_per_user,
  total_revenue / NULLIF(unique_users, 0) AS revenue_per_user
FROM
  country_summary
ORDER BY
  total_revenue DESC;

