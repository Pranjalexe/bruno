"""
MCP tool loader — connects to MCP servers and converts their tools to LangChain tools.
"""
import sys
from pathlib import Path

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from bruno.config import BrunoSettings


async def load_mcp_tools(settings: BrunoSettings) -> tuple[MultiServerMCPClient, list[BaseTool]]:
    """Connects to configured MCP servers and returns their tools as LangChain tools.
    
    Returns a tuple of (MCP client context manager, list of tools).
    The caller is responsible for entering and exiting the client context.
    """
    server_dir = Path(__file__).parent.parent.parent / "mcp_servers"

    configs = {
        "filesystem": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [str(server_dir / "filesystem_server.py")],
            "env": {"BRUNO_ALLOWED_DIRS": str(settings.data_dir)},
        },
        "env": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [str(server_dir / "env_server.py")],
        },
        "sqlite": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [str(server_dir / "sqlite_server.py")],
        },
    }

    # Merge with custom servers from config
    configs.update(settings.mcp_servers)

    client = MultiServerMCPClient(configs)

    # We can't automatically get_tools() without entering the context
    # We'll return the client so the caller can enter it and then call client.get_tools()

    return client
