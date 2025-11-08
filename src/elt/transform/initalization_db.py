# init_silver_tables.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv("infra/.env")

def get_db_connection():
    """Establish PostgreSQL connection using .env credentials."""
    load_dotenv()
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )

def create_silver_tables():
    """Initialize all Silver layer tables."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS silver_tracks (
            track_id TEXT PRIMARY KEY
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS silver_albums (
            album_id TEXT PRIMARY KEY,
            album_name TEXT,
            album_type TEXT,
            release_date TEXT,
            release_date_precision TEXT,
            total_tracks INT,
            spotify_url TEXT,
            uri TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS silver_artists (
            artist_id TEXT PRIMARY KEY,
            artist_name TEXT,
            spotify_url TEXT,
            href TEXT,
            uri TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS silver_track_artists (
            track_id TEXT REFERENCES silver_tracks(track_id),
            artist_id TEXT REFERENCES silver_artists(artist_id),
            PRIMARY KEY (track_id, artist_id)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS silver_plays (
            track_id TEXT REFERENCES silver_tracks(track_id),
            played_at TIMESTAMPTZ NOT NULL,
            PRIMARY KEY (track_id, played_at)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    create_silver_tables()
