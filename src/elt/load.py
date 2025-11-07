from minio import Minio
from minio.error import S3Error
import io
import json
import logging

logger = logging.getLogger(__name__)


class MinioContext:
    def __init__(self, endpoint: str, access_key: str, secret_key: str) -> None:
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )


def create_bucket(context: MinioContext, bucket_name: str) -> None:
    try:
        if not context.client.bucket_exists(bucket_name):
            context.client.make_bucket(bucket_name)
            logger.info(f"Bucket '{bucket_name}' created successfully")
        else:
            logger.info(f"Bucket '{bucket_name}' already exists")
    except S3Error as e:
        logger.error(f"Error creating bucket {bucket_name}: {e}")
        raise


def load_data_to_bucket(context: MinioContext, bucket_name: str, object_name: str, data: dict) -> None:
    try:
        json_data = json.dumps(data, indent=2)
        data_stream = io.BytesIO(json_data.encode('utf-8'))
        
        context.client.put_object(
            bucket_name,
            object_name,
            data_stream,
            length=len(json_data.encode('utf-8')),
            content_type='application/json'
        )
        logger.info(f"Data loaded successfully to {bucket_name}/{object_name}")
    except S3Error as e:
        if e.code == "NoSuchBucket":
            logger.warning(f"Bucket {bucket_name} does not exist. Creating bucket...")
            create_bucket(context, bucket_name)
            load_data_to_bucket(context, bucket_name, object_name, data)
        else:
            logger.error(f"Error loading data: {e}")
            raise

def handler(data: dict, bucket_name: str = "spotify-data", object_name: str = "tracks.json"):
    logger.info(f"Starting data load process for bucket: {bucket_name}, object: {object_name}")
    
    ctx = MinioContext(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin"
    )
    
    load_data_to_bucket(ctx, bucket_name, object_name, data)
    logger.info("Data load process completed successfully")