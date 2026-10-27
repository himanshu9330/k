"""
SentinelAI-X Incident Lifecycle & Ingestion Orchestration Service
==================================================================
Coordinates the end-to-end cybersecurity pipeline:
1. Log Ingestion & Validation
2. Multi-Format Event Normalization
3. Deterministic Rule-Based Threat Detection
4. Generative AI Security Analysis (Gemini / Fallback)
5. Deterministic Multi-Factor Risk Scoring
6. MITRE ATT&CK Technique Mapping
7. Incident Entity Creation (INC-XXXXXX)
8. Response Recommendation Synthesis (Human-in-the-Loop)
9. Timeline Event Logging & IOC Correlation
10. Database Persistence & Forensics Audit Logging
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from models.incident import Incident, IncidentStatus, IncidentSeverity
from models.log import SecurityLog
from models.event import SecurityEvent
from models.risk_assessment import RiskAssessment
from models.response_action import ResponseAction, ActionStatus
from models.mitre import MitreTechnique
from models.timeline import TimelineEvent
from models.threat import ThreatIndicator
from models.user import User

from services.parser_service import parse_log
from services.detection_service import detect_threats
from services.gemini_service import analyze_security_events
from services.risk_service import calculate_risk_score
from services.mitre_service import map_technique_from_evidence, seed_mitre_database
from services.response_service import generate_response_recommendations
from services.threat_service import enrich_indicator
from services.audit_service import log_audit_event

logger = logging.getLogger("sentinelai.incident")


def _generate_incident_id(db: Session) -> str:
    """Generate next sequential human-readable incident identifier (INC-000001)."""
    count = db.query(func.count(Incident.id)).scalar() or 0
    return f"INC-{count + 1:06d}"


def process_log_and_create_incident(
    db: Session,
    filename: str,
    raw_content: str,
    user: Optional[User] = None,
    client_ip: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute complete end-to-end incident detection, analysis, risk scoring,
    and response synthesis pipeline from raw security log input.
    """
    # Ensure MITRE database is seeded
    seed_mitre_database(db)

    # 1. Parse log events
    events = parse_log(raw_content)
    event_count = len(events)
    lines = raw_content.splitlines()
    if raw_content.strip().startswith("{") or raw_content.strip().startswith("["):
        log_format = "json"
    elif lines and "," in lines[0]:
        log_format = "csv"
    else:
        log_format = "syslog_ssh"

    # 2. Persist SecurityLog record
    log_record = SecurityLog(
        filename=filename,
        file_size=len(raw_content.encode("utf-8")),
        log_format=log_format,
        raw_content=raw_content[:50000],  # Store up to 50KB in db
        event_count=event_count,
        uploaded_by_id=user.id if user else None
    )
    db.add(log_record)
    db.flush()

    # 3. Persist normalized security events
    for ev in events[:200]:  # Cap event persistence per log upload to 200
        event_entry = SecurityEvent(
            log_id=log_record.id,
            timestamp=ev.get("timestamp"),
            event_type=ev.get("event_type", "security_event"),
            source_ip=ev.get("source_ip"),
            destination_ip=ev.get("destination_ip"),
            username=ev.get("username"),
            service=ev.get("service"),
            port=ev.get("port"),
            status=ev.get("status"),
            raw_log=ev.get("raw_log")
        )
        db.add(event_entry)

    # 4. Rule-Based Threat Detection Engine
    rule_detection = detect_threats(events)

    # 5. Gemini AI Security Analysis (or graceful fallback)
    ai_analysis = analyze_security_events(events, rule_detection=rule_detection)

    # 6. Deterministic Risk Scoring Engine
    risk_data = calculate_risk_score(ai_analysis, events=events)

    # 7. MITRE ATT&CK Mapping
    mitre_data = map_technique_from_evidence(
        incident_type=ai_analysis.get("incident_type", rule_detection.get("incident_type")),
        events=events,
        gemini_technique=ai_analysis.get("mitre_technique")
    )

    # 8. Incident Response Recommendation Engine
    response_recs = generate_response_recommendations(
        analysis=ai_analysis,
        source_ip=ai_analysis.get("source_ip", rule_detection.get("source_ip")),
        target_service=ai_analysis.get("target_service", rule_detection.get("target_service")),
        target_accounts=ai_analysis.get("target_accounts", rule_detection.get("target_accounts"))
    )

    # 9. Create Incident Entity
    inc_code = _generate_incident_id(db)
    target_accounts_list = ai_analysis.get("target_accounts") or rule_detection.get("target_accounts") or []

    incident = Incident(
        incident_id=inc_code,
        title=f"{ai_analysis.get('incident_type', 'Security Incident')} from {ai_analysis.get('source_ip', 'Unknown')}",
        description=f"Automated threat analysis identified {ai_analysis.get('incident_type')} targeting {ai_analysis.get('target_service', 'service')} with risk score {risk_data['risk_score']}/100.",
        incident_type=ai_analysis.get("incident_type", "Security Incident"),
        severity=ai_analysis.get("severity", "MEDIUM"),
        risk_score=risk_data["risk_score"],
        risk_level=risk_data["risk_level"],
        status=IncidentStatus.OPEN.value,
        source_ip=ai_analysis.get("source_ip", rule_detection.get("source_ip")),
        destination_ip=None,
        target_service=ai_analysis.get("target_service", rule_detection.get("target_service")),
        target_accounts=json.dumps(target_accounts_list),
        failed_attempts=int(ai_analysis.get("failed_attempts") or rule_detection.get("failed_attempts") or 0),
        mitre_technique_id=mitre_data.get("technique_id"),
        confidence=float(ai_analysis.get("confidence", 0.85)),
        ai_status=ai_analysis.get("ai_status", "COMPLETED"),
        ai_explanation=ai_analysis.get("explanation"),
        investigation_steps=json.dumps(ai_analysis.get("investigation_steps", [])),
        log_id=log_record.id,
        assigned_to_id=user.id if user else None
    )
    db.add(incident)
    db.flush()

    # 10. Persist Risk Assessment Entity
    factor_scores = {f["name"]: f["score"] for f in risk_data.get("factors", [])}
    risk_assessment = RiskAssessment(
        incident_id=incident.id,
        base_score=factor_scores.get("Base Severity Weight", 0),
        frequency_score=factor_scores.get("Attack Frequency & Velocity", 0),
        privilege_score=factor_scores.get("Privileged Target Exposure", 0),
        service_score=factor_scores.get("Service Criticality", 0),
        pattern_score=factor_scores.get("Attack Pattern Severity", 0),
        confidence_score=factor_scores.get("Analytical Confidence", 0),
        final_score=risk_data["risk_score"],
        risk_level=risk_data["risk_level"],
        formula=risk_data["formula"],
        summary=risk_data["summary"],
        factors_json=json.dumps(risk_data["factors"])
    )
    db.add(risk_assessment)

    # 11. Persist Recommended Response Actions
    for act in response_recs:
        resp_act = ResponseAction(
            incident_id=incident.id,
            action=act["action"],
            reason=act["reason"],
            priority=act["priority"],
            risk_level=act["risk_level"],
            command_preview=act.get("command_preview"),
            status=ActionStatus.PROPOSED.value,
            requires_approval=True
        )
        db.add(resp_act)

    # 12. Create Initial Timeline Events
    now = datetime.now(timezone.utc)
    db.add(TimelineEvent(
        incident_id=incident.id,
        timestamp=now,
        event_type="DETECTION",
        title="Security Telemetry Ingested & Pattern Flagged",
        description=f"Log file '{filename}' parsed ({event_count} normalized events). Matched threat signature: {incident.incident_type}.",
        source="Log Ingestion Gateway",
        actor="Parser & Rule Engine",
        status_after="OPEN"
    ))

    db.add(TimelineEvent(
        incident_id=incident.id,
        timestamp=now,
        event_type="AI_ANALYSIS",
        title=f"Gemini Security Intelligence Corroboration ({ai_analysis.get('ai_status', 'COMPLETED')})",
        description=f"Classified as {incident.severity} threat with {int(incident.confidence * 100)}% confidence. Assigned MITRE technique {incident.mitre_technique_id or 'T1078'}.",
        source="Google Gemini 3.6 Flash",
        actor="Gemini AI Engine",
        status_after="OPEN"
    ))

    # 13. Create Threat Indicator (IOC) if attacker IP is known
    src_ip = incident.source_ip
    if src_ip and src_ip != "Unknown":
        intel = enrich_indicator(src_ip, "IP")
        db.add(ThreatIndicator(
            incident_id=incident.id,
            indicator_type="IP",
            value=src_ip,
            threat_type=intel.get("threat_classification", "Suspicious Attacker IP"),
            reputation_score=intel.get("reputation_score", 75),
            risk_level=intel.get("risk_level", incident.severity),
            confidence=intel.get("confidence", 0.85),
            source=intel.get("source_provenance", "DEMO_LOCAL_INTEL"),
            country=intel.get("country"),
            asn=intel.get("asn"),
            actor_group=intel.get("actor_group"),
            mitre_technique_id=incident.mitre_technique_id,
            details=f"Origin IP flagged during incident {incident.incident_id}.",
            first_seen=now,
            last_seen=now
        ))

    db.commit()
    db.refresh(incident)

    # 14. Record Forensics Audit Log
    log_audit_event(
        db=db,
        action="LOG_INGESTION_AND_INCIDENT_CREATION",
        entity_type="INCIDENT",
        entity_id=incident.incident_id,
        details={
            "filename": filename,
            "event_count": event_count,
            "incident_type": incident.incident_type,
            "risk_score": incident.risk_score,
            "severity": incident.severity,
            "mitre_technique": incident.mitre_technique_id,
            "ai_status": incident.ai_status
        },
        user=user,
        ip_address=client_ip
    )

    return {
        "log_id": log_record.id,
        "filename": filename,
        "file_size": log_record.file_size,
        "log_format": log_format,
        "event_count": event_count,
        "events": events,
        "incident_id": incident.incident_id,
        "risk_score": incident.risk_score,
        "risk_level": incident.risk_level,
        "ai_status": incident.ai_status,
        "ai_analysis": ai_analysis,
        "risk_analysis": risk_data,
        "mitre_technique": mitre_data,
        "response_actions": response_recs
    }


