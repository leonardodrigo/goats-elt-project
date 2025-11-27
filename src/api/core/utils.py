from functools import lru_cache
from src.api.clients.spotify import SpotifyClient
from src.api.clients.minio import MinIOClient
from src.api.core.config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
    KAFKA_BOOTSTRAP_SERVERS,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
)
from src.api.clients.kafka import KafkaClient
from src.api.clients.postgres import PostgresClient


@lru_cache(maxsize=1)
def get_cached_spotify_client() -> SpotifyClient:
    return SpotifyClient()


@lru_cache(maxsize=1)
def get_cached_minio_client(bucket_name: str = MINIO_BUCKET) -> MinIOClient:
    return MinIOClient(
        endpoint=MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        bucket_name=bucket_name,
    )


@lru_cache(maxsize=1)
def get_cached_kafka_client() -> KafkaClient:
    return KafkaClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)


@lru_cache(maxsize=1)
def get_cached_postgres_client() -> PostgresClient:
    return PostgresClient(
        host=POSTGRES_HOST,
        port=int(POSTGRES_PORT),
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )
