"""Talk2DB text-to-SQL pipeline.

Orchestrates: Question → Schema Context → LLM → SQL → QueryService → Result
"""
import re
import time
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.schema import extract_schema, build_context, DatabaseSchema
from app.services import QueryService, QueryResult
from app.llm.client import generate_sql
from app.llm.linker import get_relevant_tables
from app.llm.prompts import (
    SYSTEM_PROMPT, build_user_prompt, 
    CORRECTION_PROMPT, build_correction_prompt,
    SUMMARY_PROMPT, build_summary_prompt
)


class Talk2DBResult(BaseModel):
    """Complete result from a natural language query."""
    question: str
    generated_sql: str
    query_result: Optional[QueryResult] = None
    summary: Optional[str] = None
    error: Optional[str] = None
    success: bool = True
    total_time_ms: float = 0.0
    llm_time_ms: float = 0.0
    retries: int = 0
    linked_tables: list[str] = Field(default_factory=list)


def _clean_sql(raw: str) -> str:
    """Clean the LLM response to extract a pure SQL query."""
    text = raw.strip()

    # Remove markdown code fences
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
        text = text.strip()

    # Take only the first statement if multiple exist
    if ";" in text:
        text = text.split(";")[0].strip()

    return text


def ask(
    question: str,
    schema: Optional[DatabaseSchema] = None,
    selected_tables: Optional[list[str]] = None,
    value_candidates: Optional[dict[str, list[str]]] = None,
    max_rows: int = 100,
    max_retries: int = 3,
) -> Talk2DBResult:
    """Ask a natural language question and get a database answer.

    The pipeline: Linker → Context Builder → LLM → AST Validator → Execute → (Correction Loop)
    """
    total_start = time.perf_counter()
    llm_total_ms = 0.0

    try:
        # Step 1: Get schema
        if schema is None:
            schema = extract_schema()

        # Step 2: Schema Linking
        if selected_tables is None:
            llm_start = time.perf_counter()
            selected_tables = get_relevant_tables(question, schema)
            llm_total_ms += (time.perf_counter() - llm_start) * 1000

        # Step 3: Build context for LLM
        schema_context = build_context(
            schema,
            selected_tables=selected_tables,
            value_candidates=value_candidates,
        )

        last_error = None
        current_sql = ""
        query_result = None

        # Step 4: Generation and Correction Loop
        for attempt in range(max_retries):
            llm_start = time.perf_counter()
            
            if attempt == 0:
                user_prompt = build_user_prompt(schema_context, question)
                raw_sql = generate_sql(SYSTEM_PROMPT, user_prompt)
            else:
                user_prompt = build_correction_prompt(schema_context, question, current_sql, last_error)
                raw_sql = generate_sql(CORRECTION_PROMPT, user_prompt)
                
            llm_total_ms += (time.perf_counter() - llm_start) * 1000
            current_sql = _clean_sql(raw_sql)

            if not current_sql:
                last_error = "LLM returned empty SQL"
                continue

            # Step 5: Execute SQL (AST validation happens inside QueryService)
            query_result = QueryService.execute(current_sql, max_rows=max_rows)
            
            if query_result.success:
                # Step 6: Generate Summary
                llm_start = time.perf_counter()
                summary_prompt = build_summary_prompt(question, current_sql, query_result.rows)
                summary = generate_sql(SUMMARY_PROMPT, summary_prompt)
                llm_total_ms += (time.perf_counter() - llm_start) * 1000
                
                total_time_ms = round((time.perf_counter() - total_start) * 1000, 2)
                return Talk2DBResult(
                    question=question,
                    generated_sql=current_sql,
                    query_result=query_result,
                    summary=summary,
                    success=True,
                    total_time_ms=total_time_ms,
                    llm_time_ms=round(llm_total_ms, 2),
                    retries=attempt,
                    linked_tables=selected_tables,
                )
            else:
                last_error = query_result.error

        # If we exhausted retries and still failed
        total_time_ms = round((time.perf_counter() - total_start) * 1000, 2)
        return Talk2DBResult(
            question=question,
            generated_sql=current_sql,
            query_result=query_result,
            error=last_error,
            success=False,
            total_time_ms=total_time_ms,
            llm_time_ms=round(llm_total_ms, 2),
            retries=max_retries - 1,
            linked_tables=selected_tables,
        )

    except Exception as e:
        total_time_ms = round((time.perf_counter() - total_start) * 1000, 2)
        return Talk2DBResult(
            question=question,
            generated_sql="",
            error=str(e),
            success=False,
            total_time_ms=total_time_ms,
            llm_time_ms=round(llm_total_ms, 2),
        )
