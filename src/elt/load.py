from minio import Minio
from minio.error import S3Error
import io
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "spotify-data")


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


def load_data_to_bucket(
    context: StorageContext, object_name: str, data: dict
) -> None:
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