def get_incidents_paginated(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    incident_type: Optional[str] = None,
    source_ip: Optional[str] = None,
    target_service: Optional[str] = None,
    mitre_technique: Optional[str] = None,
    search: Optional[str] = None
) -> Tuple[List[Incident], int]:
    """Retrieve filtered, paginated incidents."""
    query = db.query(Incident)

    if severity:
        query = query.filter(Incident.severity == severity.upper())
    if status:
        query = query.filter(Incident.status == status.upper())
    if incident_type:
        query = query.filter(Incident.incident_type.ilike(f"%{incident_type}%"))
    if source_ip:
        query = query.filter(Incident.source_ip == source_ip)
    if target_service:
        query = query.filter(Incident.target_service == target_service.lower())
    if mitre_technique:
        query = query.filter(Incident.mitre_technique_id == mitre_technique.upper())
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Incident.incident_id.ilike(pattern)) |
            (Incident.title.ilike(pattern)) |
            (Incident.source_ip.ilike(pattern)) |
            (Incident.incident_type.ilike(pattern))
        )

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(desc(Incident.created_at)).offset(offset).limit(page_size).all()

    return items, total


def get_incident_by_code(db: Session, incident_id: str) -> Optional[Incident]:
    """Look up an incident by code (e.g. 'INC-000001') or numeric ID."""
    if incident_id.isdigit():
        return db.query(Incident).filter(Incident.id == int(incident_id)).first()
    return db.query(Incident).filter(Incident.incident_id == incident_id.upper()).first()


