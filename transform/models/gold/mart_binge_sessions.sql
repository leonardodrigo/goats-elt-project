{{ config(materialized='table')}}

WITH plays_with_gaps AS (
  SELECT
    f.play_id,
    f.played_at,
    f.artist_id,
    f.track_id,
    dt.duration_minutes,

    -- Calculate time since previous play
    f.played_at - LAG(f.played_at) OVER (ORDER BY f.played_at) AS gap_since_last_play
  FROM {{ ref('fct_plays') }} f
  JOIN {{ ref('dim_tracks_latest') }} dt ON f.track_id = dt.track_id
),

session_markers AS (
  SELECT
    *,
    -- New session if gap > 30 minutes
    CASE
      WHEN gap_since_last_play > INTERVAL '30 minutes' OR gap_since_last_play IS NULL
      THEN 1
      ELSE 0
    END AS is_new_session
  FROM plays_with_gaps
),

sessions AS (
  SELECT
    *,
    SUM(is_new_session) OVER (ORDER BY played_at) AS session_id
  FROM session_markers
),

session_summary AS (
  SELECT
    session_id,
    MIN(played_at) AS session_start,
    MAX(played_at) AS session_end,
    COUNT(*) AS tracks_in_session,
    COUNT(DISTINCT artist_id) AS unique_artists_in_session,
    SUM(duration_minutes) AS session_duration_minutes,

    EXTRACT(EPOCH FROM (MAX(played_at) - MIN(played_at))) / 60 AS session_length_minutes
  FROM sessions
  GROUP BY session_id
)

SELECT
  session_start,
  session_end,
  tracks_in_session,
  unique_artists_in_session,
  ROUND(session_duration_minutes, 1) AS music_duration_minutes,
  ROUND(session_length_minutes, 1) AS session_length_minutes,

  CASE
    WHEN tracks_in_session >= 20 THEN 'Marathon'
    WHEN tracks_in_session >= 10 THEN 'Long Session'
    WHEN tracks_in_session >= 5 THEN 'Regular Session'
    ELSE 'Quick Listen'
  END AS session_type,

  TO_CHAR(session_start, 'Day') AS day_of_week,
  EXTRACT(HOUR FROM session_start) AS start_hour

FROM session_summary
WHERE tracks_in_session > 1  -- Exclude single plays
ORDER BY session_start DESC
