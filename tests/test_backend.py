import unittest
import sqlite3
from app.database import get_connection
from app.schema import (
    get_tables,
    table_exists,
    get_table_schema,
    get_foreign_keys,
    extract_schema,
)
from app.services import QueryService


class TestBackend(unittest.TestCase):

    def test_readonly_select(self):
        """Verify SELECT succeeds on read-only connection."""
        conn = get_connection()
        cursor = conn.execute("SELECT * FROM Artist LIMIT 5")
        rows = cursor.fetchall()
        conn.close()
        self.assertEqual(len(rows), 5)

    def test_readonly_delete_blocked(self):
        """Verify DELETE is blocked by SQLite mode=ro."""
        conn = get_connection()
        with self.assertRaises(sqlite3.OperationalError) as ctx:
            conn.execute("DELETE FROM Artist WHERE ArtistId = 1")
        conn.close()
        self.assertIn("readonly", str(ctx.exception).lower())

    def test_readonly_insert_blocked(self):
        """Verify INSERT is blocked by SQLite mode=ro."""
        conn = get_connection()
        with self.assertRaises(sqlite3.OperationalError) as ctx:
            conn.execute("INSERT INTO Artist (Name) VALUES ('Unauthorized')")
        conn.close()
        self.assertIn("readonly", str(ctx.exception).lower())

    def test_get_tables(self):
        """Verify all expected Chinook tables are discovered."""
        tables = get_tables()
        expected = [
            "Album", "Artist", "Customer", "Employee", "Genre",
            "Invoice", "InvoiceLine", "MediaType", "Playlist",
            "PlaylistTrack", "Track"
        ]
        for t in expected:
            self.assertIn(t, tables)

    def test_table_exists(self):
        """Verify table_exists returns True for valid tables and False for invalid."""
        self.assertTrue(table_exists("Artist"))
        self.assertTrue(table_exists("Track"))
        self.assertFalse(table_exists("NonExistentTable"))

    def test_table_schema_artist(self):
        """Verify Artist table schema and primary key."""
        schema = get_table_schema("Artist")
        self.assertIsNotNone(schema)
        col_names = [c["name"] for c in schema]
        self.assertIn("ArtistId", col_names)
        self.assertIn("Name", col_names)

        pk_col = next(c for c in schema if c["name"] == "ArtistId")
        self.assertTrue(pk_col["primary_key"])

    def test_foreign_keys_album(self):
        """Verify Album foreign keys reference Artist."""
        fks = get_foreign_keys("Album")
        self.assertIsNotNone(fks)
        self.assertTrue(any(
            fk["table"] == "Artist" and fk["column"] == "ArtistId" and fk["references_column"] == "ArtistId"
            for fk in fks
        ))

    def test_extract_schema(self):
        """Verify extract_schema returns a full DatabaseSchema model."""
        db_schema = extract_schema()
        self.assertGreaterEqual(len(db_schema.tables), 11)
        table_names = [t.name for t in db_schema.tables]
        self.assertIn("Artist", table_names)
        self.assertIn("Album", table_names)

    def test_query_service(self):
        """Verify QueryService executes SELECT and returns QueryResult."""
        result = QueryService.execute("SELECT ArtistId, Name FROM Artist LIMIT 3")
        self.assertEqual(result.columns, ["ArtistId", "Name"])
        self.assertEqual(result.row_count, 3)
        self.assertEqual(len(result.rows), 3)
        self.assertGreaterEqual(result.execution_time_ms, 0.0)


if __name__ == "__main__":
    unittest.main()
