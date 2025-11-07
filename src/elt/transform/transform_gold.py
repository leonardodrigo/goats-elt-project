import psycopg2
from psycopg2.extras import execute_values
from src.elt.transform.initalization_db import get_db_connection


def create_gold_tables():
    """Create denormalized and aggregated gold tables."""
    conn = get_db_connection()
    cur = conn.cursor()

    # --- Listening history (joined and flattened)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gold_listening_history AS
        SELECT
            p.played_at,
            t.track_id,
            a.album_name,
            ar.artist_name,
            ar.artist_id,
            al.album_id
        FROM silver_plays p
        JOIN silver_tracks t ON p.track_id = t.track_id
        JOIN silver_track_artists ta ON t.track_id = ta.track_id
        JOIN silver_artists ar ON ta.artist_id = ar.artist_id
        JOIN silver_albums al ON al.album_id IS NOT NULL; -- add track-album relation later if available
    """)

    # --- Artist popularity (aggregated)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gold_artist_popularity AS
        SELECT
            ar.artist_id,
            ar.artist_name,
            COUNT(p.track_id) AS total_plays,
            MIN(p.played_at) AS first_play,
            MAX(p.played_at) AS last_play
        FROM silver_plays p
        JOIN silver_track_artists ta ON p.track_id = ta.track_id
        JOIN silver_artists ar ON ta.artist_id = ar.artist_id
        GROUP BY ar.artist_id, ar.artist_name;
    """)

    # --- Album summary (aggregated)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gold_album_summary AS
        SELECT
            al.album_id,
            al.album_name,
            COUNT(DISTINCT p.track_id) AS unique_tracks_played,
            COUNT(p.track_id) AS total_plays
        FROM silver_plays p
        JOIN silver_tracks t ON p.track_id = t.track_id
        JOIN silver_albums al ON al.album_id IS NOT NULL
        GROUP BY al.album_id, al.album_name;
    """)

    # --- Daily listening stats
    cur.execute("""
        CREATE TABLE IF NOT EXISTS gold_daily_activity AS
        SELECT
            DATE(p.played_at) AS play_date,
            COUNT(*) AS total_plays,
            COUNT(DISTINCT ta.artist_id) AS unique_artists
        FROM silver_plays p
        JOIN silver_track_artists ta ON p.track_id = ta.track_id
        GROUP BY play_date
        ORDER BY play_date;
    """)

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    create_gold_tables()
