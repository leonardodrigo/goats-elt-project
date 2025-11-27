from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from src.api.core.config import POSTGRES_RAW_TRACKS_TABLE
from src.api.core.utils import get_cached_postgres_client, get_cached_minio_client

router = APIRouter()


class LoadRequest(BaseModel):
    object_name: str
    pg_schema: str = "raw"
    table: str = POSTGRES_RAW_TRACKS_TABLE
    data_column: Optional[str] = "data"
    other_columns: Optional[List[str]] = None
    file_format: str = "jsonl"


@router.post(
    "/load",
    description="Loads transformed data into Postgres",
)
def load_to_postgres(payload: LoadRequest):
    postgres = get_cached_postgres_client()
    minio = get_cached_minio_client()
    try:
        postgres.insert_json_from_minio(
            minio_client=minio,
            object_name=payload.object_name,
            schema=payload.pg_schema,
            table=payload.table,
            data_column=payload.data_column,
            other_columns=payload.other_columns,
            file_format=payload.file_format,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"success": True}
