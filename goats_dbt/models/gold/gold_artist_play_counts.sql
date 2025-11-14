{{ config(materialized='table') }}

with plays as (
    select track_id, played_at
    from {{ ref('silver_plays') }}
),

track_artists as (
    select track_id, artist_id
    from {{ ref('silver_track_artists') }}
)

select
    a.artist_id,
    count(*) as total_plays
from plays p
join track_artists a
  on p.track_id = a.track_id
group by a.artist_id
