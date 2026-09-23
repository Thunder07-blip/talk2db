from typing import Any, Optional
from pydantic import BaseModel, Field


class ColumnSchema(BaseModel):
    name: str
    data_type: str
    nullable: bool
    primary_key: bool
    default_value: Optional[Any] = None


class ForeignKeySchema(BaseModel):
    column: str
    referenced_table: str
    referenced_column: str


class TableSchema(BaseModel):
    name: str
    columns: list[ColumnSchema] = Field(default_factory=list)
    foreign_keys: list[ForeignKeySchema] = Field(default_factory=list)


class DatabaseSchema(BaseModel):
    tables: list[TableSchema] = Field(default_factory=list)
