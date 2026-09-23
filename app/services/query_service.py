import time
import sqlite3
from typing import Any, Optional
from pydantic import BaseModel, Field
from app.database import get_connection


class QueryResult(BaseModel):
    """Structured result from a SQL query execution."""
    columns: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    execution_time_ms: float = 0.0
    truncated: bool = False
    error: Optional[str] = None
    success: bool = True


from app.services.validator import validate_sql_ast


class QueryService:
    """Service responsible for executing read-only SQL queries against the database."""

    @staticmethod
    def execute(sql: str, max_rows: int = 100) -> QueryResult:
        """Execute a read-only SQL query and return structured results.

        Args:
            sql: The SQL query string to execute.
            max_rows: Maximum number of rows to return. Defaults to 100.

        Returns:
            QueryResult with columns, rows, timing, and error information.
        """
        # Validate SQL before execution
        validation_error = validate_sql_ast(sql)
        if validation_error:
            return QueryResult(
                error=validation_error,
                success=False,
            )

        conn = get_connection()
        start_time = time.perf_counter()
        try:
            cursor = conn.execute(sql)
            columns = [col[0] for col in cursor.description] if cursor.description else []
            raw_rows = cursor.fetchall()
            execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

            rows = [dict(row) for row in raw_rows]
            truncated = len(rows) > max_rows
            if truncated:
                rows = rows[:max_rows]

            return QueryResult(
                columns=columns,
                rows=rows,
                row_count=len(rows),
                execution_time_ms=execution_time_ms,
                truncated=truncated,
            )
        except sqlite3.OperationalError as e:
            execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return QueryResult(
                error=str(e),
                success=False,
                execution_time_ms=execution_time_ms,
            )
        except sqlite3.DatabaseError as e:
            execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return QueryResult(
                error=str(e),
                success=False,
                execution_time_ms=execution_time_ms,
            )
        finally:
            conn.close()
