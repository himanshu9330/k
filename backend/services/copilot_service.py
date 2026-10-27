"""
SentinelAI-X AI Copilot Service
================================
Context-aware SOC investigation assistant grounded in live incident telemetry,
MITRE ATT&CK knowledge, and explainable risk factors.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.config import settings
from services.gemini_service import get_gemini_client
from models.incident import Incident

logger = logging.getLogger("sentinelai.copilot")


COPILOT_SUGGESTIONS = [
    {
        "id": "sug-why-critical",
        "category": "Risk & Severity",
        "prompt": "Why is this incident classified with this severity and risk score?",
        "description": "Explains the multi-factor mathematical risk calculation and weighting."
    },
    {
        "id": "sug-evidence",
        "category": "Forensics",
        "prompt": "What forensic evidence directly proves this attack occurred?",
        "description": "Lists corroborated telemetry events, usernames, and origin IPs."
    },
    {
        "id": "sug-mitre-defense",
        "category": "MITRE ATT&CK",
        "prompt": "Explain the mapped MITRE ATT&CK technique and recommended mitigations.",
        "description": "Breaks down the adversary technique, tactic, and defensive countermeasures."
    },
    {
        "id": "sug-containment",
        "category": "Response",
        "prompt": "Generate a step-by-step containment and recovery plan for this incident.",
        "description": "Produces actionable CLI commands, firewall rules, and account lock actions."
    },
    {
        "id": "sug-executive-summary",
        "category": "Reporting",
        "prompt": "Draft a concise CISO executive briefing summarizing this incident.",
        "description": "Generates a professional executive summary for leadership."
    }
]


def get_copilot_suggestions() -> List[Dict[str, Any]]:
    return COPILOT_SUGGESTIONS


def process_copilot_query(
    message: str,
    incident_id: Optional[str] = None,
    chat_history: Optional[List[Dict[str, str]]] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Processes an investigation question using Google Gemini with incident context grounding.
    """
    incident_context = {}
    incident_obj = None

    if incident_id and db:
        incident_obj = db.query(Incident).filter(Incident.incident_id == incident_id).first()
        if incident_obj:
            incident_context = {
                "incident_id": incident_obj.incident_id,
                "title": incident_obj.title,
                "type": incident_obj.incident_type,
                "severity": incident_obj.severity,
                "risk_score": incident_obj.risk_score,
                "risk_level": incident_obj.risk_level,
                "status": incident_obj.status,
                "source_ip": incident_obj.source_ip,
                "target_service": incident_obj.target_service,
                "target_accounts": json.loads(incident_obj.target_accounts) if incident_obj.target_accounts else [],
                "failed_attempts": incident_obj.failed_attempts,
                "mitre_technique": incident_obj.mitre_technique_id,
                "confidence": incident_obj.confidence,
                "ai_explanation": incident_obj.ai_explanation,
                "analyst_notes": incident_obj.analyst_notes,
                "response_actions": [
                    {"action": a.action, "priority": a.priority, "status": a.status, "command": a.command_preview}
                    for a in incident_obj.response_actions
                ],
                "evidence_events": [
                    {"type": e.event_type, "user": e.username, "ip": e.source_ip, "raw": e.raw_log}
                    for e in (incident_obj.log.events if incident_obj.log else [])
                ]
            }

    client = get_gemini_client()
    if not client:
        return _copilot_fallback_response(message, incident_obj, incident_context)

    # Build prompt
    history_str = ""
    if chat_history:
        for turn in chat_history[-4:]:  # last 4 turns
            role = "Analyst" if turn.get("role") == "user" else "Copilot"
            history_str += f"{role}: {turn.get('content', '')}\n"

    incident_ctx_str = json.dumps(incident_context, indent=2, default=str) if incident_context else "No specific incident selected. General SOC assistant mode."

    system_prompt = f"""
You are SentinelAI-X Copilot, an expert AI cybersecurity investigation assistant for Security Operations Center (SOC) analysts.

Your mission: Provide precise, professional, evidence-based answers to help analysts investigate threats, understand risk scores, review MITRE techniques, and execute response playbooks.

======================================================================
RULES OF ENGAGEMENT:
======================================================================
1. Ground your answers strictly in the supplied incident telemetry when available.
2. If evidence is missing, state it clearly rather than inventing details.
3. Provide practical, actionable guidance (CLI command templates, firewall iptables, log analysis steps).
4. Maintain a professional, authoritative, yet approachable cybersecurity tone.

======================================================================
INCIDENT CONTEXT:
======================================================================
{incident_ctx_str}

======================================================================
RECENT CONVERSATION HISTORY:
======================================================================
{history_str}

======================================================================
ANALYST QUERY:
======================================================================
{message}
"""

    model_name = settings.GEMINI_MODEL or "gemini-2.5-flash"

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=system_prompt,
        )
        reply_text = response.text.strip()

        followups = [
            "What additional telemetry should I collect?",
            "What are the containment priorities?",
            "How do I prevent recurrence of this attack?"
        ]
        if incident_context:
            followups = [
                f"Show mitigation commands for {incident_context.get('mitre_technique', 'T1110')}",
                f"How should we isolate source IP {incident_context.get('source_ip', 'the attacker')}?",
                "Draft an executive report for this incident"
            ]

        return {
            "reply": reply_text,
            "incident_id": incident_id,
            "suggested_followups": followups,
            "referenced_evidence": [f"Source IP: {incident_context.get('source_ip')}", f"Target Accounts: {incident_context.get('target_accounts')}"] if incident_context else [],
            "mitre_references": [incident_context.get("mitre_technique")] if incident_context.get("mitre_technique") else ["T1110"],
            "copilot_mode": "CONTEXT_AWARE" if incident_context else "GENERAL_SOC"
        }

    except Exception as e:
        logger.error(f"Copilot Gemini error: {e}")
        return _copilot_fallback_response(message, incident_obj, incident_context)


