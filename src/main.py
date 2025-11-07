import typer
import logging
import os
from dotenv import load_dotenv

load_dotenv("infra/.env")

logger = logging.getLogger(__name__)

app = typer.Typer()
app.__version__ = "0.1.0"

DATABASE_CONNECTION = os.getenv("DATABASE_URL", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@app.command()
def run():
    logger.info("Starting ELT process...")
    from elt.extract import handler as extract_handler
    from elt.load import handler as load_handler

    logger.info("Extracting data from Spotify...")
    spotify_data = extract_handler()

    logger.info("Loading data to MinIO...")
    load_handler(spotify_data)

    logger.info("ELT process completed successfully")


@app.command()
def main():
    app()


if __name__ == "__main__":
    main()
