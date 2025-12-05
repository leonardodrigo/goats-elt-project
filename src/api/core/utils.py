from functools import lru_cache
from src.api.clients.spotify import SpotifyClient
from src.api.clients.storage import CloudStorageClient
from src.api.core.config import (
    KAFKA_BOOTSTRAP_SERVERS,
)
from src.api.clients.kafka import KafkaClient


@lru_cache(maxsize=1)
def get_cached_spotify_client() -> SpotifyClient:
    return SpotifyClient()


@lru_cache(maxsize=1)
def get_cached_storage_client() -> CloudStorageClient:
    return CloudStorageClient()


@lru_cache(maxsize=1)
def get_cached_kafka_client() -> KafkaClient:
    return KafkaClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
