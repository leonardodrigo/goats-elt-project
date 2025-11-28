{{ config(
    materialized='table',
) }}

WITH input AS (
  SELECT
    track->'album' as album,
    loaded_at
  FROM {{ source('bronze','bronze_recently_played') }}
  WHERE track->'album'->>'id' IS NOT NULL
),

latest_albums AS (
  SELECT DISTINCT ON (album->>'id')
    album->>'id' as album_id,
    album->>'name' as album_name,
    album->>'uri' as album_uri,
    album->>'album_type' as album_type,
    album->>'release_date' as album_release_date,
    EXTRACT(YEAR FROM (album->>'release_date')::DATE) as album_release_year,
    (album->>'total_tracks')::INTEGER as album_total_tracks,
    album->'images'->0->>'url' as album_image_url
  FROM input
  ORDER BY album->>'id', loaded_at DESC
)

SELECT * FROM latest_albums
ORDER BY album_id
