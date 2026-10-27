"""
SentinelAI-X Forensic Audit Log Routes
========================================
Endpoints for querying and filtering the immutable audit trail.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from models.audit import AuditLog
from schemas.common import ApiResponse
from schemas.audit import AuditLogSchema
from services.audit_service import get_audit_logs

router = APIRouter(prefix="/audit", tags=["Forensic Audit Trail"])


@router.get("", response_model=ApiResponse[List[AuditLogSchema]])
def list_audit_trail(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve filtered, paginated forensic audit records."""
    logs, total = get_audit_logs(
        db=db,
        page=page,
        page_size=page_size,
        action=action,
        entity_type=entity_type,
        search=search
    )

    data = [AuditLogSchema.model_validate(l) for l in logs]
    return ApiResponse(
        data=data,
        message=f"Retrieved {len(data)} of {total} audit records"
    )
