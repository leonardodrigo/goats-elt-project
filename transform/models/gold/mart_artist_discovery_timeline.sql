{{ config(materialized='table')}}

WITH artist_first_play AS (
  SELECT
    f.artist_id,
    da.artist_name,
    MIN(f.played_at) AS discovered_at,
    MIN(f.played_date) AS discovered_date,
    COUNT(*) AS lifetime_plays,
    SUM(dt.duration_minutes) AS lifetime_minutes
  FROM {{ ref('fct_plays') }} f
  JOIN {{ ref('dim_artists_latest') }} da ON f.artist_id = da.artist_id
  JOIN {{ ref('dim_tracks_latest') }} dt ON f.track_id = dt.track_id
  GROUP BY f.artist_id, da.artist_name
),

discovery_cohorts AS (
  SELECT
    *,
    DATE_TRUNC('month', discovered_date) AS discovery_month,
    CURRENT_DATE - discovered_date AS days_since_discovery,
    
    CASE 
      WHEN discovered_date >= CURRENT_DATE - INTERVAL '30 days' THEN 'Last Month'
      WHEN discovered_date >= CURRENT_DATE - INTERVAL '90 days' THEN 'Last Quarter'
      WHEN discovered_date >= CURRENT_DATE - INTERVAL '1 year' THEN 'This Year'
      ELSE 'Older'
    END AS discovery_period
  FROM artist_first_play
)

SELECT
  artist_name,
  discovered_at,
  discovered_date,
  discovery_month,
  discovery_period,
  lifetime_plays,
  ROUND(lifetime_minutes, 1) AS lifetime_hours,
  days_since_discovery,
  
  -- Engagement metrics
  ROUND(lifetime_plays::NUMERIC / NULLIF(days_since_discovery, 0), 2) AS avg_plays_per_day_since_discovery,
  
  CASE 
    WHEN lifetime_plays >= 100 THEN 'Obsessed'
    WHEN lifetime_plays >= 50 THEN 'Super Fan'
    WHEN lifetime_plays >= 10 THEN 'Regular Listener'
    ELSE 'Casual'
  END AS fan_level
  
FROM discovery_cohorts
ORDER BY discovered_date DESC
