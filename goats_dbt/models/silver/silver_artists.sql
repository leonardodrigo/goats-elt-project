{{ config(materialized="table") }}

with exploded as (
    select jsonb_array_elements(artists) as artist
    from {{ ref('stg_recently_played') }}
)

select distinct
    artist->>'artist_id' as artist_id,
    artist->>'artist_name' as artist_name,
    artist->>'spotify_url' as spotify_url,
    artist->>'href' as href,
    artist->>'uri' as uri
from exploded
