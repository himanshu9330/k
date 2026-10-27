"""
SentinelAI-X SOC Dashboard & Analytics Routes
===============================================
Provides aggregated intelligence metrics, KPI cards data,
severity and status distributions, attack vectors, and MITRE mapping stats.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from models.incident import Incident, IncidentStatus, IncidentSeverity
from models.log import SecurityLog
from models.event import SecurityEvent
from models.response_action import ResponseAction, ActionStatus
from models.mitre import MitreTechnique
from schemas.common import ApiResponse
from schemas.dashboard import (
    DashboardSummary,
    SeverityCounts,
    StatusCounts,
    AttackDistributionItem,
    MitreDistributionItem,
    TopTargetItem,
    TopSourceIpItem
)
from routes.incident_routes import _format_incident_response

router = APIRouter(prefix="/dashboard", tags=["SOC Dashboard Analytics"])


@router.get("/summary", response_model=ApiResponse[DashboardSummary])
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Retrieve top-level KPI metrics and incident distributions for the SOC dashboard."""
    total_incidents = db.query(func.count(Incident.id)).scalar() or 0

    # Severity counts
    critical = db.query(func.count(Incident.id)).filter(Incident.severity == "CRITICAL").scalar() or 0
    high = db.query(func.count(Incident.id)).filter(Incident.severity == "HIGH").scalar() or 0
    medium = db.query(func.count(Incident.id)).filter(Incident.severity == "MEDIUM").scalar() or 0
    low = db.query(func.count(Incident.id)).filter(Incident.severity == "LOW").scalar() or 0

    # Status counts
    open_cnt = db.query(func.count(Incident.id)).filter(Incident.status == "OPEN").scalar() or 0
    inv_cnt = db.query(func.count(Incident.id)).filter(Incident.status == "INVESTIGATING").scalar() or 0
    con_cnt = db.query(func.count(Incident.id)).filter(Incident.status == "CONTAINED").scalar() or 0
    res_cnt = db.query(func.count(Incident.id)).filter(Incident.status == "RESOLVED").scalar() or 0
    fp_cnt = db.query(func.count(Incident.id)).filter(Incident.status == "FALSE_POSITIVE").scalar() or 0

    avg_score = db.query(func.avg(Incident.risk_score)).scalar() or 0.0
    total_logs = db.query(func.count(SecurityLog.id)).scalar() or 0
    total_events = db.query(func.count(SecurityEvent.id)).scalar() or 0
    pending_actions = db.query(func.count(ResponseAction.id)).filter(ResponseAction.status == ActionStatus.PROPOSED.value).scalar() or 0

    recent = db.query(Incident).order_by(desc(Incident.created_at)).limit(5).all()

    summary = DashboardSummary(
        total_incidents=total_incidents,
        severity_breakdown=SeverityCounts(critical=critical, high=high, medium=medium, low=low),
        status_breakdown=StatusCounts(open=open_cnt, investigating=inv_cnt, contained=con_cnt, resolved=res_cnt, false_positive=fp_cnt),
        average_risk_score=round(float(avg_score), 1),
        total_logs_processed=total_logs,
        total_events_normalized=total_events,
        pending_response_actions=pending_actions,
        recent_incidents=[_format_incident_response(i) for i in recent]
    )

    return ApiResponse(data=summary, message="Dashboard summary metrics retrieved")


@router.get("/attacks", response_model=ApiResponse[List[AttackDistributionItem]])
def get_attack_distribution(db: Session = Depends(get_db)):
    """Retrieve breakdown of incidents by classified attack type."""
    total = db.query(func.count(Incident.id)).scalar() or 1
    rows = (
        db.query(Incident.incident_type, func.count(Incident.id).label("count"))
        .group_by(Incident.incident_type)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )

    items = [
        AttackDistributionItem(
            incident_type=r[0],
            count=r[1],
            percentage=round((r[1] / total) * 100, 1)
        )
        for r in rows
    ]
    return ApiResponse(data=items, message="Attack distribution retrieved")


@router.get("/mitre", response_model=ApiResponse[List[MitreDistributionItem]])
def get_mitre_distribution(db: Session = Depends(get_db)):
    """Retrieve incident frequency across mapped MITRE ATT&CK techniques."""
    rows = (
        db.query(Incident.mitre_technique_id, func.count(Incident.id).label("count"))
        .filter(Incident.mitre_technique_id.isnot(None))
        .group_by(Incident.mitre_technique_id)
        .order_by(desc("count"))
        .limit(10)
        .all()
    )

    items = []
    for tid, count in rows:
        tech = db.query(MitreTechnique).filter(MitreTechnique.technique_id == tid).first()
        items.append(
            MitreDistributionItem(
                technique_id=tid,
                technique_name=tech.name if tech else "Unknown Technique",
                tactic=tech.tactic if tech else "Credential Access",
                count=count
            )
        )
    return ApiResponse(data=items, message="MITRE technique distribution retrieved")


@router.get("/top-sources", response_model=ApiResponse[List[TopSourceIpItem]])
def get_top_source_ips(db: Session = Depends(get_db)):
    """Retrieve top attacking source IPs by incident frequency."""
    rows = (
        db.query(
            Incident.source_ip,
            func.count(Incident.id).label("count"),
            func.sum(Incident.failed_attempts).label("failed"),
            Incident.severity
        )
        .filter(Incident.source_ip.isnot(None), Incident.source_ip != "Unknown")
        .group_by(Incident.source_ip)
        .order_by(desc("count"))
        .limit(8)
        .all()
    )

    items = [
        TopSourceIpItem(
            source_ip=r[0],
            incident_count=r[1],
            failed_attempts=int(r[2] or 0),
            severity=r[3]
        )
        for r in rows
    ]
    return ApiResponse(data=items, message="Top source IPs retrieved")


@router.get("/top-targets", response_model=ApiResponse[List[TopTargetItem]])
def get_top_targeted_services(db: Session = Depends(get_db)):
    """Retrieve most frequently targeted services."""
    rows = (
        db.query(Incident.target_service, func.count(Incident.id).label("count"))
        .filter(Incident.target_service.isnot(None))
        .group_by(Incident.target_service)
        .order_by(desc("count"))
        .limit(8)
        .all()
    )

    items = [
        TopTargetItem(
            target=r[0].upper() if r[0] else "GENERAL",
            count=r[1],
            service=r[0] or "general"
        )
        for r in rows
    ]
    return ApiResponse(data=items, message="Top targeted services retrieved")
