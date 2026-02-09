"""Report business logic."""
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.report import Report
from app.schemas.report import ReportCreate, ReportUpdate


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_reports(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Report]:
        return (
            self.db.query(Report)
            .filter(Report.created_by == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_report(self, report_id: int, user_id: int) -> Optional[Report]:
        return (
            self.db.query(Report)
            .filter(and_(Report.id == report_id, Report.created_by == user_id))
            .first()
        )

    def create_report(self, data: ReportCreate, user_id: int) -> Report:
        report = Report(**data.model_dump(), created_by=user_id)
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def update_report(
        self,
        report_id: int,
        data: ReportUpdate,
        user_id: int,
    ) -> Optional[Report]:
        report = self.get_report(report_id, user_id)
        if not report:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(report, key, value)
        self.db.commit()
        self.db.refresh(report)
        return report

    def delete_report(self, report_id: int, user_id: int) -> bool:
        report = self.get_report(report_id, user_id)
        if not report:
            return False
        self.db.delete(report)
        self.db.commit()
        return True
