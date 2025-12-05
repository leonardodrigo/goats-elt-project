import json
from src.api.clients.postgres import get_db_connection
import logging
from enum import Enum
from src.api.clients.storage import CloudStorageClient

logger = logging.getLogger(__name__)


class Schema(Enum):
    RAW = "raw"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


def schemas_init():
    """Create raw, bronze, silver, and gold schemas if they do not exist."""

    with get_db_connection() as conn:
        cursor = conn.cursor()

        for schema in Schema:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema.value};")

    logger.info("Schemas verified:", ", ".join(s.value for s in Schema))


def init_bronze_table():
    """Create schema and bronze table if they don't exist"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create bronze table met alleen top-level velden als kolommen
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS raw.raw_recently_played (
                id SERIAL PRIMARY KEY,
                source_file TEXT NOT NULL,
                loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

                -- Top-level velden uit 'items'
                track JSONB,
                played_at TIMESTAMPTZ,
                context JSONB
            );
        """)


def insert_raw_data(file_key: str, items: list):
    """Insert each item from the API response into bronze layer"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        for item in items:
            cursor.execute(
                """
                INSERT INTO raw.raw_recently_played (
                    source_file,
                    track,
                    played_at,
                    context
                    ) VALUES (%s, %s, %s, %s)
                """,
                (
                    file_key,
                    json.dumps(item.get("track")),
                    item.get("played_at"),
                    json.dumps(item.get("context")),
                ),
            )


def handler(object_name=None, bucket_name=None):
    schemas_init()
    init_bronze_table()

    if bucket_name is None:
        raise ValueError("bucket_name must be provided for GCS")

    gcs_client = CloudStorageClient()
    if object_name is None:
        object_name = gcs_client.get_most_recent_gcs_object(bucket_name)
        if object_name is None:
            raise ValueError("No files found in the GCS bucket.")

    data: dict = gcs_client.download_json(bucket_name, object_name)

    logger.info(f"data: {data}")
    items = data.get("items", [])

    logger.info("Starting insert raw data")
    insert_raw_data(object_name, items)
    logger.info("Loading done")
