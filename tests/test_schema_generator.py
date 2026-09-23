"""Tests for schema.json and schema.md artifact generation."""
import json
import tempfile
import unittest
from pathlib import Path
from app.schema import (
    extract_schema,
    generate_schema_json,
    generate_schema_markdown,
)


class TestSchemaJsonGeneration(unittest.TestCase):

    def setUp(self):
        self.schema = extract_schema()
        self.tmpdir = Path(tempfile.mkdtemp())
        self.json_path = self.tmpdir / "schema.json"
        generate_schema_json(self.schema, self.json_path)

    def test_json_file_created(self):
        self.assertTrue(self.json_path.exists())

    def test_json_is_valid(self):
        with open(self.json_path, "r") as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)

    def test_json_has_tables_key(self):
        with open(self.json_path, "r") as f:
            data = json.load(f)
        self.assertIn("tables", data)

    def test_json_has_all_11_tables(self):
        with open(self.json_path, "r") as f:
            data = json.load(f)
        table_names = [t["name"] for t in data["tables"]]
        self.assertEqual(len(table_names), 11)
        self.assertIn("Artist", table_names)
        self.assertIn("Album", table_names)
        self.assertIn("Track", table_names)

    def test_json_artist_pk(self):
        with open(self.json_path, "r") as f:
            data = json.load(f)
        artist = next(t for t in data["tables"] if t["name"] == "Artist")
        artist_id_col = next(c for c in artist["columns"] if c["name"] == "ArtistId")
        self.assertTrue(artist_id_col["primary_key"])

    def test_json_album_fk_references_artist(self):
        with open(self.json_path, "r") as f:
            data = json.load(f)
        album = next(t for t in data["tables"] if t["name"] == "Album")
        fks = album["foreign_keys"]
        self.assertTrue(any(
            fk["column"] == "ArtistId"
            and fk["referenced_table"] == "Artist"
            and fk["referenced_column"] == "ArtistId"
            for fk in fks
        ))

    def test_json_track_three_foreign_keys(self):
        with open(self.json_path, "r") as f:
            data = json.load(f)
        track = next(t for t in data["tables"] if t["name"] == "Track")
        self.assertEqual(len(track["foreign_keys"]), 3)

    def test_json_is_deterministic(self):
        path2 = self.tmpdir / "schema2.json"
        generate_schema_json(self.schema, path2)
        with open(self.json_path, "r") as f1, open(path2, "r") as f2:
            self.assertEqual(f1.read(), f2.read())

    def test_json_no_row_data(self):
        """Ensure no actual database row data leaked into schema JSON."""
        with open(self.json_path, "r") as f:
            text = f.read()
        # Should not contain any Chinook artist names
        self.assertNotIn("AC/DC", text)
        self.assertNotIn("Metallica", text)


class TestSchemaMarkdownGeneration(unittest.TestCase):

    def setUp(self):
        self.schema = extract_schema()
        self.tmpdir = Path(tempfile.mkdtemp())
        self.md_path = self.tmpdir / "schema.md"
        generate_schema_markdown(self.schema, self.md_path)
        with open(self.md_path, "r") as f:
            self.content = f.read()

    def test_md_file_created(self):
        self.assertTrue(self.md_path.exists())

    def test_md_contains_artist(self):
        self.assertIn("Artist", self.content)

    def test_md_contains_album(self):
        self.assertIn("Album", self.content)

    def test_md_contains_album_fk_annotation(self):
        self.assertIn("Artist.ArtistId", self.content)

    def test_md_contains_track_relationships(self):
        self.assertIn("Album.AlbumId", self.content)
        self.assertIn("MediaType.MediaTypeId", self.content)
        self.assertIn("Genre.GenreId", self.content)

    def test_md_contains_pk_marker(self):
        self.assertIn("✓", self.content)

    def test_md_contains_fk_arrow(self):
        self.assertIn("→", self.content)

    def test_md_is_deterministic(self):
        path2 = self.tmpdir / "schema2.md"
        generate_schema_markdown(self.schema, path2)
        with open(path2, "r") as f:
            content2 = f.read()
        self.assertEqual(self.content, content2)


if __name__ == "__main__":
    unittest.main()
