"""
SentinelAI-X Incident Management Routes
=========================================
Provides endpoints for querying, filtering, updating incident status,
approving response recommendations, adding analyst notes, managing timelines,
and generating executive reports.
"""

import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from models.incident import Incident, IncidentStatus
from models.timeline import TimelineEvent
from models.threat import ThreatIndicator
from models.user import User
from schemas.common import ApiResponse, PaginationMeta
from schemas.incident import (
    IncidentResponse,
    IncidentDetailResponse,
    IncidentStatusUpdate,
    IncidentNoteAdd
)
from schemas.timeline import TimelineEventSchema, TimelineEventCreate
from schemas.threat import ThreatIndicatorSchema
from schemas.mitre import MitreTechniqueSchema
from schemas.risk import RiskAssessmentSchema, RiskFactorSchema
from schemas.response_action import ResponseActionSchema, ResponseActionStatusUpdate
from schemas.log import SecurityEventSchema
from services.auth_service import get_current_user
from services.incident_service import (
    get_incidents_paginated,
    get_incident_by_code,
    update_incident_status,
    update_response_action_status,
    add_incident_note
)
from services.report_service import generate_incident_report as generate_report_logic

router = APIRouter(prefix="/incidents", tags=["Incident Management"])


def _format_incident_response(inc: Incident) -> IncidentResponse:
    """Helper to convert Incident ORM model to Pydantic IncidentResponse."""
    accounts = []
    if inc.target_accounts:
        try:
            accounts = json.loads(inc.target_accounts)
        except Exception:
            accounts = [inc.target_accounts]

    return IncidentResponse(
        id=inc.id,
        incident_id=inc.incident_id,
        title=inc.title,
        description=inc.description,
        incident_type=inc.incident_type,
        severity=inc.severity,
        risk_score=inc.risk_score,
        risk_level=inc.risk_level,
        status=inc.status,
        source_ip=inc.source_ip,
        destination_ip=inc.destination_ip,
        target_service=inc.target_service,
        affected_asset=inc.affected_asset,
        target_accounts=accounts,
        failed_attempts=inc.failed_attempts,
        mitre_technique_id=inc.mitre_technique_id,
        confidence=inc.confidence,
        ai_status=inc.ai_status,
        created_at=inc.created_at,
        updated_at=inc.updated_at
    )


