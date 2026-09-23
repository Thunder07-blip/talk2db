import unittest
from app.schema import extract_schema
from app.llm.pipeline import ask

class TestPipelineAdvanced(unittest.TestCase):
    def setUp(self):
        self.schema = extract_schema()

    def test_correction_loop(self):
        import app.llm.pipeline
        original_generate = app.llm.pipeline.generate_sql
        original_linker = app.llm.pipeline.get_relevant_tables
        
        try:
            # Mock linker to return just Artist
            app.llm.pipeline.get_relevant_tables = lambda q, s: ["Artist"]
            
            # Mock generate_sql to fail first, then succeed
            call_count = 0
            def mock_generate(sys, user):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    return "SELECT FakeColumn FROM Artist"  # Will fail DB execution
                return "SELECT Name FROM Artist"  # Will succeed
                
            app.llm.pipeline.generate_sql = mock_generate
            
            result = ask("Show me artists")
            
            self.assertTrue(result.success)
            self.assertEqual(result.retries, 1)
            self.assertEqual(result.generated_sql, "SELECT Name FROM Artist")
            self.assertEqual(result.linked_tables, ["Artist"])
            self.assertEqual(call_count, 3)  # Call 1: Bad SQL, Call 2: Good SQL, Call 3: Summary
            
        finally:
            app.llm.pipeline.generate_sql = original_generate
            app.llm.pipeline.get_relevant_tables = original_linker
            
    def test_correction_loop_exhaustion(self):
        import app.llm.pipeline
        original_generate = app.llm.pipeline.generate_sql
        
        try:
            # Always return bad SQL
            app.llm.pipeline.generate_sql = lambda sys, user: "SELECT FakeColumn FROM Artist"
            
            result = ask("Show me artists", max_retries=2, selected_tables=["Artist"])
            
            self.assertFalse(result.success)
            self.assertEqual(result.retries, 1) # 0-indexed, so 2 attempts = max retry 1
            self.assertIn("no such column: FakeColumn", result.error)
            
        finally:
            app.llm.pipeline.generate_sql = original_generate
