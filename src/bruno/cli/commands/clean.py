import shutil
from pathlib import Path

import typer
from rich.console import Console

from bruno.config import get_settings

def clean_cmd(
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt")
):
    """Clear all memory, cache, and indices used by Bruno (preserves API keys)."""
    console = Console()
    settings = get_settings()
    data_dir = settings.data_dir
    
    if not data_dir.exists():
        console.print("[yellow]Bruno data directory does not exist. Nothing to clean.[/yellow]")
        return
        
    if not yes:
        confirm = typer.confirm(f"Are you sure you want to delete all cached data and indices in {data_dir}? (Your .env API keys will be saved)")
        if not confirm:
            raise typer.Abort()
            
    try:
        deleted_count = 0
        for item in data_dir.iterdir():
            if item.name == ".env":
                continue  # Skip the environment variables file!
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
            deleted_count += 1
            
        console.print(f"[green]Successfully cleaned {deleted_count} items from {data_dir}.[/green]")
    except Exception as e:
        console.print(f"[red]Error cleaning data directory: {e}[/red]")
        raise typer.Exit(code=1)