@router.get("", response_model=ApiResponse[List[IncidentResponse]])
def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    incident_type: Optional[str] = None,
    source_ip: Optional[str] = None,
    target_service: Optional[str] = None,
    mitre_technique: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retrieve filtered, paginated list of security incidents."""
    items, total = get_incidents_paginated(
        db=db,
        page=page,
        page_size=page_size,
        severity=severity,
        status=status,
        incident_type=incident_type,
        source_ip=source_ip,
        target_service=target_service,
        mitre_technique=mitre_technique,
        search=search
    )

    data = [_format_incident_response(i) for i in items]
    return ApiResponse(
        data=data,
        message=f"Retrieved {len(data)} of {total} incidents"
    )


@router.get("/{incident_id}", response_model=ApiResponse[IncidentDetailResponse])
def get_incident_details(incident_id: str, db: Session = Depends(get_db)):
    """Retrieve full deep-dive intelligence for a specific incident."""
    inc = get_incident_by_code(db, incident_id)
    if not inc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {incident_id} not found")

    base_res = _format_incident_response(inc)

    # Parse investigation steps
    inv_steps = []
    if inc.investigation_steps:
        try:
            inv_steps = json.loads(inc.investigation_steps)
        except Exception:
            inv_steps = [inc.investigation_steps]

    # Parse MITRE Technique
    mitre_schema = None
    if inc.mitre_technique:
        mitre_schema = MitreTechniqueSchema.model_validate(inc.mitre_technique)

    # Parse Risk Assessment
    risk_schema = None
    if inc.risk_assessment:
        ra = inc.risk_assessment
        factors = []
        if ra.factors_json:
            try:
                factors_raw = json.loads(ra.factors_json)
                factors = [RiskFactorSchema.model_validate(f) for f in factors_raw]
            except Exception:
                pass

        risk_schema = RiskAssessmentSchema(
            risk_score=ra.final_score,
            risk_level=ra.risk_level,
            base_score=ra.base_score,
            frequency_score=ra.frequency_score,
            privilege_score=ra.privilege_score,
            service_score=ra.service_score,
            pattern_score=ra.pattern_score,
            confidence_score=ra.confidence_score,
            formula=ra.formula,
            summary=ra.summary,
            factors=factors
        )

    # Response Actions
    resp_actions = [ResponseActionSchema.model_validate(a) for a in inc.response_actions]

    # Evidence events from parent log
    evidence_events = []
    if inc.log and inc.log.events:
        evidence_events = [SecurityEventSchema.model_validate(e) for e in inc.log.events[:50]]

    # Timeline events
    timeline_events = [TimelineEventSchema.model_validate(t) for t in inc.timeline_events]

    # Threat indicators
    threat_indicators = [ThreatIndicatorSchema.model_validate(i) for i in inc.threat_indicators]

    detail = IncidentDetailResponse(
        **base_res.model_dump(),
        ai_explanation=inc.ai_explanation,
        investigation_steps=inv_steps,
        analyst_notes=inc.analyst_notes,
        mitre_technique=mitre_schema,
        risk_assessment=risk_schema,
        response_actions=resp_actions,
        evidence_events=evidence_events,
        timeline_events=timeline_events,
        threat_indicators=threat_indicators
    )

    return ApiResponse(data=detail, message="Incident details retrieved successfully")


@router.patch("/{incident_id}/status", response_model=ApiResponse[IncidentResponse])
def change_incident_status(
    request: Request,
    incident_id: str,
    payload: IncidentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Transition incident lifecycle status:
    OPEN -> INVESTIGATING -> CONTAINED -> RESOLVED / FALSE_POSITIVE.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    try:
        updated = update_incident_status(
            db=db,
            incident_id=incident_id,
            new_status=payload.status,
            user=current_user,
            notes=payload.notes,
            client_ip=client_ip
        )
        return ApiResponse(
            data=_format_incident_response(updated),
            message=f"Incident {incident_id} status updated to {payload.status.upper()}"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/{incident_id}/notes", response_model=ApiResponse[IncidentDetailResponse])
def add_note_to_incident(
    request: Request,
    incident_id: str,
    payload: IncidentNoteAdd,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Append an analyst investigation note to the incident."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    try:
        add_incident_note(
            db=db,
            incident_id=incident_id,
            note_text=payload.note,
            user=current_user,
            client_ip=client_ip
        )
        return get_incident_details(incident_id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{incident_id}/timeline", response_model=ApiResponse[List[TimelineEventSchema]])
def get_incident_timeline(incident_id: str, db: Session = Depends(get_db)):
    """Retrieve chronological timeline events for the incident."""
    inc = get_incident_by_code(db, incident_id)
    if not inc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    events = db.query(TimelineEvent).filter(TimelineEvent.incident_id == inc.id).order_by(TimelineEvent.timestamp.asc()).all()
    return ApiResponse(
        data=[TimelineEventSchema.model_validate(e) for e in events],
        message="Incident timeline retrieved"
    )


@router.post("/{incident_id}/timeline", response_model=ApiResponse[TimelineEventSchema])
def create_custom_timeline_event(
    incident_id: str,
    payload: TimelineEventCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Add a custom timeline event to an incident."""
    inc = get_incident_by_code(db, incident_id)
    if not inc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    actor = current_user.full_name or current_user.username if current_user else (payload.actor or "Security Analyst")

    evt = TimelineEvent(
        incident_id=inc.id,
        event_type=payload.event_type.upper(),
        title=payload.title,
        description=payload.description,
        source=payload.source or "SOC Analyst",
        actor=actor,
        status_after=payload.status_after
    )
    db.add(evt)
    db.commit()
    db.refresh(evt)

    return ApiResponse(
        data=TimelineEventSchema.model_validate(evt),
        message="Timeline event created successfully"
    )


@router.get("/{incident_id}/iocs", response_model=ApiResponse[List[ThreatIndicatorSchema]])
def get_incident_iocs(incident_id: str, db: Session = Depends(get_db)):
    """Retrieve Indicators of Compromise linked to this incident."""
    inc = get_incident_by_code(db, incident_id)
    if not inc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    iocs = db.query(ThreatIndicator).filter(ThreatIndicator.incident_id == inc.id).all()
    return ApiResponse(
        data=[ThreatIndicatorSchema.model_validate(i) for i in iocs],
        message="Incident IOCs retrieved"
    )


@router.post("/{incident_id}/response-actions/{action_id}/status", response_model=ApiResponse[ResponseActionSchema])
def update_action_status(
    request: Request,
    incident_id: str,
    action_id: int,
    payload: ResponseActionStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Approve, reject, or mark a response recommendation as executed."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    try:
        action = update_response_action_status(
            db=db,
            action_id=action_id,
            new_status=payload.status,
            user=current_user,
            client_ip=client_ip
        )
        return ApiResponse(
            data=ResponseActionSchema.model_validate(action),
            message=f"Response action {action_id} status set to {payload.status.upper()}"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{incident_id}/report", response_model=ApiResponse[dict])
def generate_incident_report_endpoint(incident_id: str, db: Session = Depends(get_db)):
    """Generate a structured executive incident briefing report."""
    report = generate_report_logic(incident_id_str=incident_id, db=db)
    return ApiResponse(data=report, message="Incident report generated successfully")
