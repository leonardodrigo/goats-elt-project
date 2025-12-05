import spotipy
from spotipy.oauth2 import SpotifyOAuth
import asyncio
import os
import time
import logging

import logging
from src.monitoring.otel_setup import setup_otel_logging

setup_otel_logging()

logger = logging.getLogger("goats-elt")
logger.setLevel(logging.DEBUG)


def ensure_token(func):
    def wrapper(self, *args, **kwargs):
        if time.time() >= self.expires_at - 10:
            token_info = self.sp_oauth.refresh_access_token(self.refresh_token)
            self.sp = spotipy.Spotify(auth=token_info["access_token"])
            self.expires_at = token_info["expires_at"]
        return func(self, *args, **kwargs)

    return wrapper


def ensure_token_async(func):
    async def wrapper(self, *args, **kwargs):
        if time.time() >= self.expires_at - 10:
            token_info = await asyncio.to_thread(
                self.sp_oauth.refresh_access_token, self.refresh_token
            )
            self.sp = spotipy.Spotify(auth=token_info["access_token"])
            self.expires_at = token_info["expires_at"]
        return await func(self, *args, **kwargs)

    return wrapper


class SpotifyClient:
    def __init__(self) -> None:
        self.client_id = os.getenv("SPOTIPY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")
        self.refresh_token = os.getenv("SPOTIPY_REFRESH_TOKEN")
        self.scopes = os.getenv("SPOTIPY_SCOPES")

        self.sp_oauth = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scopes,
        )

        token_info = self.sp_oauth.refresh_access_token(self.refresh_token)
        self.sp = spotipy.Spotify(auth=token_info["access_token"])
        self.expires_at = token_info["expires_at"]

    @ensure_token
    def fetch_recently_played_tracks(self, limit: int = 50) -> dict:
        return self.sp.current_user_recently_played(limit=limit)

    @ensure_token_async
    async def fetch_current_playing(self) -> dict:
        current_playing = await asyncio.to_thread(self.sp.currently_playing)
        return current_playing
