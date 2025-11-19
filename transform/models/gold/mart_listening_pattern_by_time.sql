{{ config(
    materialized='table'
) }}

WITH base_plays AS (
  SELECT 
    f.*,
    dt.duration_minutes,
    dt.explicit,
    dt.track_popularity
  FROM {{ ref('fct_plays') }} f
  JOIN {{ ref('dim_tracks_latest') }} dt ON f.track_id = dt.track_id
),

listening_patterns AS (
  SELECT
    -- Time dimensions
    played_date,
    time_of_day,
    played_hour,
    
    -- Aggregated metrics
    COUNT(*) AS total_plays,
    COUNT(DISTINCT track_id) AS unique_tracks,
    COUNT(DISTINCT artist_id) AS unique_artists,
    COUNT(DISTINCT album_id) AS unique_albums,
    
    -- Duration metrics
    SUM(duration_minutes) AS total_minutes_listened,
    AVG(duration_minutes) AS avg_track_duration,
    
    -- Explicit content analysis
    COUNT(CASE WHEN explicit THEN 1 END) AS explicit_plays,
    COUNT(CASE WHEN NOT explicit THEN 1 END) AS clean_plays,
    ROUND(100.0 * COUNT(CASE WHEN explicit THEN 1 END) / COUNT(*), 2) AS explicit_percentage,
    
    -- Popularity metrics
    AVG(track_popularity) AS avg_track_popularity,
    
    -- Context analysis
    COUNT(DISTINCT context_type) AS unique_context_types,
    MODE() WITHIN GROUP (ORDER BY context_type) AS most_common_context
    
  FROM base_plays
  GROUP BY played_date, time_of_day, played_hour
),

-- Add classifications
enriched_patterns AS (
  SELECT
    *,
    
    -- Explicit content pattern
    CASE
      WHEN explicit_percentage >= 75 THEN 'Mostly Explicit'
      WHEN explicit_percentage >= 50 THEN 'Mixed'
      WHEN explicit_percentage >= 25 THEN 'Mostly Clean'
      ELSE 'Predominantly Clean'
    END AS content_rating_pattern

  FROM listening_patterns
)

SELECT
  -- Time identifiers
  played_date,
  time_of_day,
  played_hour,
  
  -- Core metrics
  total_plays,
  unique_tracks,
  unique_artists,
  unique_albums,
  total_minutes_listened,
  avg_track_duration,
  
  -- Explicit content metrics
  explicit_plays,
  clean_plays,
  explicit_percentage,
  content_rating_pattern,
  
  -- Additional metrics
  avg_track_popularity,
  unique_context_types,
  most_common_context

FROM enriched_patterns
ORDER BY played_date DESC, played_hour
