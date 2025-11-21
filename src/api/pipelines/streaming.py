import asyncio
import logging
from typing import Callable, Awaitable
from src.api.clients.spotify import SpotifyClient
from src.api.clients.kafka import KafkaClient
from src.api.models.tracks import CurrentPlaying
import os

logger = logging.getLogger(__name__)

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")

if KAFKA_TOPIC is None:
    raise ValueError("KAFKA_TOPIC environment variable is not set")


class Streaming:
    def __init__(self, spotify_client: SpotifyClient):
        self.spotify_client = spotify_client
        self.last_track_id = None

    async def run_streaming(
        self,
        kafka_client: KafkaClient,
        fetch_func: Callable[[], Awaitable[dict]],
        process_func: Callable[[dict, KafkaClient, str], Awaitable[None]],
        poll_interval: int,
        stream_name: str,
    ) -> None:
        logger.info(f"Starting streaming loop for {stream_name}")
        while True:
            try:
                data = await fetch_func()
                await process_func(data, kafka_client, stream_name)
            except Exception as e:
                logger.error(f"[{stream_name}] Error in streaming loop: {e}")
            await asyncio.sleep(poll_interval)

    async def run_current_playing(
        self, kafka_client: KafkaClient, poll_interval: int
    ) -> None:
        await self.run_streaming(
            kafka_client=kafka_client,
            fetch_func=self.spotify_client.fetch_current_playing,
            process_func=self._process_current_playing,
            poll_interval=poll_interval,
            stream_name="CurrentPlaying",
        )

    async def _process_current_playing(
        self, track: dict, kafka_client: KafkaClient, stream_name: str
    ) -> None:
        
        logger.info(f"track name: {track}")

        current_playing = CurrentPlaying.model_validate(track)

        if track is None or current_playing.is_playing is False:
            logger.info(f"[{stream_name}] No track playing...")
            return

        track_id = current_playing.item.id
        track_name = current_playing.item.name
        artist_names = ", ".join(artist.name for artist in current_playing.item.artists)

        # Not publish duplicate current playing tracks
        if track_id != self.last_track_id:
            logger.info(f"[{stream_name}] [Published] {track_name} - {artist_names}")
            await kafka_client.send(
                topic=KAFKA_TOPIC, message=current_playing.model_dump()
            )
            self.last_track_id = track_id
        else:
            logger.info(
                f"[{stream_name}] [Not published] {track_name} - {artist_names}"
            )
