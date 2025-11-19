{{ config(
    materialized='table'
) }}

WITH staged_plays AS (
  SELECT * FROM {{ ref('silver_plays_latest') }}
),

deduped_plays AS (
  SELECT DISTINCT ON (play_id)
    *
  FROM staged_plays
  ORDER BY play_id DESC
)

SELECT
  -- Primary Key
  play_id,
  
  -- Foreign Keys (to dimensions)
  track_id,
  album_id,
  artist_id,
  played_date,
  
  played_at,
  played_hour,
  context_type,
  context_id,
  
  -- Derived Measures
  CASE 
    WHEN played_hour BETWEEN 6 AND 11 THEN 'Morning'
    WHEN played_hour BETWEEN 12 AND 17 THEN 'Afternoon'
    WHEN played_hour BETWEEN 18 AND 21 THEN 'Evening'
    ELSE 'Night'
  END AS time_of_day

FROM deduped_plays
