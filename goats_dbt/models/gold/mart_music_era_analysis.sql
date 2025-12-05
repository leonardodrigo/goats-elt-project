{{ config(materialized='table') }}

SELECT
    dal.release_decade,
    COUNT(*) AS total_plays,
    COUNT(DISTINCT f.track_id) AS unique_tracks,
    COUNT(DISTINCT f.artist_id) AS unique_artists,
    SUM(dt.duration_minutes) AS total_minutes,

    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS percentage_of_listening,

    -- Top artist per decade
    MODE() WITHIN GROUP (ORDER BY f.artist_id) AS most_played_artist_id,

    -- Average release year
    ROUND(AVG(dal.album_release_year), 0) AS avg_release_year

FROM {{ ref('fct_plays') }} AS f
INNER JOIN {{ ref('dim_albums_latest') }} AS dal ON f.album_id = dal.album_id
INNER JOIN {{ ref('dim_tracks_latest') }} AS dt ON f.track_id = dt.track_id
GROUP BY dal.release_decade
ORDER BY total_plays DESC
