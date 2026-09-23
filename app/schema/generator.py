import json
from pathlib import Path
from .models import DatabaseSchema


def generate_schema_json(schema: DatabaseSchema, output_path: Path) -> None:
    """Serialize DatabaseSchema to a stable, indented JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = schema.model_dump()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=False, ensure_ascii=False)
        f.write("\n")


def generate_schema_markdown(schema: DatabaseSchema, output_path: Path) -> None:
    """Render DatabaseSchema to a compact Markdown file with PK/FK annotations."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build FK lookup: table.column -> "referenced_table.referenced_column"
    lines: list[str] = ["# Database Schema\n"]

    for table in schema.tables:
        fk_map: dict[str, str] = {}
        for fk in table.foreign_keys:
            fk_map[fk.column] = f"{fk.referenced_table}.{fk.referenced_column}"

        lines.append(f"## Table: {table.name}\n")
        lines.append("| Column | Type | PK | FK |")
        lines.append("|--------|------|----|----|")

        for col in table.columns:
            pk = "✓" if col.primary_key else ""
            fk = f"→ {fk_map[col.name]}" if col.name in fk_map else ""
            lines.append(f"| {col.name} | {col.data_type} | {pk} | {fk} |")

        lines.append("")  # blank line between tables

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