def _copilot_fallback_response(message: str, incident_obj: Any, ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Provides a helpful deterministic assistant reply when the Gemini API is offline."""
    if ctx:
        reply = (
            f"**SentinelAI-X Copilot (Deterministic Knowledge Mode)**\n\n"
            f"**Incident Summary ({ctx.get('incident_id')} - {ctx.get('title')}):**\n"
            f"- **Threat Type:** {ctx.get('type')}\n"
            f"- **Severity / Risk Score:** {ctx.get('severity')} ({ctx.get('risk_score')}/100 - {ctx.get('risk_level')})\n"
            f"- **Attacker Source IP:** `{ctx.get('source_ip')}`\n"
            f"- **Target Service:** `{ctx.get('target_service')}`\n"
            f"- **MITRE ATT&CK:** `{ctx.get('mitre_technique')}`\n\n"
            f"**Recommended Immediate Investigation Steps:**\n"
            f"1. Query firewall logs to verify whether `{ctx.get('source_ip')}` has established persistent outbound connections.\n"
            f"2. Force credential rotation for targeted account(s): {', '.join(ctx.get('target_accounts', [])) or 'All affected users'}.\n"
            f"3. Review host SSH/Auth logs for accepted logins following the failed velocity bursts.\n"
            f"4. Authorize proposed containment actions on the Incident Deep-Dive page.\n\n"
            f"*(Note: Gemini live conversational API is offline; displaying contextual telemetry from rule engine.)*"
        )
    else:
        reply = (
            "**SentinelAI-X Copilot (SOC Knowledge Mode)**\n\n"
            "I can assist you with:\n"
            "- **Threat Analysis:** Understanding attack patterns (Brute Force, Password Spray, Port Scans, Web SQLi).\n"
            "- **Risk Scoring:** Explaining the 6-factor deterministic risk equation ($0-100$).\n"
            "- **MITRE ATT&CK:** Reviewing tactics, techniques, and mitigations.\n"
            "- **Incident Response:** Generating containment CLI commands and investigation playbooks.\n\n"
            "Select an active incident from the dropdown or ask any cybersecurity investigation question!"
        )

    return {
        "reply": reply,
        "incident_id": ctx.get("incident_id") if ctx else None,
        "suggested_followups": [
            "Why is this incident critical?",
            "What evidence supports this classification?",
            "Show me response command templates"
        ],
        "referenced_evidence": [f"Source IP: {ctx.get('source_ip')}"] if ctx else [],
        "mitre_references": [ctx.get("mitre_technique")] if ctx and ctx.get("mitre_technique") else ["T1110"],
        "copilot_mode": "FALLBACK"
    }
