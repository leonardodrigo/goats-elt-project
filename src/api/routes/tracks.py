from fastapi import APIRouter
from src.api.pipelines.batch import extract_and_load_recently_played_tracks
from src.api.core.utils import get_cached_spotify_client, get_cached_storage_client

router = APIRouter()


@router.post(
    "/recently_played_tracks",
    description="Extracts the last 50 played tracks and loads into GCS",
)
def el_recently_played_tracks():
    spotify_client = get_cached_spotify_client()
    storage_client = get_cached_storage_client()

    extract_and_load_recently_played_tracks(
        spotify_client=spotify_client, storage_client=storage_client, limit=50
    )

    return {"status": "ok"}
