"""
MCP server for secure, read-only filesystem access.
"""
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("bruno-filesystem")

def get_allowed_dirs() -> list[Path]:
    dirs_str = os.environ.get("BRUNO_ALLOWED_DIRS", ".")
    return [Path(d).resolve() for d in dirs_str.split(",")]

def is_allowed(path: Path) -> bool:
    try:
        resolved = path.resolve()
        for allowed in get_allowed_dirs():
            if resolved.is_relative_to(allowed):
                return True
        return False
    except Exception:
        return False

@mcp.tool()
def read_file(path: str) -> str:
    """Read the contents of a file."""
    p = Path(path)
    if not is_allowed(p):
        return "Error: Access denied. Path is outside allowed directories."
    if not p.is_file():
        return f"Error: File not found: {path}"

    # 1MB limit
    if p.stat().st_size > 1024 * 1024:
        return "Error: File too large to read (>1MB)."

    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"Error reading file: {e}"

@mcp.tool()
def list_directory(path: str) -> list[str]:
    """List files and subdirectories."""
    p = Path(path)
    if not is_allowed(p):
        return ["Error: Access denied."]
    if not p.is_dir():
        return [f"Error: Directory not found: {path}"]

    try:
        return [str(item.name) for item in p.iterdir()]
    except Exception as e:
        return [f"Error listing directory: {e}"]

@mcp.tool()
def search_files(query: str, directory: str, pattern: str = "*") -> list[str]:
    """Search for files by name pattern within a directory."""
    p = Path(directory)
    if not is_allowed(p):
        return ["Error: Access denied."]

    try:
        results = []
        for file in p.rglob(pattern):
            if query.lower() in file.name.lower():
                results.append(str(file.relative_to(p)))
                if len(results) >= 50:
                    break
        return results
    except Exception as e:
        return [f"Error searching files: {e}"]

if __name__ == "__main__":
    mcp.run(transport="stdio")
