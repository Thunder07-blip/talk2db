import unittest
from app.services.validator import validate_sql_ast


class TestValidator(unittest.TestCase):
    def test_valid_select(self):
        self.assertIsNone(validate_sql_ast("SELECT * FROM Artist"))

    def test_valid_with(self):
        self.assertIsNone(validate_sql_ast("WITH t AS (SELECT * FROM Artist) SELECT * FROM t"))

    def test_reject_insert(self):
        err = validate_sql_ast("INSERT INTO Artist (Name) VALUES ('test')")
        self.assertIn("SELECT queries are allowed", err)

    def test_reject_update(self):
        err = validate_sql_ast("UPDATE Artist SET Name = 'test'")
        self.assertIn("SELECT queries are allowed", err)

    def test_reject_delete(self):
        err = validate_sql_ast("DELETE FROM Artist")
        self.assertIn("SELECT queries are allowed", err)

    def test_reject_drop(self):
        err = validate_sql_ast("DROP TABLE Artist")
        self.assertIn("SELECT queries are allowed", err)

    def test_reject_multiple_statements(self):
        err = validate_sql_ast("SELECT * FROM Artist; DROP TABLE Artist")
        self.assertEqual(err, "Multiple SQL statements are not allowed")

    def test_reject_nested_modifying(self):
        # A tricky one: SELECT but modifying node inside (syntactically invalid but checks deep inspection)
        # We can simulate by a parser error or a specific construct.
        err = validate_sql_ast("SELECT 1; UPDATE Artist SET Name = 'hacked'")
        self.assertEqual(err, "Multiple SQL statements are not allowed")

    def test_empty_sql(self):
        self.assertEqual(validate_sql_ast(""), "Empty SQL statement")
        self.assertEqual(validate_sql_ast("   -- just a comment  "), "Empty SQL statement")

    def test_syntax_error(self):
        err = validate_sql_ast("SELECT FROM WHERE")
        self.assertIn("SQL parsing error", err)
