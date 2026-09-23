"""Comprehensive query execution tests using Chinook database."""
import unittest
from app.services import QueryService


class TestQueryServiceBasic(unittest.TestCase):

    def test_simple_select(self):
        result = QueryService.execute("SELECT * FROM Artist LIMIT 5")
        self.assertTrue(result.success)
        self.assertEqual(result.row_count, 5)
        self.assertIn("ArtistId", result.columns)
        self.assertIn("Name", result.columns)

    def test_select_with_where(self):
        result = QueryService.execute(
            "SELECT Name FROM Artist WHERE ArtistId = 1"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.row_count, 1)
        self.assertEqual(result.rows[0]["Name"], "AC/DC")

    def test_select_with_order_by_limit(self):
        result = QueryService.execute(
            "SELECT Name FROM Artist ORDER BY Name ASC LIMIT 3"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.row_count, 3)
        # Names should be alphabetically sorted
        names = [r["Name"] for r in result.rows]
        self.assertEqual(names, sorted(names))

    def test_select_count(self):
        result = QueryService.execute("SELECT COUNT(*) as cnt FROM Artist")
        self.assertTrue(result.success)
        self.assertEqual(result.row_count, 1)
        self.assertGreater(result.rows[0]["cnt"], 0)

    def test_select_group_by(self):
        result = QueryService.execute(
            "SELECT Country, COUNT(*) as cnt FROM Customer GROUP BY Country ORDER BY cnt DESC LIMIT 5"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.row_count, 5)
        self.assertIn("Country", result.columns)
        self.assertIn("cnt", result.columns)

    def test_inner_join(self):
        result = QueryService.execute(
            "SELECT Album.Title, Artist.Name "
            "FROM Album INNER JOIN Artist ON Album.ArtistId = Artist.ArtistId "
            "LIMIT 5"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.row_count, 5)
        self.assertIn("Title", result.columns)
        self.assertIn("Name", result.columns)

    def test_multi_table_join(self):
        """Test a 3-table join: Track -> Album -> Artist."""
        result = QueryService.execute(
            "SELECT Track.Name as TrackName, Album.Title as AlbumTitle, Artist.Name as ArtistName "
            "FROM Track "
            "INNER JOIN Album ON Track.AlbumId = Album.AlbumId "
            "INNER JOIN Artist ON Album.ArtistId = Artist.ArtistId "
            "LIMIT 5"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.row_count, 5)
        self.assertIn("TrackName", result.columns)
        self.assertIn("AlbumTitle", result.columns)
        self.assertIn("ArtistName", result.columns)

    def test_aggregation_over_join(self):
        """Test aggregation over joined tables: top customers by spend."""
        result = QueryService.execute(
            "SELECT Customer.FirstName, Customer.LastName, SUM(Invoice.Total) as TotalSpent "
            "FROM Customer "
            "INNER JOIN Invoice ON Customer.CustomerId = Invoice.CustomerId "
            "GROUP BY Customer.CustomerId "
            "ORDER BY TotalSpent DESC "
            "LIMIT 5"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.row_count, 5)
        self.assertIn("TotalSpent", result.columns)
        # Verify amounts are sorted descending
        amounts = [r["TotalSpent"] for r in result.rows]
        self.assertEqual(amounts, sorted(amounts, reverse=True))

    def test_query_returning_zero_rows(self):
        result = QueryService.execute(
            "SELECT * FROM Artist WHERE Name = 'ThisArtistDoesNotExist999'"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.row_count, 0)
        self.assertEqual(result.rows, [])

    def test_execution_time_measured(self):
        result = QueryService.execute("SELECT * FROM Track LIMIT 10")
        self.assertTrue(result.success)
        self.assertGreaterEqual(result.execution_time_ms, 0.0)


class TestQueryServiceErrors(unittest.TestCase):

    def test_invalid_sql_syntax(self):
        result = QueryService.execute("SLECT * FROM Artist")
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)

    def test_nonexistent_table(self):
        result = QueryService.execute("SELECT * FROM nonexistent_table")
        self.assertFalse(result.success)
        self.assertIn("no such table", result.error)

    def test_nonexistent_column(self):
        result = QueryService.execute("SELECT FakeColumn FROM Artist")
        self.assertFalse(result.success)
        self.assertIn("no such column", result.error)

    def test_delete_rejected(self):
        result = QueryService.execute("DELETE FROM Artist WHERE ArtistId = 1")
        self.assertFalse(result.success)
        self.assertIn("DELETE", result.error)

    def test_insert_rejected(self):
        result = QueryService.execute(
            "INSERT INTO Artist (Name) VALUES ('Hacker')"
        )
        self.assertFalse(result.success)
        self.assertIn("INSERT", result.error)

    def test_drop_rejected(self):
        result = QueryService.execute("DROP TABLE Artist")
        self.assertFalse(result.success)
        self.assertIn("DROP", result.error)

    def test_update_rejected(self):
        result = QueryService.execute(
            "UPDATE Artist SET Name = 'Hacked' WHERE ArtistId = 1"
        )
        self.assertFalse(result.success)
        self.assertIn("UPDATE", result.error)

    def test_empty_sql_rejected(self):
        result = QueryService.execute("")
        self.assertFalse(result.success)
        self.assertIn("Empty", result.error)

    def test_whitespace_only_sql_rejected(self):
        result = QueryService.execute("   \n  \t  ")
        self.assertFalse(result.success)
        self.assertIn("Empty", result.error)


class TestQueryServiceLimits(unittest.TestCase):

    def test_default_limit_100(self):
        """Track table has >100 rows, default should truncate."""
        result = QueryService.execute("SELECT * FROM Track")
        self.assertTrue(result.success)
        self.assertEqual(result.row_count, 100)
        self.assertTrue(result.truncated)

    def test_custom_max_rows(self):
        result = QueryService.execute("SELECT * FROM Track", max_rows=10)
        self.assertTrue(result.success)
        self.assertEqual(result.row_count, 10)
        self.assertTrue(result.truncated)

    def test_no_truncation_when_under_limit(self):
        result = QueryService.execute("SELECT * FROM Genre")
        self.assertTrue(result.success)
        self.assertFalse(result.truncated)

    def test_truncated_false_with_limit_clause(self):
        result = QueryService.execute("SELECT * FROM Artist LIMIT 5")
        self.assertTrue(result.success)
        self.assertEqual(result.row_count, 5)
        self.assertFalse(result.truncated)

    def test_with_clause_allowed(self):
        result = QueryService.execute(
            "WITH top_artists AS (SELECT * FROM Artist LIMIT 5) "
            "SELECT * FROM top_artists"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.row_count, 5)


if __name__ == "__main__":
    unittest.main()
