import typer
import uvicorn

api_cli = typer.Typer(help="Goats API commands")


@api_cli.command()
def start(host: str = "0.0.0.0", port: int = 8080, reload: bool = False):
    uvicorn.run("src.api.app:app", host=host, port=port, reload=reload)
