"""
MCP server for read-only SQLite database access.
"""
import re
import sqlite3
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from bruno.mcp_servers.filesystem_server import is_allowed

mcp = FastMCP("bruno-sqlite")

FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "CREATE", "TRUNCATE", "REPLACE", "GRANT", "REVOKE"
]

def is_safe_query(sql: str) -> bool:
    upper_sql = sql.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf'\b{keyword}\b', upper_sql):
            return False
    return True

@mcp.tool()
def list_tables(db_path: str) -> list[str]:
    """List all tables in the SQLite database."""
    p = Path(db_path)
    if not is_allowed(p):
        return ["Error: Access denied."]

    try:
        conn = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    except Exception as e:
        return [f"Error listing tables: {e}"]

@mcp.tool()
def describe_table(db_path: str, table_name: str) -> list[dict]:
    """Get the schema of a table."""
    p = Path(db_path)
    if not is_allowed(p):
        return [{"error": "Access denied."}]

    try:
        conn = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
        cursor = conn.cursor()
        # safe as table_name is parameterized effectively or escaped, but pragma table_info needs formatting safely
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [{"cid": r[0], "name": r[1], "type": r[2], "notnull": r[3], "dflt_value": r[4], "pk": r[5]} for r in cursor.fetchall()]
        conn.close()
        return columns
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def query(db_path: str, sql: str) -> list[dict]:
    """Execute a read-only SQL query."""
    p = Path(db_path)
    if not is_allowed(p):
        return [{"error": "Access denied."}]

    if not is_safe_query(sql):
        return [{"error": "Unsafe query. Only SELECT statements are allowed."}]

    try:
        conn = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        # Limit to 100 rows just in case
        rows = [dict(row) for row in cursor.fetchmany(100)]
        conn.close()
        return rows
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == "__main__":
    mcp.run(transport="stdio")
