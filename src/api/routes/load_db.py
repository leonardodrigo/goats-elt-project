from fastapi import APIRouter
from src.api.pipelines.load_db import handler

router = APIRouter()


@router.post(
    "/load_db",
    description="load date into the postgres database",
)
def load_db():
    handler(object_name="recently_played_tracks_20251121_122638.json")
    return {"status": "ok"}
