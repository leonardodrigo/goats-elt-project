{{ config(
    materialized='table',
) }}

WITH silver AS (
  SELECT
    track_id,
    track_name,
    track_uri,
    track_href,
    track_popularity,
    duration_ms,
    duration_minutes,
    explicit,
    is_local,
    disc_number,
    track_number,
    isrc,
    album_id,
    artist_id,
    artist_count
  FROM {{ ref('silver_tracks_latest') }}
),

dim_tracks AS (
  SELECT
    -- Identifiers
    track_id,
    track_name,
    track_uri,
    track_href,

    -- Metrics
    track_popularity,
    duration_ms,
    duration_minutes,

    -- Business enrichment: popularity categorization
    CASE
      WHEN track_popularity >= 80 THEN 'Very Popular'
      WHEN track_popularity >= 60 THEN 'Popular'
      WHEN track_popularity >= 40 THEN 'Moderate'
      WHEN track_popularity >= 20 THEN 'Low'
      ELSE 'Very Low'
    END AS popularity_category,

    -- Business enrichment: duration categorization
    CASE
      WHEN duration_minutes < 2 THEN 'Short'
      WHEN duration_minutes < 4 THEN 'Medium'
      WHEN duration_minutes < 6 THEN 'Long'
      ELSE 'Very Long'
    END AS duration_category,

    -- Flags
    explicit,
    is_local,

    -- Position
    disc_number,
    track_number,

    -- External IDs
    isrc,

    -- Foreign Keys
    album_id,
    artist_id,

    -- Metadata
    artist_count,

    -- Business enrichment: collaboration flag
    CASE WHEN artist_count > 1 THEN TRUE ELSE FALSE END AS is_collaboration

  FROM silver
  ORDER BY track_id DESC
)

SELECT * FROM dim_tracks
