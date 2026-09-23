from typing import Any, Optional
from app.database import get_connection
from .models import ColumnSchema, ForeignKeySchema, TableSchema, DatabaseSchema


def get_tables() -> list[str]:
    """Retrieve all non-system table names from the database."""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
        """)
        return [row["name"] for row in cursor.fetchall()]
    finally:
        conn.close()


def table_exists(table_name: str) -> bool:
    """Check whether a table exists in the database."""
    conn = get_connection()
    try:
        cursor = conn.execute("""
            SELECT 1
            FROM sqlite_master
            WHERE type = 'table'
            AND name = ?
            LIMIT 1;
        """, (table_name,))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def get_table_schema(table_name: str) -> Optional[list[dict[str, Any]]]:
    """Retrieve column definitions for a given table."""
    if not table_exists(table_name):
        return None

    conn = get_connection()
    try:
        cursor = conn.execute(f'PRAGMA table_info("{table_name}")')
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "name": row["name"],
                "type": row["type"],
                "not_null": bool(row["notnull"]),
                "default": row["dflt_value"],
                "primary_key": bool(row["pk"])
            })
        return columns
    finally:
        conn.close()


def get_foreign_keys(table_name: str) -> Optional[list[dict[str, str]]]:
    """Retrieve foreign key relationships for a given table."""
    if not table_exists(table_name):
        return None

    conn = get_connection()
    try:
        cursor = conn.execute(f'PRAGMA foreign_key_list("{table_name}")')
        foreign_keys = []
        for row in cursor.fetchall():
            foreign_keys.append({
                "table": row["table"],
                "column": row["from"],
                "references_column": row["to"]
            })
        return foreign_keys
    finally:
        conn.close()


def extract_schema() -> DatabaseSchema:
    """Extract complete database schema including all tables, columns, and foreign keys."""
    table_names = get_tables()
    tables: list[TableSchema] = []

    for table_name in table_names:
        raw_cols = get_table_schema(table_name) or []
        columns = [
            ColumnSchema(
                name=c["name"],
                data_type=c["type"],
                nullable=not c["not_null"],
                primary_key=c["primary_key"],
                default_value=c["default"]
            )
            for c in raw_cols
        ]

        raw_fks = get_foreign_keys(table_name) or []
        foreign_keys = [
            ForeignKeySchema(
                column=fk["column"],
                referenced_table=fk["table"],
                referenced_column=fk["references_column"]
            )
            for fk in raw_fks
        ]

        tables.append(TableSchema(
            name=table_name,
            columns=columns,
            foreign_keys=foreign_keys
        ))

    return DatabaseSchema(tables=tables)
