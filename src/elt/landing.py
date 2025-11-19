from minio import Minio
from minio.error import S3Error
import io
import json
import logging
import os
from datetime import datetime
from db_helper import get_db_connection



logger = logging.getLogger(__name__)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")


class StorageContext:
    def __init__(self, endpoint: str, access_key: str, secret_key: str) -> None:
        self.client = Minio(
            endpoint, access_key=access_key, secret_key=secret_key, secure=False
        )

def create_bucket(context: StorageContext) -> None:
    try:
        if not context.client.bucket_exists(MINIO_BUCKET):
            context.client.make_bucket(MINIO_BUCKET)
            logger.info(f"Bucket '{MINIO_BUCKET}' created successfully")
        else:
            logger.info(f"Bucket '{MINIO_BUCKET}' already exists")
    except S3Error as e:
        logger.error(f"Error creating bucket {MINIO_BUCKET}: {e}")
        raise

def load_data_to_bucket(context: StorageContext, object_name: str, data: dict) -> None:
    try:
        json_data = json.dumps(data, indent=2)
        data_stream = io.BytesIO(json_data.encode("utf-8"))

        context.client.put_object(
            MINIO_BUCKET,
            object_name,
            data_stream,
            length=len(json_data.encode("utf-8")),
            content_type="application/json",
        )
        logger.info(f"Data loaded successfully to {MINIO_BUCKET}/{object_name}")
    except S3Error as e:
        if e.code == "NoSuchBucket":
            logger.warning(f"Bucket {MINIO_BUCKET} does not exist. Creating bucket...")
            create_bucket(context)
            load_data_to_bucket(context, object_name, data)

def init_log_landing_loading():
    #Create the log_landing_loading table if it doesn't exist
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public.log_landing_loading (
                id SERIAL PRIMARY KEY,
                object_name VARCHAR(255) UNIQUE NOT NULL,
                bucket_name VARCHAR(255) NOT NULL,
                landed_at TIMESTAMP NOT NULL,
                loaded_at TIMESTAMP,
                status VARCHAR(50) NOT NULL,
            );
        """)
        logger.info("Tracking table initialized successfully")
    
def insert_log_landing_loading(object_name, timestamp):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO public.log_landing_loading
            (object_name, bucket_name, landed_at, loaded_at, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            object_name,
            MINIO_BUCKET,
            timestamp,
            None,
            "landed"
        ))

def update_log_landed(object_name: str, timestamp_loaded: datetime) -> None:
    """Update PostgreSQL log table when data lands in MinIO"""

    init_log_landing_loading()

    insert_log_landing_loading(object_name, timestamp_loaded)

def handler(data: dict):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    object_name = f"tracks_{timestamp}.json"

    ctx = StorageContext(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
    )

    load_data_to_bucket(ctx, object_name, data)
    logger.info("Data load process completed successfully")

    """ Updates the log so that later can be checken when landing happened
    , but loading didn't """
    update_log_landed(object_name, timestamp)
    
    return object_name
