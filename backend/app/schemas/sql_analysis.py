"""SQL analysis request/response schemas."""
from pydantic import BaseModel
from typing import Optional, List, Any


class SQLAnalyzeRequest(BaseModel):
    sql_query: str


class SQLCompareRequest(BaseModel):
    sql1: str
    sql2: str
