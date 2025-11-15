{{ config(materialized="view") }}

select *
from {{ source('goats_elt', 'spotify_plays_raw') }}
