"""Tests for LLM-ready schema context system."""
import unittest
from app.schema import extract_schema, DatabaseSchema
from app.schema.context import (
    build_schema_context,
    filter_schema,
    get_distinct_values,
    build_context,
)


class TestBuildSchemaContext(unittest.TestCase):

    def setUp(self):
        self.schema = extract_schema()

    def test_output_is_string(self):
        ctx = build_schema_context(self.schema)
        self.assertIsInstance(ctx, str)

    def test_starts_with_header(self):
        ctx = build_schema_context(self.schema)
        self.assertTrue(ctx.startswith("DATABASE SCHEMA"))

    def test_contains_artist(self):
        ctx = build_schema_context(self.schema)
        self.assertIn("TABLE Artist", ctx)

    def test_contains_album(self):
        ctx = build_schema_context(self.schema)
        self.assertIn("TABLE Album", ctx)

    def test_pk_annotation(self):
        ctx = build_schema_context(self.schema)
        self.assertIn("[PK]", ctx)

    def test_fk_annotation_album_artist(self):
        ctx = build_schema_context(self.schema)
        self.assertIn("[FK → Artist.ArtistId]", ctx)

    def test_track_fk_annotations(self):
        ctx = build_schema_context(self.schema)
        self.assertIn("[FK → Album.AlbumId]", ctx)
        self.assertIn("[FK → MediaType.MediaTypeId]", ctx)
        self.assertIn("[FK → Genre.GenreId]", ctx)

    def test_all_11_tables_present(self):
        ctx = build_schema_context(self.schema)
        expected = [
            "Album", "Artist", "Customer", "Employee", "Genre",
            "Invoice", "InvoiceLine", "MediaType", "Playlist",
            "PlaylistTrack", "Track",
        ]
        for t in expected:
            self.assertIn(f"TABLE {t}", ctx)

    def test_deterministic_output(self):
        ctx1 = build_schema_context(self.schema)
        ctx2 = build_schema_context(self.schema)
        self.assertEqual(ctx1, ctx2)


class TestFilterSchema(unittest.TestCase):

    def setUp(self):
        self.schema = extract_schema()

    def test_filter_returns_only_requested(self):
        filtered = filter_schema(self.schema, ["Artist", "Album"])
        names = [t.name for t in filtered.tables]
        self.assertEqual(sorted(names), ["Album", "Artist"])

    def test_filter_preserves_columns(self):
        filtered = filter_schema(self.schema, ["Artist"])
        artist = filtered.tables[0]
        col_names = [c.name for c in artist.columns]
        self.assertIn("ArtistId", col_names)
        self.assertIn("Name", col_names)

    def test_filter_preserves_included_fk_targets(self):
        """Album.ArtistId FK should be kept when Artist is also selected."""
        filtered = filter_schema(self.schema, ["Artist", "Album"])
        album = next(t for t in filtered.tables if t.name == "Album")
        fk_targets = [fk.referenced_table for fk in album.foreign_keys]
        self.assertIn("Artist", fk_targets)

    def test_filter_drops_excluded_fk_targets(self):
        """Album.ArtistId FK should be dropped when Artist is NOT selected."""
        filtered = filter_schema(self.schema, ["Album"])
        album = filtered.tables[0]
        self.assertEqual(len(album.foreign_keys), 0)

    def test_filter_does_not_mutate_original(self):
        original_table_count = len(self.schema.tables)
        filter_schema(self.schema, ["Artist"])
        self.assertEqual(len(self.schema.tables), original_table_count)

    def test_filter_rejects_unknown_table(self):
        with self.assertRaises(ValueError) as ctx:
            filter_schema(self.schema, ["Artist", "FakeTable"])
        self.assertIn("FakeTable", str(ctx.exception))

    def test_filter_returns_database_schema(self):
        filtered = filter_schema(self.schema, ["Genre"])
        self.assertIsInstance(filtered, DatabaseSchema)

    def test_filter_single_table(self):
        filtered = filter_schema(self.schema, ["Genre"])
        self.assertEqual(len(filtered.tables), 1)
        self.assertEqual(filtered.tables[0].name, "Genre")

    def test_filter_preserves_order(self):
        """Tables should maintain original schema ordering."""
        filtered = filter_schema(self.schema, ["Track", "Album", "Artist"])
        names = [t.name for t in filtered.tables]
        # Original order is Album, Artist, Track (alphabetical from extractor)
        self.assertEqual(names, ["Album", "Artist", "Track"])


