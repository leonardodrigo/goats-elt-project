import typer
import uvicorn
from src.api.app import app

api_cli = typer.Typer(help="Goats API commands")


@api_cli.command()
def start(host: str = "0.0.0.0", port: int = 8080):
    uvicorn.run(app, host=host, port=port)
