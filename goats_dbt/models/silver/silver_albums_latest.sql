{{ config(
    materialized='table',
) }}

WITH input AS (
    SELECT
        track -> 'album' AS album,
        loaded_at
    FROM {{ ref('bronze_recently_played') }}
    WHERE track -> 'album' ->> 'id' IS NOT null
),

latest_albums AS (
    SELECT DISTINCT ON (album ->> 'id')
        album ->> 'id' AS album_id,
        album ->> 'name' AS album_name,
        album ->> 'uri' AS album_uri,
        album ->> 'album_type' AS album_type,
        album ->> 'release_date' AS album_release_date,
        EXTRACT(YEAR FROM (album ->> 'release_date')::DATE) AS album_release_year,
        (album ->> 'total_tracks')::INTEGER AS album_total_tracks,
        album -> 'images' -> 0 ->> 'url' AS album_image_url
    FROM input
    ORDER BY album ->> 'id', loaded_at DESC
)

SELECT * FROM latest_albums
ORDER BY album_id
