import json
import re
from typing import Optional
from app.schema import DatabaseSchema, build_context
from app.llm.client import generate_sql
from app.llm.prompts import SCHEMA_LINKING_PROMPT, build_linking_prompt


def get_relevant_tables(question: str, schema: DatabaseSchema) -> list[str]:
    """Determine which tables are needed to answer the question using the LLM.
    
    Returns a list of table names. If parsing fails, returns all tables as a fallback.
    """
    # Build a lightweight context of JUST table names and columns (no sample values)
    schema_context = build_context(schema)
    
    user_prompt = build_linking_prompt(schema_context, question)
    
    # We use generate_sql but under the hood it's just generate_text
    response_text = generate_sql(SCHEMA_LINKING_PROMPT, user_prompt)
    
    # Clean up markdown fences if present
    text = response_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
        text = text.strip()
        
    try:
        tables = json.loads(text)
        if isinstance(tables, list):
            # Validate tables exist in schema
            valid_tables = [t.name for t in schema.tables]
            return [t for t in tables if t in valid_tables]
    except json.JSONDecodeError:
        pass
        
    # Fallback: if JSON decoding fails, return all tables
    return [t.name for t in schema.tables]
