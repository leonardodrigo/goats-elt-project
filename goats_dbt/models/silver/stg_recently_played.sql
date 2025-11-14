{{ config(materialized="view") }}

select
    data->>'track_id' as track_id,
    (data->>'played_at')::timestamp as played_at,
    data->'album' as album,
    data->'artists' as artists,
    data->'album_artists' as album_artists
from {{ source('raw', 'raw_recently_played') }}
