import typer
import logging

logger = logging.getLogger(__name__)

app = typer.Typer()

DATABASE_CONNECTION = ""

@app.command()
def run_extraction():
    logger.info("Starting the extraction process...")
    from elt.extract import handler
    handler()

@app.command()
def run_load():
    logger.info("Starting the load process...")
    from elt.load import handler
    handler()


def main():
    print("Hello from goats-elt-project!")


if __name__ == "__main__":
    main()
