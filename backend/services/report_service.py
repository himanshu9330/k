"""
SentinelAI-X Incident Reporting Service
=======================================
Generates and persists formal CISO Executive Briefings, Technical Incident
Forensic Reports, and Compliance Audit Reports.
"""

import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from models.incident import Incident
from models.report import Report


def generate_incident_report(
    incident_id_str: str,
    report_type: str = "EXECUTIVE_BRIEFING",
    custom_notes: Optional[str] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Generates a structured incident report.
    If database session is provided, persists the generated report into the 'reports' table.
    """
    incident = None
    if db:
        incident = db.query(Incident).filter(Incident.incident_id == incident_id_str).first()

    if not incident:
        # Generate generic fallback structure
        return {
            "report_id": f"REP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "title": f"Incident Briefing: {incident_id_str}",
            "report_type": report_type,
            "classification": "RESTRICTED / SOC INTERNAL",
            "executive_summary": f"Security incident {incident_id_str} recorded in SentinelAI-X telemetry.",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    # Extract accounts and actions
    accounts = json.loads(incident.target_accounts) if incident.target_accounts else []
    actions = [
        {"action": a.action, "reason": a.reason, "priority": a.priority, "status": a.status}
        for a in incident.response_actions
    ]

    report_id = f"REP-{incident.incident_id.replace('INC-', '')}-{datetime.now(timezone.utc).strftime('%m%d%H%M')}"
    title = f"CISO Executive Incident Briefing: {incident.title} ({incident.incident_id})"
    
    exec_summary = (
        f"On {incident.created_at.strftime('%B %d, %Y at %H:%M UTC')}, the SentinelAI-X automated SOC detection "
        f"engine identified a {incident.severity} severity security incident ({incident.incident_type}) "
        f"originating from source IP {incident.source_ip or 'an unknown origin'}. The attack targeted the "
        f"{incident.target_service.upper() if incident.target_service else 'infrastructure'} service with "
        f"{incident.failed_attempts} observed adversarial attempts. Multi-factor mathematical risk scoring "
        f"rated this event at {incident.risk_score} / 100 ({incident.risk_level} RISK). "
        f"The incident has been mapped to MITRE ATT&CK technique {incident.mitre_technique_id or 'T1078'}."
    )

    threat_summary = (
        f"Adversary Telemetry Profile:\n"
        f"- Source Origin: {incident.source_ip or 'Unresolved'}\n"
        f"- Target Service: {incident.target_service or 'General Protocol'}\n"
        f"- Affected Accounts: {', '.join(accounts) if accounts else 'None identified'}\n"
        f"- Failed Volume: {incident.failed_attempts} attempts\n"
        f"- Detection Confidence: {int(incident.confidence * 100)}%"
    )

    mitre_analysis = (
        f"Technique ID: {incident.mitre_technique_id or 'T1078'}\n"
        f"Technique Name: {incident.mitre_technique.name if incident.mitre_technique else 'Generic Access Technique'}\n"
        f"Tactic: {incident.mitre_technique.tactic if incident.mitre_technique else 'Credential Access'}\n"
        f"Defense Strategy: {incident.mitre_technique.mitigation if incident.mitre_technique else 'Apply rate limiting and MFA.'}"
    )

    resolution_text = (
        f"Incident status is currently {incident.status}. "
        f"{len([a for a in incident.response_actions if a.status == 'APPROVED'])} containment actions approved."
    )

    # Persist report if db provided
    if db:
        new_report = Report(
            report_id=report_id,
            incident_id=incident.id,
            report_type=report_type,
            title=title,
            classification="RESTRICTED / SOC INTERNAL",
            executive_summary=exec_summary,
            threat_summary=threat_summary,
            mitre_analysis=mitre_analysis,
            recommended_actions=json.dumps(actions),
            analyst_notes=custom_notes or incident.analyst_notes,
            resolution=resolution_text,
            generated_by="SentinelAI-X Autonomous Engine"
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

    return {
        "report_id": report_id,
        "title": title,
        "classification": "RESTRICTED / SOC INTERNAL",
        "report_type": report_type,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "incident_metadata": {
            "incident_id": incident.incident_id,
            "title": incident.title,
            "incident_type": incident.incident_type,
            "severity": incident.severity,
            "risk_score": incident.risk_score,
            "risk_level": incident.risk_level,
            "status": incident.status,
            "source_ip": incident.source_ip,
            "target_service": incident.target_service,
            "target_accounts": accounts,
            "failed_attempts": incident.failed_attempts,
            "created_at": incident.created_at.isoformat(),
        },
        "executive_summary": exec_summary,
        "threat_summary": threat_summary,
        "mitre_attack": {
            "technique_id": incident.mitre_technique_id or "T1078",
            "name": incident.mitre_technique.name if incident.mitre_technique else "Brute Force",
            "tactic": incident.mitre_technique.tactic if incident.mitre_technique else "Credential Access",
            "mitigation": incident.mitre_technique.mitigation if incident.mitre_technique else "Enforce MFA and IP rate limits.",
        },
        "ai_explanation": incident.ai_explanation or "Deterministic rule correlation verified security anomaly.",
        "recommended_response_actions": actions,
        "analyst_notes": custom_notes or incident.analyst_notes or "No additional analyst remarks recorded.",
        "resolution": resolution_text,
    }
