"""Report schemas."""
from pydantic import BaseModel
from typing import Optional


class ReportCreate(BaseModel):
    name: str
    description: Optional[str] = None
    report_type: Optional[str] = None
    sql_query: Optional[str] = None
    complexity_score: Optional[float] = None
    complexity_category: Optional[str] = None
    estimated_hours: Optional[float] = None
    source_system: Optional[str] = None


class ReportUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    report_type: Optional[str] = None
    sql_query: Optional[str] = None
    complexity_score: Optional[float] = None
    complexity_category: Optional[str] = None
    estimated_hours: Optional[float] = None
    source_system: Optional[str] = None
    migrated: Optional[bool] = None


class ReportResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    report_type: Optional[str] = None
    sql_query: Optional[str] = None
    complexity_score: Optional[float] = None
    complexity_category: Optional[str] = None
    estimated_hours: Optional[float] = None
    source_system: Optional[str] = None
    created_by: int
    migrated: bool

    class Config:
        from_attributes = True
