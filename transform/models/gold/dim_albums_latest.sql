{{ config(materialized='table')}}

SELECT
  album_id,
  album_name,
  album_uri,
  album_type,
  album_release_date,
  album_release_year,
  album_total_tracks,
  album_image_url,
  
  -- Decade categorization
  CASE 
    WHEN album_release_year >= 2020 THEN '2020s'
    WHEN album_release_year >= 2010 THEN '2010s'
    WHEN album_release_year >= 2000 THEN '2000s'
    WHEN album_release_year >= 2000 THEN '1990s'
    WHEN album_release_year >= 2000 THEN '1980s'
    WHEN album_release_year >= 2000 THEN '1970s'
    WHEN album_release_year >= 2000 THEN '1960s'
    ELSE 'Pre-1960s'
  END AS release_decade
  
FROM {{ ref('silver_albums_latest') }}
WHERE album_id IS NOT NULL
