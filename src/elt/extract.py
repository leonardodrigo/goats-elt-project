import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os


CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SCOPE = "user-read-recently-played"


class SpotifyContext:
    def __init__(
        self, client_id: str, client_secret: str, redirect_uri: str, scope: str
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=scope,
            )
        )


def get_recently_played_tracks(context: SpotifyContext, limit: int = 50) -> dict:
    result = context.sp.current_user_recently_played(limit=limit)
    return result


def handler() -> dict:
    ctx = SpotifyContext(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
    )

    return get_recently_played_tracks(ctx)
