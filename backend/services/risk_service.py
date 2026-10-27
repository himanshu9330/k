"""
SentinelAI-X Deterministic Risk Scoring Engine
================================================
Calculates a reproducible, mathematical cybersecurity risk score (0-100)
based on multi-factor telemetry:

1. Base Severity Weight (0-50 pts)
2. Attack Frequency / Volume Factor (0-25 pts)
3. Privileged Account Targeting Factor (0-15 pts)
4. Sensitive / Critical Service Factor (0-10 pts)
5. Attack Technique / Pattern Factor (0-10 pts)
6. Confidence Weighting Adjustment (0-5 pts)

Score Range & Classifications:
  0  - 29  : LOW
  30 - 59  : MEDIUM
  60 - 79  : HIGH
  80 - 100 : CRITICAL
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class RiskFactorBreakdown(BaseModel):
    name: str
    score: int
    max_score: int
    description: str
    evidence: Optional[str] = None


class RiskAssessmentResult(BaseModel):
    risk_score: int = Field(ge=0, le=100, description="Overall risk score (0-100)")
    risk_level: str = Field(description="Qualitative severity: LOW, MEDIUM, HIGH, CRITICAL")
    factors: List[RiskFactorBreakdown] = Field(default_factory=list)
    formula: str = Field(description="Mathematical explanation of score calculation")
    summary: str = Field(description="Concise analytical risk summary")


# Canonical lists of sensitive indicators
PRIVILEGED_ACCOUNTS = {
    "root",
    "admin",
    "administrator",
    "system",
    "superuser",
    "daemon",
    "bin",
    "sys",
    "operator",
    "dbadmin",
    "sa",
    "postgres",
    "oracle",
    "master"
}

SENSITIVE_SERVICES = {
    "ssh": 10,
    "rdp": 10,
    "telnet": 10,
    "vnc": 10,
    "smb": 10,
    "database": 10,
    "mysql": 10,
    "postgresql": 10,
    "oracle": 10,
    "mssql": 10,
    "redis": 8,
    "mongodb": 8,
    "ftp": 8,
    "ldap": 8,
    "kerberos": 8,
    "http": 5,
    "https": 5
}

SEVERITY_BASE_SCORES = {
    "LOW": 10,
    "MEDIUM": 25,
    "HIGH": 40,
    "CRITICAL": 50
}


def calculate_risk_score(
    analysis: Dict[str, Any],
    events: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Calculate a deterministic risk score and return complete factor breakdown.

    Args:
        analysis: Dictionary containing incident analysis (from Gemini or Rule Engine).
        events: Optional list of raw/normalized security events.

    Returns:
        Dict matching RiskAssessmentResult schema.
    """
    factors: List[RiskFactorBreakdown] = []
    raw_total = 0

    # -------------------------------------------------------------------------
    # 1. Base Severity Score (Max: 50 pts)
    # -------------------------------------------------------------------------
    severity = str(analysis.get("severity", "LOW")).strip().upper()
    base_score = SEVERITY_BASE_SCORES.get(severity, 10)
    raw_total += base_score
    factors.append(RiskFactorBreakdown(
        name="Base Severity Weight",
        score=base_score,
        max_score=50,
        description=f"Assigned based on initial threat severity assessment: {severity}",
        evidence=f"Severity classification: {severity}"
    ))

    # -------------------------------------------------------------------------
    # 2. Attack Frequency / Volume Factor (Max: 25 pts)
    # -------------------------------------------------------------------------
    failed_attempts = analysis.get("failed_attempts") or 0
    if not isinstance(failed_attempts, int):
        try:
            failed_attempts = int(failed_attempts)
        except (ValueError, TypeError):
            failed_attempts = 0

    # Fallback to count in events if available
    if failed_attempts == 0 and events:
        failed_attempts = sum(1 for e in events if e.get("event_type") in ("failed_login", "authentication_failure"))

    frequency_score = 0
    freq_desc = "No repeated authentication failures detected"
    if failed_attempts >= 10:
        frequency_score = 25
        freq_desc = f"Heavy velocity: {failed_attempts} failed attempts detected"
    elif failed_attempts >= 5:
        frequency_score = 20
        freq_desc = f"High velocity: {failed_attempts} failed attempts detected"
    elif failed_attempts >= 3:
        frequency_score = 15
        freq_desc = f"Moderate velocity: {failed_attempts} failed attempts detected"
    elif failed_attempts >= 1:
        frequency_score = 5
        freq_desc = f"Single or low failed attempts ({failed_attempts})"

    raw_total += frequency_score
    factors.append(RiskFactorBreakdown(
        name="Attack Frequency & Velocity",
        score=frequency_score,
        max_score=25,
        description=freq_desc,
        evidence=f"Failed attempts count = {failed_attempts}"
    ))

    # -------------------------------------------------------------------------
    # 3. Privileged Account Targeting Factor (Max: 15 pts)
    # -------------------------------------------------------------------------
    target_accounts = analysis.get("target_accounts") or []
    if isinstance(target_accounts, str):
        target_accounts = [target_accounts]

    matched_privileged = [
        acc for acc in target_accounts
        if str(acc).lower() in PRIVILEGED_ACCOUNTS
    ]

    privilege_score = 15 if matched_privileged else 0
    raw_total += privilege_score
    factors.append(RiskFactorBreakdown(
        name="Privileged Target Exposure",
        score=privilege_score,
        max_score=15,
        description=(
            f"Targeted high-privilege account(s): {', '.join(matched_privileged)}"
            if matched_privileged else "Standard/non-privileged account target"
        ),
        evidence=f"Target accounts: {', '.join(str(a) for a in target_accounts) if target_accounts else 'None'}"
    ))

    # -------------------------------------------------------------------------
    # 4. Sensitive Service Exposure (Max: 10 pts)
    # -------------------------------------------------------------------------
    target_service = str(analysis.get("target_service", "")).strip().lower()
    service_score = SENSITIVE_SERVICES.get(target_service, 0)
    # If not exact match, check substring
    if service_score == 0 and target_service:
        for s_name, s_val in SENSITIVE_SERVICES.items():
            if s_name in target_service:
                service_score = s_val
                break

    raw_total += service_score
    factors.append(RiskFactorBreakdown(
        name="Service Criticality",
        score=service_score,
        max_score=10,
        description=(
            f"Targeted critical remote or data access service: {target_service.upper()}"
            if service_score > 0 else f"Standard service profile ({target_service or 'general'})"
        ),
        evidence=f"Target service: {target_service or 'unspecified'}"
    ))

    # -------------------------------------------------------------------------
    # 5. Attack Pattern / Technique Multiplier (Max: 10 pts)
    # -------------------------------------------------------------------------
    incident_type = str(analysis.get("incident_type", "")).lower()
    mitre_tech = str(analysis.get("mitre_technique", "")).upper()
    pattern_score = 0
    matched_patterns = []

    if any(k in incident_type for k in ["brute", "password", "spray", "credential", "dictionary"]):
        pattern_score = max(pattern_score, 10)
        matched_patterns.append("Credential Access / Brute Force")
    if any(k in incident_type for k in ["scan", "enumeration", "discovery", "recon"]):
        pattern_score = max(pattern_score, 8)
        matched_patterns.append("Reconnaissance / Port Scanning")
    if any(k in incident_type for k in ["privilege", "escalation", "root", "sudo", "injection"]):
        pattern_score = max(pattern_score, 10)
        matched_patterns.append("Privilege Escalation / Exploitation")
    if mitre_tech and mitre_tech != "UNKNOWN":
        pattern_score = max(pattern_score, 8)
        matched_patterns.append(f"Mapped MITRE Technique ({mitre_tech})")

    raw_total += pattern_score
    factors.append(RiskFactorBreakdown(
        name="Attack Pattern Severity",
        score=pattern_score,
        max_score=10,
        description=(
            f"Recognized persistent threat vector: {', '.join(matched_patterns)}"
            if matched_patterns else "Standard or unclassified event stream"
        ),
        evidence=f"Incident Type: {analysis.get('incident_type', 'N/A')}, MITRE: {mitre_tech or 'N/A'}"
    ))

    # -------------------------------------------------------------------------
    # 6. Detection Confidence Factor (Max: 5 pts)
    # -------------------------------------------------------------------------
    confidence = analysis.get("confidence", 0.0)
    try:
        conf_val = float(confidence)
    except (ValueError, TypeError):
        conf_val = 0.0

    confidence_score = 5 if conf_val >= 0.85 else (3 if conf_val >= 0.6 else 0)
    raw_total += confidence_score
    factors.append(RiskFactorBreakdown(
        name="Analytical Confidence",
        score=confidence_score,
        max_score=5,
        description=f"Confidence factor based on corroborating telemetry ({int(conf_val * 100)}%)",
        evidence=f"Confidence score: {conf_val:.2f}"
    ))

    # -------------------------------------------------------------------------
    # Bounded Normalization (0 - 100)
    # -------------------------------------------------------------------------
    final_score = min(max(raw_total, 0), 100)

    # Determine qualitative risk level
    if final_score >= 80:
        risk_level = "CRITICAL"
    elif final_score >= 60:
        risk_level = "HIGH"
    elif final_score >= 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    formula_str = (
        f"Score = min(100, Base({base_score}) + Frequency({frequency_score}) + "
        f"Privilege({privilege_score}) + Service({service_score}) + "
        f"Pattern({pattern_score}) + Confidence({confidence_score})) = {final_score}"
    )

    summary_str = (
        f"Risk Score {final_score}/100 ({risk_level}). "
        f"{'Targeting privileged account(s). ' if matched_privileged else ''}"
        f"Service: {target_service or 'unspecified'}. "
        f"Detected {failed_attempts} failed attempts with {int(conf_val * 100)}% analytical confidence."
    )

    return {
        "risk_score": final_score,
        "risk_level": risk_level,
        "factors": [f.model_dump() for f in factors],
        "formula": formula_str,
        "summary": summary_str
    }
