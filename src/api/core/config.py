import os
from dotenv import load_dotenv

dotenv_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "infra", ".env"
)
load_dotenv(dotenv_path=dotenv_path)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")
POLL_INTERVAL = os.getenv("POLL_INTERVAL")

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REFRESH_TOKEN = os.getenv("SPOTIPY_REFRESH_TOKEN")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SPOTIPY_SCOPES = os.getenv("SPOTIPY_SCOPES")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")
