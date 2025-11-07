import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json


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


def get_recently_played_tracks(context: SpotifyContext, limit: int = 50) -> str:
    result = context.sp.current_user_recently_played(limit=limit)
    tracks = json.dumps(result, indent=4)
    return tracks


def handler():
    pass
