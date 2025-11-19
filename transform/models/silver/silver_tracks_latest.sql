{{ config(materialized='table') }}

WITH bronze AS (
  SELECT 
    track,
    loaded_at
  FROM {{ source('sources','bronze_recently_played') }}
  WHERE track->>'id' IS NOT NULL
),

latest_tracks AS (
  SELECT DISTINCT ON (track->>'id')
    track->>'id' AS track_id,
    track->>'name' AS track_name,
    track->>'uri' AS track_uri,
    track->>'href' AS track_href,
    (track->>'popularity')::INTEGER AS track_popularity,
    (track->>'duration_ms')::INTEGER AS duration_ms,
    ROUND((track->>'duration_ms')::NUMERIC / 60000, 2) AS duration_minutes,
    (track->>'explicit')::BOOLEAN AS explicit,
    (track->>'is_local')::BOOLEAN AS is_local,
    (track->>'disc_number')::INTEGER AS disc_number,
    (track->>'track_number')::INTEGER AS track_number,
    track->'external_ids'->>'isrc' AS isrc,
    track->'album'->>'id' AS album_id,
    track->'artists'->0->>'id' AS artist_id,
    jsonb_array_length(track->'artists') AS artist_count,
    loaded_at
  FROM bronze
  ORDER BY track->>'id', loaded_at DESC
)

SELECT * FROM latest_tracks
