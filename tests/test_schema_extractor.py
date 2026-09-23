"""Deep schema extraction tests for Chinook database."""
import unittest
from app.schema import (
    get_tables,
    table_exists,
    get_table_schema,
    get_foreign_keys,
    extract_schema,
    DatabaseSchema,
)


EXPECTED_TABLES = [
    "Album", "Artist", "Customer", "Employee", "Genre",
    "Invoice", "InvoiceLine", "MediaType", "Playlist",
    "PlaylistTrack", "Track",
]


class TestSchemaExtractor(unittest.TestCase):

    def setUp(self):
        self.schema = extract_schema()
        self._table_map = {t.name: t for t in self.schema.tables}

    # --- Table discovery ---

    def test_all_11_chinook_tables_discovered(self):
        table_names = get_tables()
        self.assertEqual(len(table_names), 11)
        for t in EXPECTED_TABLES:
            self.assertIn(t, table_names)

    def test_table_names_are_sorted(self):
        table_names = get_tables()
        self.assertEqual(table_names, sorted(table_names))

    def test_no_sqlite_system_tables(self):
        table_names = get_tables()
        for t in table_names:
            self.assertFalse(t.startswith("sqlite_"))

    # --- table_exists ---

    def test_table_exists_valid(self):
        for t in EXPECTED_TABLES:
            self.assertTrue(table_exists(t), f"{t} should exist")

    def test_table_exists_invalid(self):
        self.assertFalse(table_exists("NonExistent"))
        self.assertFalse(table_exists(""))
        self.assertFalse(table_exists("artist"))  # case-sensitive name check

    # --- Artist schema ---

    def test_artist_columns(self):
        schema = get_table_schema("Artist")
        self.assertIsNotNone(schema)
        col_names = [c["name"] for c in schema]
        self.assertEqual(col_names, ["ArtistId", "Name"])

    def test_artist_pk(self):
        schema = get_table_schema("Artist")
        pk_col = next(c for c in schema if c["name"] == "ArtistId")
        self.assertTrue(pk_col["primary_key"])
        non_pk = next(c for c in schema if c["name"] == "Name")
        self.assertFalse(non_pk["primary_key"])

    def test_artist_no_foreign_keys(self):
        fks = get_foreign_keys("Artist")
        self.assertIsNotNone(fks)
        self.assertEqual(len(fks), 0)

    # --- Album schema ---

    def test_album_fk_references_artist(self):
        fks = get_foreign_keys("Album")
        self.assertIsNotNone(fks)
        self.assertTrue(any(
            fk["table"] == "Artist"
            and fk["column"] == "ArtistId"
            and fk["references_column"] == "ArtistId"
            for fk in fks
        ))

    # --- Track schema (3 FKs) ---

    def test_track_has_three_foreign_keys(self):
        fks = get_foreign_keys("Track")
        self.assertIsNotNone(fks)
        self.assertEqual(len(fks), 3)

    def test_track_fk_album(self):
        fks = get_foreign_keys("Track")
        self.assertTrue(any(
            fk["table"] == "Album" and fk["column"] == "AlbumId"
            for fk in fks
        ))

    def test_track_fk_mediatype(self):
        fks = get_foreign_keys("Track")
        self.assertTrue(any(
            fk["table"] == "MediaType" and fk["column"] == "MediaTypeId"
            for fk in fks
        ))

    def test_track_fk_genre(self):
        fks = get_foreign_keys("Track")
        self.assertTrue(any(
            fk["table"] == "Genre" and fk["column"] == "GenreId"
            for fk in fks
        ))

    # --- PlaylistTrack (composite PK + 2 FKs) ---

    def test_playlisttrack_composite_pk(self):
        schema = get_table_schema("PlaylistTrack")
        pk_cols = [c for c in schema if c["primary_key"]]
        self.assertEqual(len(pk_cols), 2)
        pk_names = {c["name"] for c in pk_cols}
        self.assertEqual(pk_names, {"PlaylistId", "TrackId"})

    def test_playlisttrack_has_two_foreign_keys(self):
        fks = get_foreign_keys("PlaylistTrack")
        self.assertEqual(len(fks), 2)

    # --- InvoiceLine (2 FKs) ---

    def test_invoiceline_has_two_foreign_keys(self):
        fks = get_foreign_keys("InvoiceLine")
        self.assertEqual(len(fks), 2)

    def test_invoiceline_fk_invoice(self):
        fks = get_foreign_keys("InvoiceLine")
        self.assertTrue(any(
            fk["table"] == "Invoice" and fk["column"] == "InvoiceId"
            for fk in fks
        ))

    def test_invoiceline_fk_track(self):
        fks = get_foreign_keys("InvoiceLine")
        self.assertTrue(any(
            fk["table"] == "Track" and fk["column"] == "TrackId"
            for fk in fks
        ))

    # --- extract_schema() typed model ---

    def test_extract_schema_returns_database_schema(self):
        self.assertIsInstance(self.schema, DatabaseSchema)

    def test_extract_schema_has_all_tables(self):
        table_names = [t.name for t in self.schema.tables]
        for t in EXPECTED_TABLES:
            self.assertIn(t, table_names)

    def test_extract_schema_artist_columns_typed(self):
        artist = self._table_map["Artist"]
        self.assertEqual(len(artist.columns), 2)
        self.assertEqual(artist.columns[0].name, "ArtistId")
        self.assertEqual(artist.columns[0].data_type, "INTEGER")
        self.assertTrue(artist.columns[0].primary_key)

    def test_extract_schema_album_fk_typed(self):
        album = self._table_map["Album"]
        self.assertEqual(len(album.foreign_keys), 1)
        fk = album.foreign_keys[0]
        self.assertEqual(fk.column, "ArtistId")
        self.assertEqual(fk.referenced_table, "Artist")
        self.assertEqual(fk.referenced_column, "ArtistId")

    def test_schema_is_deterministic(self):
        schema2 = extract_schema()
        self.assertEqual(self.schema.model_dump(), schema2.model_dump())

    def test_nonexistent_table_returns_none(self):
        self.assertIsNone(get_table_schema("FakeTable"))
        self.assertIsNone(get_foreign_keys("FakeTable"))


if __name__ == "__main__":
    unittest.main()
