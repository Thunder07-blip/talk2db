"""CLI script to generate schema artifacts (schema.json and schema.md).

Usage: python -m app.schema.generate_artifacts
"""
from pathlib import Path
from app.schema.extractor import extract_schema
from app.schema.generator import generate_schema_json, generate_schema_markdown


def main() -> None:
    schema = extract_schema()

    output_dir = Path(__file__).resolve().parent.parent.parent / "generated"

    json_path = output_dir / "schema.json"
    md_path = output_dir / "schema.md"

    generate_schema_json(schema, json_path)
    print(f"Generated {json_path}")

    generate_schema_markdown(schema, md_path)
    print(f"Generated {md_path}")

    print(f"\nSchema: {len(schema.tables)} tables extracted.")


if __name__ == "__main__":
    main()
