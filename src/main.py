import typer
import logging
from src.api.cli import api_cli


__version__ = "0.1.0"

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=getattr(logging, "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

main_cli = typer.Typer()


@main_cli.command()
def version():
    logger.info(__version__)


# API CLI commands
main_cli.add_typer(api_cli, name="api")


def app():
    main_cli()


if __name__ == "__main__":
    app()
