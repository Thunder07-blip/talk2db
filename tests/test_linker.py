import unittest
from app.schema import extract_schema
from app.llm.linker import get_relevant_tables

class TestLinker(unittest.TestCase):
    def setUp(self):
        self.schema = extract_schema()

    def test_linker_basic(self):
        # We'll use a mocked LLM response to avoid live API calls in unit tests
        # Or we can just let it run if it's an integration test. Let's mock generate_sql.
        import app.llm.linker
        original_generate = app.llm.linker.generate_sql
        
        try:
            # Mock
            app.llm.linker.generate_sql = lambda sys, user: '["Artist", "Album"]'
            
            tables = get_relevant_tables("Who wrote this album?", self.schema)
            self.assertEqual(tables, ["Artist", "Album"])
            
            # Test invalid JSON fallback
            app.llm.linker.generate_sql = lambda sys, user: 'Sure, here are the tables: Artist, Album'
            tables_fallback = get_relevant_tables("Who wrote this album?", self.schema)
            self.assertEqual(len(tables_fallback), len(self.schema.tables))
            
            # Test markdown code block JSON
            app.llm.linker.generate_sql = lambda sys, user: '```json\n["Track"]\n```'
            tables_md = get_relevant_tables("List tracks", self.schema)
            self.assertEqual(tables_md, ["Track"])
            
            # Test invalid table filtering
            app.llm.linker.generate_sql = lambda sys, user: '["Artist", "FakeTable"]'
            tables_filtered = get_relevant_tables("Artist fake", self.schema)
            self.assertEqual(tables_filtered, ["Artist"])
            
        finally:
            app.llm.linker.generate_sql = original_generate
