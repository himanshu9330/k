"""
Tests for SentinelAI-X Deterministic Risk Scoring Engine
"""

from services.risk_service import calculate_risk_score


def test_risk_score_critical():
    analysis = {
        "incident_type": "Brute Force Attack",
        "severity": "HIGH",
        "source_ip": "192.168.1.15",
        "target_service": "ssh",
        "target_accounts": ["admin", "root"],
        "failed_attempts": 10,
        "mitre_technique": "T1110",
        "confidence": 0.95
    }
    res = calculate_risk_score(analysis)
    assert res["risk_score"] >= 80
    assert res["risk_level"] == "CRITICAL"
    assert len(res["factors"]) == 6
    assert "Base Severity Weight" in [f["name"] for f in res["factors"]]


def test_risk_score_low():
    analysis = {
        "incident_type": "Normal Telemetry",
        "severity": "LOW",
        "source_ip": "10.0.0.5",
        "target_service": "http",
        "target_accounts": ["user1"],
        "failed_attempts": 0,
        "mitre_technique": "T1078",
        "confidence": 0.50
    }
    res = calculate_risk_score(analysis)
    assert res["risk_score"] < 30
    assert res["risk_level"] == "LOW"


def test_risk_score_bounds():
    # Extreme scenario should not exceed 100
    extreme_analysis = {
        "incident_type": "Critical Root Exploitation Brute Force",
        "severity": "CRITICAL",
        "source_ip": "1.2.3.4",
        "target_service": "ssh",
        "target_accounts": ["root", "admin", "administrator"],
        "failed_attempts": 500,
        "mitre_technique": "T1110",
        "confidence": 1.0
    }
    res = calculate_risk_score(extreme_analysis)
    assert res["risk_score"] == 100
    assert res["risk_level"] == "CRITICAL"
