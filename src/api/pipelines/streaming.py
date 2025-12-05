import asyncio
import logging
from typing import Callable, Awaitable
from src.api.clients.spotify import SpotifyClient
from src.api.clients.kafka import KafkaClient
from src.api.models.tracks import CurrentPlaying
import os

from opentelemetry import metrics, trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")

if KAFKA_TOPIC is None:
    raise ValueError("KAFKA_TOPIC environment variable is not set")

# Metrics
meter = metrics.get_meter(__name__)
tracks_counter = meter.create_counter(
    "tracks_processed_total",
    description="Total tracks processed",
)


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
            with tracer.start_as_current_span(f"streaming.{stream_name.lower()}_poll") as span:
                span.set_attribute("stream.name", stream_name)
                span.set_attribute("stream.poll_interval", poll_interval)
                try:
                    data = await fetch_func()
                    await process_func(data, kafka_client, stream_name)
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
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
        with tracer.start_as_current_span("streaming.process_track") as span:
            if track is None:
                span.set_attribute("track.status", "no_track")
                logger.info(f"[{stream_name}] No track playing...")
                return

            current_playing = CurrentPlaying.model_validate(track)

            if current_playing.is_playing is False:
                span.set_attribute("track.status", "paused")
                logger.info(f"[{stream_name}] No track playing...")
                return

            track_id = current_playing.item.id
            track_name = current_playing.item.name
            artist_names = ", ".join(artist.name for artist in current_playing.item.artists)
            
            span.set_attribute("track.id", track_id)
            span.set_attribute("track.name", track_name)
            span.set_attribute("track.artists", artist_names)

            if track_id != self.last_track_id:
                span.set_attribute("track.status", "published")
                logger.info(f"[{stream_name}] [Published] {track_name} - {artist_names}")
                
                with tracer.start_as_current_span("kafka.send"):
                    await kafka_client.send(
                        topic=KAFKA_TOPIC, message=current_playing.model_dump()
                    )
                
                self.last_track_id = track_id
                tracks_counter.add(1, {"status": "published"})
            else:
                span.set_attribute("track.status", "skipped")
                logger.info(
                    f"[{stream_name}] [Not published] {track_name} - {artist_names}"
                )
                tracks_counter.add(1, {"status": "skipped"})
