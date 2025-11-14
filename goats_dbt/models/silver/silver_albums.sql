{{ config(materialized="table") }}

select distinct
    album->>'album_id' as album_id,
    album->>'album_name' as album_name,
    album->>'album_type' as album_type,
    album->>'release_date' as release_date,
    album->>'release_date_precision' as release_date_precision,
    (album->>'total_tracks')::int as total_tracks,
    album->>'spotify_url' as spotify_url,
    album->>'uri' as uri
from {{ ref('stg_recently_played') }}
