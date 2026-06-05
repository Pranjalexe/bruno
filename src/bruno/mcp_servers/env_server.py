"""
MCP server for reading environment variables (filtered).
"""
import os
import sys

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("bruno-env")

SENSITIVE_PATTERNS = ["KEY", "SECRET", "TOKEN", "PASSWORD", "CREDENTIAL", "AUTH"]

@mcp.tool()
def get_env(name: str) -> str | None:
    """Get the value of a specific environment variable."""
    value = os.environ.get(name)
    if value and any(p in name.upper() for p in SENSITIVE_PATTERNS):
        return "***REDACTED***"
    return value

@mcp.tool()
def list_env(prefix: str = "") -> dict[str, str]:
    """List environment variables, optionally filtered by prefix."""
    result = {}
    for k, v in os.environ.items():
        if k.startswith(prefix):
            if any(p in k.upper() for p in SENSITIVE_PATTERNS):
                result[k] = "***REDACTED***"
            else:
                result[k] = v
    return result

@mcp.tool()
def get_python_info() -> dict:
    """Returns Python version, sys.path, virtualenv status."""
    return {
        "version": sys.version,
        "executable": sys.executable,
        "path": sys.path,
        "in_virtualenv": hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
