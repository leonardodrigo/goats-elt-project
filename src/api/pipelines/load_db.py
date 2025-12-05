import json
from src.api.clients.postgres import get_db_connection
import logging
from enum import Enum
from src.api.clients.storage import CloudStorageClient
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class Schema(Enum):
    RAW = "raw"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


def schemas_init():
    """Create raw, bronze, silver, and gold schemas if they do not exist."""
    with tracer.start_as_current_span("db.schemas_init") as span:
        span.set_attribute("db.schema_count", len(Schema))
        
        with get_db_connection() as conn:
            cursor = conn.cursor()

            for schema in Schema:
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema.value};")

        logger.info("Schemas verified:", ", ".join(s.value for s in Schema))


def init_bronze_table():
    """Create schema and bronze table if they don't exist"""
    with tracer.start_as_current_span("db.init_bronze_table") as span:
        span.set_attribute("db.table", "raw.raw_recently_played")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()

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
    with tracer.start_as_current_span("db.insert_raw_data") as span:
        span.set_attribute("db.table", "raw.raw_recently_played")
        span.set_attribute("db.records_count", len(items))
        
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
    with tracer.start_as_current_span("load_db"):
        tracer.set_attribute("bucket_name", bucket_name)
        schemas_init()
        tracer.add_event("Schemas initialized")
        init_bronze_table()
        tracer.add_event("Bronze table initialized")

        if bucket_name is None:
            raise ValueError("bucket_name must be provided for GCS")

        gcs_client = CloudStorageClient()
        if object_name is None:
            object_name = gcs_client.get_most_recent_gcs_object(bucket_name)
            tracer.get_current_span().set_attribute("object_name", object_name)
            if object_name is None:
                raise ValueError("No files found in the GCS bucket.")

        with tracer.start_as_current_span("gcs.download_json") as span:
            span.set_attribute("gcs.bucket", bucket_name)
            span.set_attribute("gcs.object", object_name)
            data: dict = gcs_client.download_json(bucket_name, object_name)

        items = data.get("items", [])
        tracer.get_current_span().set_attribute("items_count", len(items))

        logger.info("Starting insert raw data")
        insert_raw_data(object_name, items)
        logger.info("Loading done")
