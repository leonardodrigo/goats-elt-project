{{ config(materialized="table") }}

with exploded as (
    select
        track_id,
        jsonb_array_elements(artists) as artist
    from {{ ref('stg_recently_played') }}
)

select distinct
    track_id,
    artist->>'artist_id' as artist_id
from exploded
