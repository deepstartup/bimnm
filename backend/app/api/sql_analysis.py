"""SQL analysis and comparison API."""
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.sql_analysis import SQLAnalyzeRequest, SQLCompareRequest
from app.services.sql_analyzer import analyze_sql, compare_sql

router = APIRouter()


@router.post("/analyze")
def sql_analyze(
    body: SQLAnalyzeRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze SQL complexity, lineage, and migration recommendations."""
    return analyze_sql(body.sql_query)


@router.post("/compare")
def sql_compare(
    body: SQLCompareRequest,
    current_user: User = Depends(get_current_user),
):
    """Compare two SQL queries for similarity and differences."""
    return compare_sql(body.sql1, body.sql2)
