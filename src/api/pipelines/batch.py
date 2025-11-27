from src.api.clients.minio import MinIOClient
from src.api.clients.spotify import SpotifyClient
import logging
import os

logger = logging.getLogger(__name__)

BUCKET_NAME = os.getenv("MINIO_DEFAULT_BUCKET")


def load_data_to_bucket(client: MinIOClient, object_name: str, data: dict) -> None:
    client.upload_json(object_name, data)


def extract_and_load_recently_played_tracks(
    spotify_client: SpotifyClient,
    minio_client: MinIOClient,
    object_name: str,
    limit: int = 50,
) -> None:
    recently_played_tracks = spotify_client.fetch_recently_played_tracks(limit=limit)
    logger.info("Extracted recently played tracks")

    load_data_to_bucket(
        client=minio_client, object_name=object_name, data=recently_played_tracks
    )
