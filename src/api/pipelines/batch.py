from src.api.clients.storage import CloudStorageClient
from src.api.clients.spotify import SpotifyClient
from datetime import datetime
import logging
import os
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

BUCKET_NAME = os.getenv("BUCKET_NAME")


def extract_and_load_recently_played_tracks(
    spotify_client: SpotifyClient, storage_client: CloudStorageClient, limit: int = 50
) -> None:
    with tracer.start_as_current_span("extract_and_load") as span:
        span.set_attribute("pipeline.stage", "extract")
        span.set_attribute("data.source", "spotify_api")
        span.set_attribute("data.limit", limit)
        
        with tracer.start_as_current_span("spotify.fetch_recently_played"):
            recently_played_tracks = spotify_client.fetch_recently_played_tracks(limit=limit)
            track_count = len(recently_played_tracks.get("items", []))
            span.set_attribute("tracks.count", track_count)
            logger.info("Extracted recently played tracks")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        object_name = f"recently_played_tracks_{timestamp}.json"

        with tracer.start_as_current_span("gcs.upload_json") as upload_span:
            upload_span.set_attribute("gcs.bucket", BUCKET_NAME)
            upload_span.set_attribute("gcs.object", object_name)
            storage_client.upload_json(
                bucket_name=BUCKET_NAME, blob_name=object_name, data=recently_played_tracks
            )