def update_incident_status(
    db: Session,
    incident_id: str,
    new_status: str,
    user: Optional[User] = None,
    notes: Optional[str] = None,
    client_ip: Optional[str] = None
) -> Incident:
    """Transition incident lifecycle status with audit and timeline recording."""
    incident = get_incident_by_code(db, incident_id)
    if not incident:
        raise ValueError(f"Incident {incident_id} not found")

    old_status = incident.status
    incident.status = new_status.upper()
    incident.updated_at = datetime.now(timezone.utc)

    # Determine timeline event type
    evt_type_map = {
        "INVESTIGATING": ("INITIAL_INVESTIGATION", "Analyst Triage Commenced"),
        "CONTAINED": ("CONTAINMENT", "Threat Contained & Host Isolated"),
        "RESOLVED": ("RESOLUTION", "Incident Successfully Remediated"),
        "FALSE_POSITIVE": ("RESOLUTION", "Incident Marked as False Positive"),
    }
    evt_type, evt_title = evt_type_map.get(incident.status, ("STATUS_CHANGE", f"Status updated to {incident.status}"))

    actor_name = user.full_name or user.username if user else "Security Analyst"

    db.add(TimelineEvent(
        incident_id=incident.id,
        timestamp=datetime.now(timezone.utc),
        event_type=evt_type,
        title=evt_title,
        description=notes or f"Incident transitioned from {old_status} to {incident.status}.",
        source="SOC Web UI",
        actor=actor_name,
        status_after=incident.status
    ))

    db.commit()
    db.refresh(incident)

    log_audit_event(
        db=db,
        action="INCIDENT_STATUS_CHANGE",
        entity_type="INCIDENT",
        entity_id=incident.incident_id,
        details={
            "old_status": old_status,
            "new_status": incident.status,
            "notes": notes
        },
        user=user,
        ip_address=client_ip
    )

    return incident


