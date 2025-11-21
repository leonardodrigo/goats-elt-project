from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "infra", ".env")
load_dotenv(dotenv_path=dotenv_path)


def get_refresh_token():
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=os.getenv("SPOTIPY_SCOPES"),
    )

    token_info = sp_oauth.get_access_token(as_dict=True)
    return token_info["refresh_token"]


def main():
    token = get_refresh_token()
    print(token)


if __name__ == "__main__":
    main()
