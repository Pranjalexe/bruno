import os

import typer

from bruno.cli.formatters import display_table
from bruno.config import get_settings

app = typer.Typer(help="Manage configuration.")

@app.command("show")
def show_cmd():
    """Show current configuration."""
    settings = get_settings()

    rows = []
    for k, v in settings.model_dump().items():
        if "key" in k.lower() and v:
            v = "***REDACTED***"
        rows.append([k, str(v)])

    display_table("Bruno Configuration", ["Key", "Value"], rows)

@app.command("init")
def init_cmd():
    """Interactive setup wizard."""
    typer.echo("Bruno Setup Wizard")
    typer.echo("------------------")

    api_key = typer.prompt("Google Gemini API Key (or press Enter to skip)", default="", show_default=False)

    if api_key:
        settings = get_settings()
        env_path = settings.data_dir / ".env"
        mode = "a" if env_path.exists() else "w"
        with open(env_path, mode) as f:
            if mode == "a":
                f.write("\n")
            f.write(f"BRUNO_GEMINI_API_KEY={api_key}\n")
        typer.echo(f"Saved BRUNO_GEMINI_API_KEY to {env_path}")

    typer.echo("Setup complete!")