def add_incident_note(
    db: Session,
    incident_id: str,
    note_text: str,
    user: Optional[User] = None,
    client_ip: Optional[str] = None
) -> Incident:
    """Appends an analyst note to the incident and logs a timeline event."""
    incident = get_incident_by_code(db, incident_id)
    if not incident:
        raise ValueError(f"Incident {incident_id} not found")

    actor_name = user.full_name or user.username if user else "Security Analyst"
    timestamp_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    formatted_note = f"[{timestamp_str}] {actor_name}:\n{note_text.strip()}"
    if incident.analyst_notes:
        incident.analyst_notes = f"{incident.analyst_notes}\n\n{formatted_note}"
    else:
        incident.analyst_notes = formatted_note

    incident.updated_at = datetime.now(timezone.utc)

    # Add timeline event
    db.add(TimelineEvent(
        incident_id=incident.id,
        timestamp=datetime.now(timezone.utc),
        event_type="NOTE_ADDED",
        title="Analyst Investigation Note Recorded",
        description=note_text.strip(),
        source="SOC Web UI",
        actor=actor_name,
        status_after=incident.status
    ))

    db.commit()
    db.refresh(incident)

    log_audit_event(
        db=db,
        action="INCIDENT_NOTE_ADDED",
        entity_type="INCIDENT",
        entity_id=incident.incident_id,
        details={"note_snippet": note_text[:100]},
        user=user,
        ip_address=client_ip
    )

    return incident


def update_response_action_status(
    db: Session,
    action_id: int,
    new_status: str,
    user: Optional[User] = None,
    client_ip: Optional[str] = None
) -> ResponseAction:
    """Approve or update a response action status with timeline tracking."""
    action = db.query(ResponseAction).filter(ResponseAction.id == action_id).first()
    if not action:
        raise ValueError(f"Response action ID {action_id} not found")

    old_status = action.status
    action.status = new_status.upper()

    if action.status == ActionStatus.APPROVED.value:
        action.approved_by_id = user.id if user else None
        action.approved_at = datetime.now(timezone.utc)
    elif action.status == ActionStatus.EXECUTED.value:
        action.executed_at = datetime.now(timezone.utc)

    actor_name = user.full_name or user.username if user else "Security Analyst"

    # Add timeline event for the incident
    db.add(TimelineEvent(
        incident_id=action.incident_id,
        timestamp=datetime.now(timezone.utc),
        event_type="CONTAINMENT",
        title=f"Response Action {action.status}: {action.action}",
        description=f"Analyst {actor_name} marked response action '{action.action}' as {action.status}.",
        source="SOC Response Engine",
        actor=actor_name,
        status_after=None
    ))

    db.commit()
    db.refresh(action)

    log_audit_event(
        db=db,
        action="RESPONSE_ACTION_STATUS_CHANGE",
        entity_type="RESPONSE_ACTION",
        entity_id=str(action.id),
        details={
            "action_title": action.action,
            "old_status": old_status,
            "new_status": action.status
        },
        user=user,
        ip_address=client_ip
    )

    return action
