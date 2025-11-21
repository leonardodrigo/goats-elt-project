from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import logging
from src.api.core.config import POLL_INTERVAL
from src.api.clients.kafka import KafkaClient
from src.api.clients.spotify import SpotifyClient
from src.api.pipelines.streaming import Streaming
from src.api.core.utils import get_cached_kafka_client, get_cached_spotify_client


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    kafka_client: KafkaClient = get_cached_kafka_client()
    spotify_client: SpotifyClient = get_cached_spotify_client()

    streaming_pipeline = Streaming(spotify_client)

    await kafka_client.start()

    stream_task = asyncio.create_task(
        streaming_pipeline.run_current_playing(kafka_client, int(POLL_INTERVAL))
    )

    logger.info("Streaming task created and started")
    app.state.stream_task = stream_task

    try:
        yield
    finally:
        stream_task.cancel()
        await asyncio.gather(stream_task, return_exceptions=True)
        await kafka_client.stop()
