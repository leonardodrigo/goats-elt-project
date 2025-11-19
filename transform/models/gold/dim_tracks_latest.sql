{{ config(
    materialized='table',
) }}

WITH bronze AS (
  SELECT 
    track
  FROM {{ source('sources','bronze_recently_played') }}
  WHERE track->>'id' IS NOT NULL
),

extracted AS (
  SELECT
    track->>'id' AS track_id,
    track->>'name' AS track_name,
    track->>'uri' AS track_uri,
    track->>'href' AS track_href,
    track->>'popularity' AS popularity,
    track->>'duration_ms' AS duration_ms,
    track->>'explicit' AS explicit,
    track->>'is_local' AS is_local,
    track->>'disc_number' AS disc_number,
    track->>'track_number' AS track_number,
    track->'external_ids'->>'isrc' AS isrc,
    track->'album'->>'id' AS album_id,
    track->'artists'->0->>'id' AS artist_id,
    track->'artists' AS artists
  FROM bronze
),

latest_tracks AS (
  SELECT
    -- Identifiers
    track_id,
    track_name,
    track_uri,
    track_href,
    
    -- Metrics
    popularity::INTEGER AS track_popularity,
    duration_ms::INTEGER AS duration_ms,
    ROUND(duration_ms::NUMERIC / 60000, 2) AS duration_minutes,
    
    -- Flags
    explicit::BOOLEAN AS explicit,
    is_local::BOOLEAN AS is_local,
    
    -- Position
    disc_number::INTEGER AS disc_number,
    track_number::INTEGER AS track_number,
    
    -- External IDs
    isrc,
    
    -- Foreign Keys
    album_id,
    artist_id,
    
    -- Metadata
    jsonb_array_length(artists) AS artist_count    
  FROM extracted
  ORDER BY track_id DESC
)

SELECT * FROM latest_tracks
