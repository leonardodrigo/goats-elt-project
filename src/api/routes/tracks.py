from fastapi import APIRouter
from src.api.pipelines.batch import extract_and_load_recently_played_tracks
from src.api.core.utils import get_cached_spotify_client, get_cached_minio_client

router = APIRouter()


@router.post(
    "/recently_played_tracks",
    description="Extracts the last 50 played tracks and loads into Minio",
)
def el_recently_played_tracks():
    spotify_client = get_cached_spotify_client()
    minio_client = get_cached_minio_client()

    extract_and_load_recently_played_tracks(
        spotify_client=spotify_client, minio_client=minio_client, limit=50
    )

    return {"status": "ok"}
