from fastapi import APIRouter
from src.api.pipelines.load_db import handler

router = APIRouter()


@router.post(
    "/load_db",
    description="load date into the postgres database",
)
def load_db():
    handler()
    return {"status": "ok"}
