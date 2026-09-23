import sqlite3
from app.config import SQLITE_RO_URI


def get_connection() -> sqlite3.Connection:
    """Create and return a read-only SQLite database connection."""
    conn = sqlite3.connect(
        SQLITE_RO_URI,
        uri=True
    )
    conn.row_factory = sqlite3.Row
    return conn
