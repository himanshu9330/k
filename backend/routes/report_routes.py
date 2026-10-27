"""
SentinelAI-X Security Reports REST Routes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from models.report import Report
from schemas.common import ApiResponse
from schemas.report import ReportCreate, ReportResponse
from services.report_service import generate_incident_report

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/generate", response_model=ApiResponse[ReportResponse])
def create_report(req: ReportCreate, db: Session = Depends(get_db)):
    """
    Generate a formal CISO Executive Incident Briefing, Technical Report,
    or Compliance Audit Report.
    """
    if not req.incident_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="incident_id is required to generate a report"
        )

    report_data = generate_incident_report(
        incident_id_str=req.incident_id,
        report_type=req.report_type,
        custom_notes=req.analyst_notes,
        db=db
    )

    # Fetch the newly persisted report
    saved_report = db.query(Report).filter(Report.report_id == report_data["report_id"]).first()
    if not saved_report:
        raise HTTPException(status_code=500, detail="Failed to save report")

    return ApiResponse(
        data=ReportResponse.model_validate(saved_report),
        message=f"Report {saved_report.report_id} generated and saved successfully"
    )


@router.get("", response_model=ApiResponse[List[ReportResponse]])
def list_reports(
    report_type: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all generated reports.
    """
    query = db.query(Report)
    if report_type:
        query = query.filter(Report.report_type == report_type.upper())
    
    reports = query.order_by(desc(Report.created_at)).limit(limit).all()
    return ApiResponse(
        data=[ReportResponse.model_validate(r) for r in reports],
        message="Reports retrieved successfully"
    )


@router.get("/{report_id}", response_model=ApiResponse[ReportResponse])
def get_report(report_id: str, db: Session = Depends(get_db)):
    """
    Get a single report by ID.
    """
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return ApiResponse(
        data=ReportResponse.model_validate(report),
        message="Report retrieved successfully"
    )
