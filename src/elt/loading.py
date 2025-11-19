import boto3
import json
from datetime import datetime
from db_helper import get_db_connection
import os

# ==== MinIO / S3 settings ====
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT","http://localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY","myuser")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY","mypassword")
MINIO_BUCKET = os.getenv("MINIO_BUCKET","test")

s3 = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY 
)

def read_file(key: str):
    """Read file contents from S3/MinIO"""
    response = s3.get_object(Bucket=MINIO_BUCKET, Key=key)
    return response["Body"].read().decode("utf-8")


def init_bronze_table():
    """Create schema and bronze table if they don't exist"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create bronze table met alleen top-level velden als kolommen
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public.bronze_recently_played (
                id SERIAL PRIMARY KEY,
                source_file TEXT NOT NULL,
                loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                
                -- Top-level velden uit 'items'
                track JSONB,
                played_at TIMESTAMPTZ,
                context JSONB
            );
        """)

def insert_bronze_data(file_key: str, items: list):
    """Insert each item from the API response into bronze layer"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        for item in items:
            cursor.execute(
                """
                INSERT INTO public.bronze_recently_played (
                    source_file,
                    track,
                    played_at,
                    context
                    ) VALUES (%s, %s, %s, %s)
                """,
                (
                    file_key,
                    json.dumps(item.get('track')),
                    item.get('played_at'),
                    json.dumps(item.get('context'))                
                    )
            )

def mark_as_loaded(object_name: str):
    """Update status to 'loaded'"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE public.log_landing_loading
            SET status = 'loaded',
                loaded_at = %s
            WHERE object_name = %s
        """, (datetime.now(), object_name))

def handler(object_name):

    init_bronze_table()
    
    file_contents = read_file(object_name)
    
    data = json.loads(file_contents)
    
    # Extract items array for actual data
    items = data.get('items', [])
    
    insert_bronze_data(object_name, items)

    mark_as_loaded(object_name)

handler("test.json")
