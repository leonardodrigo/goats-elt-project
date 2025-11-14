{{ config(materialized="table") }}

select distinct
    track_id,
    played_at
from {{ ref('stg_recently_played') }}
