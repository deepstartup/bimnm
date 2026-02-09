"""Report API endpoints."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.report import ReportCreate, ReportUpdate, ReportResponse
from app.services.report_service import ReportService
from app.services.report_consolidator import consolidate_reports
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ReportResponse])
def list_reports(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all reports for the current user."""
    service = ReportService(db)
    return service.get_user_reports(current_user.id, skip=skip, limit=limit)


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    report: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new report."""
    service = ReportService(db)
    return service.create_report(report, current_user.id)


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get report by ID."""
    service = ReportService(db)
    report = service.get_report(report_id, current_user.id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.put("/{report_id}", response_model=ReportResponse)
def update_report(
    report_id: int,
    report: ReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a report."""
    service = ReportService(db)
    updated = service.update_report(report_id, report, current_user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Report not found")
    return updated


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a report."""
    service = ReportService(db)
    if not service.delete_report(report_id, current_user.id):
        raise HTTPException(status_code=404, detail="Report not found")
    return None


@router.post("/consolidate")
def report_consolidate(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Find duplicate and near-duplicate reports for the current user."""
    service = ReportService(db)
    reports = service.get_user_reports(current_user.id, skip=0, limit=1000)
    return consolidate_reports(reports)
