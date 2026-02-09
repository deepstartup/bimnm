"""COE analysis API."""
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.analysis import COEAnalysis
from app.api.deps import get_current_user
from app.services.coe_processor import process_coe_csv
from app.schemas.coe import COEAnalysisRecord

router = APIRouter()


@router.post("/upload")
def coe_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload COE CSV and run analysis. Returns full analysis result."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "CSV file required")
    try:
        content = file.file.read()
    except Exception as e:
        raise HTTPException(400, f"Failed to read file: {e}")
    try:
        result = process_coe_csv(content, file.filename)
    except Exception as e:
        raise HTTPException(400, f"Failed to process CSV: {str(e)}")
    if result.get("error"):
        raise HTTPException(400, result["error"])
    # Persist summary to DB
    import json
    record = COEAnalysis(
        filename=file.filename,
        report_count=result.get("report_count"),
        duplicate_count=result.get("duplicate_count"),
        unique_count=result.get("unique_count"),
        avg_complexity=result.get("avg_complexity"),
        total_estimated_hours=result.get("total_estimated_hours"),
        results_json=json.dumps(result),
        user_id=current_user.id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    result["analysis_id"] = record.id
    return result


@router.get("/results/{analysis_id}", response_model=dict)
def get_coe_results(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get stored COE analysis results by ID."""
    row = db.query(COEAnalysis).filter(
        COEAnalysis.id == analysis_id,
        COEAnalysis.user_id == current_user.id,
    ).first()
    if not row:
        raise HTTPException(404, "Analysis not found")
    import json
    if not row.results_json:
        raise HTTPException(404, "Results not available")
    data = json.loads(row.results_json)
    data["analysis_id"] = row.id
    data["filename"] = row.filename
    data["created_at"] = row.created_at.isoformat() if row.created_at else None
    return data


@router.get("/history", response_model=List[COEAnalysisRecord])
def coe_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List past COE analyses for the current user."""
    rows = (
        db.query(COEAnalysis)
        .filter(COEAnalysis.user_id == current_user.id)
        .order_by(COEAnalysis.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        COEAnalysisRecord(
            id=r.id,
            filename=r.filename,
            report_count=r.report_count,
            duplicate_count=r.duplicate_count,
            unique_count=r.unique_count,
            avg_complexity=r.avg_complexity,
            total_estimated_hours=r.total_estimated_hours,
            created_at=r.created_at.isoformat() if r.created_at else None,
        )
        for r in rows
    ]


@router.delete("/results/{analysis_id}", status_code=204)
def delete_coe_results(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a stored COE analysis."""
    row = db.query(COEAnalysis).filter(
        COEAnalysis.id == analysis_id,
        COEAnalysis.user_id == current_user.id,
    ).first()
    if not row:
        raise HTTPException(404, "Analysis not found")
    db.delete(row)
    db.commit()
    return None
