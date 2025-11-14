{{ config(materialized='table') }}

with plays as (
    select track_id, played_at
    from {{ ref('silver_plays') }}
),

track_meta as (
    select 
        t.track_id,
        a.album_id,
        a.album_name,
        a.album_type,
        a.release_date
    from {{ ref('silver_tracks') }} t
    left join {{ ref('silver_albums') }} a
        on t.track_id = a.album_id  -- replace if different schema
)

select
    p.track_id,
    count(*) as play_count,
    min(played_at) as first_play,
    max(played_at) as last_play
from plays p
group by p.track_id
