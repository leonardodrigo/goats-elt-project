import boto3
import json
from src.api.clients.postgres import get_db_connection
import os
import logging
from enum import Enum

logger = logging.getLogger(__name__)

# ==== MinIO / S3 settings ====
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")


s3 = boto3.client(
    "s3",
    endpoint_url=f"http://{MINIO_ENDPOINT}",
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
)


def read_file(key: str):
    """Read file contents from S3/MinIO"""
    response = s3.get_object(Bucket=MINIO_BUCKET, Key=key)
    return response["Body"].read().decode("utf-8")


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

    print("Schemas verified:", ", ".join(s.value for s in Schema))


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


def get_most_recent_object():
    """Return the key (filename) of the most recently modified object in the bucket."""

    logger.info(f"Minio bucket being used to get all objects: {MINIO_BUCKET}")

    response = s3.list_objects_v2(Bucket=MINIO_BUCKET)

    if "Contents" not in response:
        return None

    # Sort objects by LastModified timestamp, descending
    latest_obj = max(response["Contents"], key=lambda obj: obj["LastModified"])
    return latest_obj["Key"]


def handler(object_name=None):
    schemas_init()

    init_bronze_table()

    # get newest file automatically
    if object_name is None:
        object_name = get_most_recent_object()

    file_contents = read_file(object_name)

    data = json.loads(file_contents)

    logger.info(f"data: {data}")

    # Extract items array for actual data
    items = data.get("items", [])

    logger.info(f"items: {items}")

    insert_raw_data(object_name, items)

    print("Loading done")
