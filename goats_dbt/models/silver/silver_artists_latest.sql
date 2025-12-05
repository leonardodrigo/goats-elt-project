{{ config(
    materialized='table',
) }}

WITH bronze AS (
    SELECT
        track -> 'artists' -> 0 AS artist,
        loaded_at
    FROM {{ ref('bronze_recently_played') }}
    WHERE track -> 'artists' -> 0 ->> 'id' IS NOT null
),

latest_artists AS (
    SELECT DISTINCT ON (artist ->> 'id')
        artist ->> 'id' AS artist_id,
        artist ->> 'name' AS artist_name,
        artist ->> 'uri' AS artist_uri,
        artist ->> 'href' AS artist_href,
        artist ->> 'type' AS artist_type,
        artist -> 'external_urls' ->> 'spotify' AS artist_spotify_url
    FROM bronze
    ORDER BY artist ->> 'id', loaded_at DESC
)

SELECT * FROM latest_artists