class TestGetDistinctValues(unittest.TestCase):

    def test_returns_values_for_valid_column(self):
        values = get_distinct_values("Customer", "Country", limit=5)
        self.assertIsInstance(values, list)
        self.assertGreater(len(values), 0)
        self.assertLessEqual(len(values), 5)

    def test_respects_limit(self):
        values_3 = get_distinct_values("Customer", "Country", limit=3)
        values_10 = get_distinct_values("Customer", "Country", limit=10)
        self.assertLessEqual(len(values_3), 3)
        self.assertLessEqual(len(values_10), 10)

    def test_values_are_sorted(self):
        values = get_distinct_values("Customer", "Country", limit=20)
        self.assertEqual(values, sorted(values))

    def test_rejects_nonexistent_table(self):
        with self.assertRaises(ValueError) as ctx:
            get_distinct_values("FakeTable", "Name")
        self.assertIn("FakeTable", str(ctx.exception))

    def test_rejects_nonexistent_column(self):
        with self.assertRaises(ValueError) as ctx:
            get_distinct_values("Artist", "FakeColumn")
        self.assertIn("FakeColumn", str(ctx.exception))

    def test_numeric_column(self):
        values = get_distinct_values("Track", "Milliseconds", limit=5)
        self.assertIsInstance(values, list)
        self.assertGreater(len(values), 0)


class TestBuildContext(unittest.TestCase):

    def setUp(self):
        self.schema = extract_schema()

    def test_full_schema_context(self):
        ctx = build_context(self.schema)
        self.assertIn("DATABASE SCHEMA", ctx)
        self.assertIn("TABLE Artist", ctx)
        self.assertIn("TABLE Track", ctx)

    def test_filtered_schema_context(self):
        ctx = build_context(self.schema, selected_tables=["Artist", "Album"])
        self.assertIn("TABLE Artist", ctx)
        self.assertIn("TABLE Album", ctx)
        self.assertNotIn("TABLE Track", ctx)
        self.assertNotIn("TABLE Customer", ctx)

    def test_with_value_candidates(self):
        ctx = build_context(
            self.schema,
            selected_tables=["Customer"],
            value_candidates={"Customer.Country": ["France", "Germany", "Brazil"]},
        )
        self.assertIn("SAMPLE VALUES", ctx)
        self.assertIn("Customer.Country: France, Germany, Brazil", ctx)

    def test_value_candidates_without_filtering(self):
        ctx = build_context(
            self.schema,
            value_candidates={"Artist.Name": ["AC/DC", "Metallica"]},
        )
        self.assertIn("DATABASE SCHEMA", ctx)
        self.assertIn("SAMPLE VALUES", ctx)
        self.assertIn("Artist.Name: AC/DC, Metallica", ctx)

    def test_deterministic_output(self):
        ctx1 = build_context(
            self.schema,
            selected_tables=["Artist", "Album"],
            value_candidates={"Artist.Name": ["AC/DC"]},
        )
        ctx2 = build_context(
            self.schema,
            selected_tables=["Artist", "Album"],
            value_candidates={"Artist.Name": ["AC/DC"]},
        )
        self.assertEqual(ctx1, ctx2)

    def test_no_value_candidates_section_when_none(self):
        ctx = build_context(self.schema, selected_tables=["Artist"])
        self.assertNotIn("SAMPLE VALUES", ctx)


if __name__ == "__main__":
    unittest.main()
