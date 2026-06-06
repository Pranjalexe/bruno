from typing import Annotated

import typer

from bruno.cli.formatters import display_spinner, display_table
from bruno.config import get_settings
from bruno.rag.ingestion import ingest_path
from bruno.rag.store import BrunoVectorStore

app = typer.Typer(help="Manage the local knowledge base index.")

@app.command("add")
def add_cmd(
    path: str = typer.Argument(..., help="Path to file or directory"),
    recursive: Annotated[bool, typer.Option("--recursive", "-r", help="Index directories recursively")] = False,
    collection: Annotated[str, typer.Option("--collection", "-c", help="Collection name")] = "knowledge_base",
):
    """Index a file or directory into the knowledge base."""
    settings = get_settings()
    store = BrunoVectorStore(settings.data_dir)

    with display_spinner(f"Indexing {path}...") as status:
        result = ingest_path(path, store, recursive=recursive, collection=collection)
        status.stop()

    typer.echo(f"Files processed: {result.files_processed}")
    typer.echo(f"Chunks created: {result.chunks_created}")
    typer.echo(f"Files skipped: {result.files_skipped}")
    if result.errors:
        typer.echo(f"Errors: {len(result.errors)}")
        for e in result.errors[:5]:
            typer.echo(f"  - {e}")
        if len(result.errors) > 5:
            typer.echo("  ... and more")

@app.command("list")
def list_cmd():
    """Show collections and document counts."""
    settings = get_settings()
    store = BrunoVectorStore(settings.data_dir)
    stats = store.get_stats()

    if not stats:
        typer.echo("No collections found.")
        return

    rows = [[name, str(count)] for name, count in stats.items()]
    display_table("Collections", ["Name", "Document Count"], rows)

@app.command("clear")
def clear_cmd(
    collection: Annotated[str | None, typer.Option("--collection", "-c", help="Specific collection to ingest into (defaults to 'knowledge_base')")] = None,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation")] = False,
):
    """Clear a collection or all collections."""
    settings = get_settings()
    store = BrunoVectorStore(settings.data_dir)

    if not yes:
        confirm = typer.confirm("Are you sure you want to delete this data?")
        if not confirm:
            typer.echo("Aborted.")
            return

    if collection:
        store.delete_collection(collection)
        typer.echo(f"Collection '{collection}' deleted.")
    else:
        for c in store.list_collections():
            store.delete_collection(c)
        typer.echo("All collections deleted.")
