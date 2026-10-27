"""
SentinelAI-X Log Ingestion Routes
===================================
Endpoints for uploading, parsing, normalizing, and listing security log data.
"""

import os
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.config import settings
from app.database import get_db
from models.log import SecurityLog
from models.user import User
from schemas.common import ApiResponse
from schemas.log import SecurityLogResponse, LogUploadResult, SecurityEventSchema
from services.auth_service import get_current_user
from services.incident_service import process_log_and_create_incident

router = APIRouter(prefix="/logs", tags=["Log Ingestion"])


def _validate_uploaded_file(file: UploadFile, content: bytes) -> str:
    """Sanitize filename and enforce size and extension constraints."""
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file has no filename.")

    # Prevent path traversal
    safe_filename = os.path.basename(file.filename)
    if ".." in safe_filename or "/" in safe_filename or "\\" in safe_filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename format.")

    # Extension validation
    ext = os.path.splitext(safe_filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Size limit
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum upload limit of {settings.MAX_UPLOAD_SIZE_BYTES / (1024*1024):.1f} MB."
        )

    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    return safe_filename


@router.post("/upload", response_model=ApiResponse[LogUploadResult])
async def upload_security_log(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Ingest and process a security log file.
    Executes parsing, deterministic threat detection, Gemini analysis,
    risk scoring, MITRE mapping, and incident persistence.
    """
    content = await file.read()
    safe_filename = _validate_uploaded_file(file, content)

    try:
        raw_text = content.decode("utf-8")
    except UnicodeDecodeError:
        raw_text = content.decode("latin-1", errors="replace")

    client_ip = request.client.host if request.client else "127.0.0.1"

    result = process_log_and_create_incident(
        db=db,
        filename=safe_filename,
        raw_content=raw_text,
        user=current_user,
        client_ip=client_ip
    )

    upload_data = LogUploadResult(
        log_id=result["log_id"],
        filename=result["filename"],
        file_size=result["file_size"],
        log_format=result["log_format"],
        event_count=result["event_count"],
        events=[SecurityEventSchema.model_validate(e) for e in result["events"][:50]],
        incident_id=result.get("incident_id"),
        risk_score=result.get("risk_score"),
        risk_level=result.get("risk_level"),
        ai_status=result.get("ai_status")
    )

    return ApiResponse(
        data=upload_data,
        message=f"Log parsed and analyzed successfully. Incident {result.get('incident_id')} created."
    )


@router.get("", response_model=ApiResponse[List[SecurityLogResponse]])
def list_logs(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """List historical ingested log files with pagination."""
    offset = (page - 1) * page_size
    logs = db.query(SecurityLog).order_by(desc(SecurityLog.created_at)).offset(offset).limit(page_size).all()
    return ApiResponse(
        data=[SecurityLogResponse.model_validate(l) for l in logs],
        message="Logs retrieved successfully"
    )


@router.get("/{log_id}", response_model=ApiResponse[dict])
def get_log_details(log_id: int, db: Session = Depends(get_db)):
    """Retrieve full details of a specific uploaded log and its normalized events."""
    log = db.query(SecurityLog).filter(SecurityLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")

    events = [SecurityEventSchema.model_validate(e) for e in log.events]
    return ApiResponse(
        data={
            "log": SecurityLogResponse.model_validate(log),
            "events": events,
            "raw_content_preview": log.raw_content[:2000]
        },
        message="Log details retrieved"
    )