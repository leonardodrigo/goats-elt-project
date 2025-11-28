{{ config(
    materialized='table',
) }}

WITH bronze AS (
    SELECT
        track,
        played_at,
        context,
        loaded_at
    FROM {{ ref('bronze_recently_played') }}
),

deduped AS (
    SELECT DISTINCT ON (track ->> 'id', played_at)
    -- Primary Key (combination of track_id + played_at)
        track ->> 'id' || '_' || played_at AS play_id,

        -- Foreign Keys
        track ->> 'id' AS track_id,
        track -> 'album' ->> 'id' AS album_id,
        track -> 'artists' -> 0 ->> 'id' AS artist_id,

        -- Time dimensions
        played_at,
        played_at::DATE AS played_date,
        EXTRACT(HOUR FROM played_at) AS played_hour,

        -- Context
        context ->> 'type' AS context_type,
        context ->> 'uri' AS context_uri,
        SPLIT_PART(context ->> 'uri', ':', 3) AS context_id

    FROM bronze
    ORDER BY track ->> 'id', played_at ASC, loaded_at DESC
)

SELECT * FROM deduped
