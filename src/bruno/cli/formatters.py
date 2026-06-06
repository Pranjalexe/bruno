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

def display_api_error(e: Exception):
    err_str = str(e).lower()
    
    title = "[bold red]🚨 API Error[/bold red]"
    
    if "per minute" in err_str:
        wait_msg = "⏱️ **Action Required:** You have hit the **Requests Per Minute** limit. Please wait **1 minute** and try again."
        title = "[bold red]🚨 Rate Limit Exceeded[/bold red]"
    elif "per day" in err_str or "daily" in err_str or "quota" in err_str or "429" in err_str:
        wait_msg = "🛑 **Action Required:** You have hit your **Free Tier / Daily Quota**. Please wait until tomorrow (resets midnight PT) or upgrade your API plan."
        title = "[bold red]🚨 Free Tier Exhausted[/bold red]"
    elif "invalid" in err_str or "expired" in err_str or "401" in err_str or "unauthorized" in err_str:
        title = "[bold red]🚨 API Key Error[/bold red]"
        wait_msg = "🔑 **Action Required:** Your API key is invalid or expired. Run `bruno config init` to set a new key."
    elif "connect" in err_str or "network" in err_str or "timeout" in err_str:
        title = "[bold red]🚨 Connection Error[/bold red]"
        wait_msg = "🌐 **Action Required:** Could not connect to the API. Please check your internet connection or VPN."
    else:
        wait_msg = "⚠️ **Action Required:** An unexpected API error occurred."

    raw_error_text = str(e).strip()
    
    markdown_content = f"""
{wait_msg}

---
**Exact Error:**
```text
{raw_error_text}
```
"""
    panel = Panel(Markdown(markdown_content), title=title, border_style="red")
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
