"""Dashboard stats API."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.report import Report
from app.models.analysis import COEAnalysis
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/stats")
def dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Aggregate KPIs for dashboard: reports, complexity breakdown, COE history."""
    reports = (
        db.query(Report)
        .filter(Report.created_by == current_user.id)
        .all()
    )
    total_reports = len(reports)
    migrated = sum(1 for r in reports if getattr(r, "migrated", False))
    complexity_breakdown = {"simple": 0, "medium": 0, "complex": 0, "very_complex": 0}
    total_hours = 0.0
    for r in reports:
        cat = (r.complexity_category or "").lower().replace(" ", "_")
        if cat in complexity_breakdown:
            complexity_breakdown[cat] += 1
        else:
            if (r.complexity_score or 0) <= 5:
                complexity_breakdown["simple"] += 1
            elif (r.complexity_score or 0) <= 15:
                complexity_breakdown["medium"] += 1
            elif (r.complexity_score or 0) <= 30:
                complexity_breakdown["complex"] += 1
            else:
                complexity_breakdown["very_complex"] += 1
        total_hours += r.estimated_hours or (r.complexity_score or 0) * 0.5
    coe_count = db.query(COEAnalysis).filter(COEAnalysis.user_id == current_user.id).count()
    return {
        "total_reports": total_reports,
        "reports_migrated": migrated,
        "migration_progress_percent": round(100 * migrated / total_reports, 1) if total_reports else 0,
        "complexity_breakdown": complexity_breakdown,
        "estimated_total_hours": round(total_hours, 1),
        "coe_analyses_count": coe_count,
    }
