from datetime import datetime
from fastapi import APIRouter
from src.api.pipelines.batch import extract_and_load_recently_played_tracks
from src.api.core.utils import get_cached_spotify_client, get_cached_minio_client

router = APIRouter()


@router.post(
    "/recently_played_tracks",
    description="Extracts the last 50 played tracks and loads into Minio",
)
def el_recently_played_tracks() -> dict:
    spotify_client = get_cached_spotify_client()
    minio_client = get_cached_minio_client()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    object_name = f"recently_played_tracks_{timestamp}.json"

    extract_and_load_recently_played_tracks(
        spotify_client=spotify_client,
        minio_client=minio_client,
        object_name=object_name,
        limit=50,
    )
    # used later on in load task of the Airflow ELT pipeline with xcoms
    return {
        "status": "ok",
        "object_name": object_name,
        "bucket_name": minio_client.bucket_name,
    }
