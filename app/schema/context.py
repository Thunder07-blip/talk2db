from typing import Any, Optional
from app.database import get_connection
from .models import DatabaseSchema, TableSchema, ColumnSchema, ForeignKeySchema
from .extractor import table_exists


def build_schema_context(schema: DatabaseSchema) -> str:
    """Build a compact text representation of the full database schema for LLM prompts.

    Args:
        schema: The complete DatabaseSchema to represent.

    Returns:
        A deterministic, human-readable string describing the entire schema.
    """
    lines: list[str] = ["DATABASE SCHEMA", ""]

    for table in schema.tables:
        fk_map: dict[str, str] = {}
        for fk in table.foreign_keys:
            fk_map[fk.column] = f"{fk.referenced_table}.{fk.referenced_column}"

        lines.append(f"TABLE {table.name}")
        for col in table.columns:
            parts = [f"  {col.name} {col.data_type}"]
            if col.primary_key:
                parts.append("[PK]")
            if col.name in fk_map:
                parts.append(f"[FK → {fk_map[col.name]}]")
            lines.append(" ".join(parts))
        lines.append("")  # blank line between tables

    return "\n".join(lines).rstrip() + "\n"


def filter_schema(
    schema: DatabaseSchema,
    tables: list[str],
) -> DatabaseSchema:
    """Filter a DatabaseSchema to include only the specified tables.

    Foreign key references are preserved only when the target table is also
    in the selection. Unknown table names raise ValueError.

    Args:
        schema: The full DatabaseSchema.
        tables: List of table names to include.

    Returns:
        A new DatabaseSchema containing only the requested tables.

    Raises:
        ValueError: If any requested table name is not found in the schema.
    """
    available = {t.name for t in schema.tables}
    requested = set(tables)

    unknown = requested - available
    if unknown:
        raise ValueError(f"Unknown table(s): {', '.join(sorted(unknown))}")

    filtered_tables: list[TableSchema] = []
    for table in schema.tables:
        if table.name not in requested:
            continue

        # Keep only FKs whose target table is also in the selection
        filtered_fks = [
            fk for fk in table.foreign_keys
            if fk.referenced_table in requested
        ]

        filtered_tables.append(TableSchema(
            name=table.name,
            columns=list(table.columns),  # shallow copy
            foreign_keys=filtered_fks,
        ))

    return DatabaseSchema(tables=filtered_tables)


def get_distinct_values(
    table_name: str,
    column_name: str,
    limit: int = 20,
) -> list[Any]:
    """Retrieve a limited sample of distinct values from a specific column.

    Args:
        table_name: Name of the table.
        column_name: Name of the column.
        limit: Maximum number of distinct values to return.

    Returns:
        A list of distinct values.

    Raises:
        ValueError: If the table or column does not exist.
    """
    if not table_exists(table_name):
        raise ValueError(f"Table '{table_name}' does not exist")

    # Validate column exists
    conn = get_connection()
    try:
        cursor = conn.execute(f'PRAGMA table_info("{table_name}")')
        col_names = [row["name"] for row in cursor.fetchall()]
        if column_name not in col_names:
            raise ValueError(
                f"Column '{column_name}' does not exist in table '{table_name}'"
            )

        cursor = conn.execute(
            f'SELECT DISTINCT "{column_name}" FROM "{table_name}" '
            f'ORDER BY "{column_name}" LIMIT ?',
            (limit,),
        )
        return [row[column_name] for row in cursor.fetchall()]
    finally:
        conn.close()


def build_context(
    schema: DatabaseSchema,
    selected_tables: Optional[list[str]] = None,
    value_candidates: Optional[dict[str, list[str]]] = None,
) -> str:
    """Build the final schema context for LLM consumption.

    Combines schema text representation with optional value candidates.

    Args:
        schema: The full DatabaseSchema.
        selected_tables: If provided, filter schema to these tables only.
        value_candidates: Optional dict mapping "Table.Column" to a list of
            sample values to include in the context.

    Returns:
        A deterministic context string suitable for LLM prompts.
    """
    if selected_tables is not None:
        working_schema = filter_schema(schema, selected_tables)
    else:
        working_schema = schema

    context = build_schema_context(working_schema)

    if value_candidates:
        lines = ["\nSAMPLE VALUES"]
        for key in sorted(value_candidates.keys()):
            values = value_candidates[key]
            formatted = ", ".join(str(v) for v in values)
            lines.append(f"  {key}: {formatted}")
        context = context.rstrip() + "\n" + "\n".join(lines) + "\n"

    return context
