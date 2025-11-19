import typer
import logging
import os
from dotenv import load_dotenv

load_dotenv()

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
    from src.elt.extract import handler as extract_handler
    from src.elt.landing import handler as landing_handler
    from src.elt.load import handler as load_handler

    logger.info("Extracting data from Spotify...")
    spotify_data = extract_handler()

    logger.info("Landing data in MinIO...")
    object_name = landing_handler(spotify_data)

    logger.info("Loading data into a postgres DB")
    load_handler(object_name)

    logger.info("ELT process completed successfully")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Default command that runs the ELT process."""
    if ctx.invoked_subcommand is None:
        run()


if __name__ == "__main__":
    app()
