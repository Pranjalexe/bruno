"""
Rich formatting helpers for Bruno CLI output.
"""
from contextlib import contextmanager

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

console = Console()

def display_response(response: str, title: str = "Bruno Response"):
    md = Markdown(response)
    panel = Panel(md, title=f"[bold bright_cyan]{title}[/bold bright_cyan]", border_style="bright_cyan")
    console.print(panel)

def display_error(error: str):
    panel = Panel(f"[red]{error}[/red]", title="[bold red]Error[/bold red]", border_style="red")
    console.print(panel)

@contextmanager
def display_spinner(message: str):
    with console.status(f"[bold green]{message}[/bold green]", spinner="dots") as status:
        yield status

def display_table(title: str, columns: list[str], rows: list[list[str]]):
    table = Table(title=f"[bold]{title}[/bold]")
    for col in columns:
        table.add_column(col, style="cyan")
    for row in rows:
        table.add_row(*[str(item) for item in row])
    console.print(table)
