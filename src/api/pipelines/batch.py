from src.api.clients.storage import CloudStorageClient
from src.api.clients.spotify import SpotifyClient
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

BUCKET_NAME = os.getenv("BUCKET_NAME")


def extract_and_load_recently_played_tracks(
    spotify_client: SpotifyClient, storage_client: CloudStorageClient, limit: int = 50
) -> None:
    recently_played_tracks = spotify_client.fetch_recently_played_tracks(limit=limit)
    logger.info("Extracted recently played tracks")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    object_name = f"recently_played_tracks_{timestamp}.json"

    storage_client.upload_json(
        bucket_name=BUCKET_NAME, blob_name=object_name, data=recently_played_tracks
    )
