{{ config(materialized='table')}}

WITH all_artists AS (
    artist_id,
    artist_name,
    artist_uri
  FROM {{ ref('silver_artists_latest') }}
  WHERE artist_id IS NOT NULL
),

artist_metrics AS (
  SELECT
    artist_id,
    COUNT(*) AS total_plays,
    COUNT(DISTINCT track_id) AS unique_tracks,
    MIN(played_at) AS first_play_date,
    MAX(played_at) AS last_play_date
  FROM {{ ref('silver_plays_latest') }}
  GROUP BY artist_id
)

SELECT
  aa.artist_id,
  aa.artist_name,
  aa.artist_uri,
  
  -- Enrichments
  COALESCE(am.total_plays, 0) AS total_plays,
  COALESCE(am.unique_tracks, 0) AS unique_tracks,
  am.first_play_date,
  am.last_play_date,
  
  -- Categorization
  CASE 
    WHEN COALESCE(am.total_plays, 0) >= 100 THEN 'Top Artist'
    WHEN COALESCE(am.total_plays, 0) >= 10 THEN 'Regular'
    ELSE 'Occasional'
  END AS artist_tier,
  
  CURRENT_TIMESTAMP AS dim_updated_at

FROM all_artists aa
LEFT JOIN artist_metrics am ON aa.artist_id = am.artist_id
