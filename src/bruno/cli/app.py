"""
Main entry point for Bruno CLI.
"""
import typer
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

from bruno import __version__
from bruno.cli.commands.config import app as config_app
from bruno.cli.commands.debug import debug_cmd
from bruno.cli.commands.index import app as index_app
from bruno.cli.commands.research import research_cmd
from bruno.cli.commands.clean import clean_cmd

app = typer.Typer(
    help="Bruno — The Terminal Research Agent",
    no_args_is_help=True,
    add_completion=False,
)

def version_callback(value: bool):
    if value:
        typer.echo(f"Bruno version: {__version__}")
        raise typer.Exit()

@app.callback()
def main_callback(
    version: bool = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="Show version."
    ),
):
    pass

# Add subcommands
app.command("debug")(debug_cmd)
app.command("research")(research_cmd)
app.command("clean")(clean_cmd)
app.add_typer(index_app, name="index")
app.add_typer(config_app, name="config")

if __name__ == "__main__":
    app()
