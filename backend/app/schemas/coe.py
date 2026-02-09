"""COE analysis schemas."""
from pydantic import BaseModel
from typing import Any, Optional


class COEAnalysisResult(BaseModel):
    report_count: int
    unique_count: int
    duplicate_count: int
    complexity_distribution: dict[str, int]
    total_estimated_hours: float
    avg_complexity: float
    duplicate_groups: list[dict[str, Any]]
    top_complex_reports: list[dict[str, Any]]
    reports_by_owner: dict[str, int]
    reports: list[dict[str, Any]]


class COEAnalysisRecord(BaseModel):
    id: int
    filename: str
    report_count: Optional[int] = None
    duplicate_count: Optional[int] = None
    unique_count: Optional[int] = None
    avg_complexity: Optional[float] = None
    total_estimated_hours: Optional[float] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
