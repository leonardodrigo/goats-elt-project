from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime
import json
from psycopg2.extras import execute_values

# 👇 import from your initialization file
from src.elt.transform.initalization_db import get_db_connection, create_silver_tables


# ------------------------------------------------------------
# 1. Parse JSON
# ------------------------------------------------------------
def parse_json(json_path: str | Path) -> List[Dict[str, Any]]:
    """Loads a Spotify 'recently played' JSON file and extracts album/artist/play data."""
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    parsed = []

    for item in items:
        track = item["track"]
        album = track["album"]
        artists = track["artists"]
        album_artists = album.get("artists", [])
        played_at = datetime.fromisoformat(item["played_at"].replace("Z", "+00:00"))

        parsed.append({
            "track_id": track["id"],
            "played_at": played_at,
            "album": {
                "album_id": album["id"],
                "album_name": album["name"],
                "album_type": album.get("album_type"),
                "release_date": album.get("release_date"),
                "release_date_precision": album.get("release_date_precision"),
                "total_tracks": album.get("total_tracks"),
                "spotify_url": album["external_urls"]["spotify"],
                "uri": album["uri"],
            },
            "artists": [
                {
                    "artist_id": a["id"],
                    "artist_name": a["name"],
                    "spotify_url": a["external_urls"]["spotify"],
                    "href": a["href"],
                    "uri": a["uri"],
                }
                for a in artists
            ],
            "album_artists": [
                {
                    "artist_id": a["id"],
                    "artist_name": a["name"],
                    "spotify_url": a["external_urls"]["spotify"],
                    "href": a["href"],
                    "uri": a["uri"],
                }
                for a in album_artists
            ],
        })
    return parsed


# ------------------------------------------------------------
# 2. Insert data into Silver tables
# ------------------------------------------------------------
def insert_silver_albums_artists_plays(data: List[Dict[str, Any]]):
    """Insert albums, artists, track-artist links, and plays into Silver tables."""
    if not data:
        print("No data to insert.")
        return

    conn = get_db_connection()
    cur = conn.cursor()

    albums, artists, track_artists, tracks, plays = {}, {}, [], set(), []

    for record in data:
        # Track
        tracks.add(record["track_id"])

        # Album
        album = record["album"]
        albums[album["album_id"]] = (
            album["album_id"],
            album["album_name"],
            album["album_type"],
            album["release_date"],
            album["release_date_precision"],
            album["total_tracks"],
            album["spotify_url"],
            album["uri"],
        )

        # Track artists
        for artist in record["artists"]:
            artists[artist["artist_id"]] = (
                artist["artist_id"],
                artist["artist_name"],
                artist["spotify_url"],
                artist["href"],
                artist["uri"],
            )
            track_artists.append((record["track_id"], artist["artist_id"]))

        # Album artists (reuse artist table)
        for artist in record["album_artists"]:
            artists[artist["artist_id"]] = (
                artist["artist_id"],
                artist["artist_name"],
                artist["spotify_url"],
                artist["href"],
                artist["uri"],
            )

        # Plays
        plays.append((record["track_id"], record["played_at"]))

    # --- Insert albums ---
    execute_values(
        cur,
        """
        INSERT INTO silver_albums (
            album_id, album_name, album_type, release_date,
            release_date_precision, total_tracks, spotify_url, uri
        )
        VALUES %s
        ON CONFLICT (album_id) DO UPDATE SET
            album_name = EXCLUDED.album_name,
            album_type = EXCLUDED.album_type,
            release_date = EXCLUDED.release_date,
            release_date_precision = EXCLUDED.release_date_precision,
            total_tracks = EXCLUDED.total_tracks,
            spotify_url = EXCLUDED.spotify_url,
            uri = EXCLUDED.uri;
        """,
        list(albums.values())
    )

    # --- Insert artists ---
    execute_values(
        cur,
        """
        INSERT INTO silver_artists (
            artist_id, artist_name, spotify_url, href, uri
        )
        VALUES %s
        ON CONFLICT (artist_id) DO UPDATE SET
            artist_name = EXCLUDED.artist_name,
            spotify_url = EXCLUDED.spotify_url,
            href = EXCLUDED.href,
            uri = EXCLUDED.uri;
        """,
        list(artists.values())
    )

    # --- Insert tracks ---
    execute_values(
        cur,
        """
        INSERT INTO silver_tracks (track_id)
        VALUES %s
        ON CONFLICT (track_id) DO NOTHING;
        """,
        [(t,) for t in tracks]
    )

    # --- Insert track-artist links ---
    execute_values(
        cur,
        """
        INSERT INTO silver_track_artists (track_id, artist_id)
        VALUES %s
        ON CONFLICT (track_id, artist_id) DO NOTHING;
        """,
        track_artists
    )

    # --- Insert play events ---
    execute_values(
        cur,
        """
        INSERT INTO silver_plays (track_id, played_at)
        VALUES %s
        ON CONFLICT (track_id, played_at) DO NOTHING;
        """,
        plays
    )

    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {len(albums)} albums, {len(artists)} artists, {len(track_artists)} links, and {len(plays)} plays.")


# ------------------------------------------------------------
# 3. Run
# ------------------------------------------------------------
if __name__ == "__main__":
    # Ensure tables exist before inserting
    create_silver_tables()

    data = parse_json("test/recently_played.json")
    insert_silver_albums_artists_plays(data)
