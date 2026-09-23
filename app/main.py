from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION
from app.schema import (
    get_tables,
    get_table_schema,
    get_foreign_keys,
    extract_schema,
)
from app.services import QueryService
from app.llm.pipeline import ask as talk2db_ask


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
)


class QueryRequest(BaseModel):
    sql: str


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def root():
    return FileResponse("app/static/index.html")


@app.get("/tables")
def tables():
    return {
        "tables": get_tables()
    }


@app.get("/schema/full")
def full_schema():
    """Return the complete database schema as structured JSON."""
    schema = extract_schema()
    return schema.model_dump()


@app.get("/schema/{table_name}")
def table_schema(table_name: str):
    columns = get_table_schema(table_name)

    if columns is None:
        raise HTTPException(
            status_code=404,
            detail=f"Table '{table_name}' not found",
        )

    return {
        "table": table_name,
        "columns": columns,
        "foreign_keys": get_foreign_keys(table_name),
    }


@app.post("/query")
def execute_query(request: QueryRequest):
    """Execute a read-only SQL query against the database.

    This endpoint is for development testing. It will be locked behind
    the safety layer in a later milestone.
    """
    result = QueryService.execute(request.sql)

    if not result.success:
        raise HTTPException(
            status_code=400,
            detail=result.error,
        )

    return result.model_dump()


class AskRequest(BaseModel):
    question: str
    selected_tables: Optional[list[str]] = None


@app.post("/ask")
def ask_question(request: AskRequest):
    """Ask a natural language question and get a database answer.

    The full pipeline: Question → Schema Context → LLM → SQL → Execute → Result
    """
    result = talk2db_ask(
        question=request.question,
        selected_tables=request.selected_tables,
    )
    return result.model_dump()
