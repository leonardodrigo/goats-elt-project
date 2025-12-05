from fastapi import APIRouter
from src.api.pipelines.load_db import handler
import os

router = APIRouter()

BUCKET_NAME = os.getenv("BUCKET_NAME")


@router.post(
    "/load_db",
    description="load date into the postgres database",
)
def load_db():
    handler(bucket_name=BUCKET_NAME)
    return {"status": "ok"}
