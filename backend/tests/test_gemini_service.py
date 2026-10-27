"""
Tests for SentinelAI-X Gemini AI Integration & Fallback Handling
"""

import json
from unittest.mock import MagicMock, patch
from services.gemini_service import analyze_security_events, _create_fallback_response


def test_gemini_fallback_on_client_none():
    with patch("services.gemini_service.get_gemini_client", return_value=None):
        events = [{"event_type": "failed_login", "username": "root", "source_ip": "1.2.3.4", "service": "ssh"}]
        result = analyze_security_events(events)
        assert result["ai_status"] == "FALLBACK"
        assert result["incident_type"] == "Authentication Failure"
        assert len(result["recommended_actions"]) > 0


def test_gemini_mocked_success(monkeypatch):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_payload = {
        "incident_type": "Brute Force Attack",
        "severity": "HIGH",
        "source_ip": "192.168.1.15",
        "target_service": "ssh",
        "target_accounts": ["admin", "root"],
        "failed_attempts": 4,
        "mitre_technique": "T1110",
        "confidence": 0.95,
        "explanation": "Observed multiple authentication failures.",
        "recommended_actions": ["Block source IP", "Disable root login"],
        "investigation_steps": ["Inspect auth logs"]
    }
    mock_response.text = json.dumps(mock_payload)
    mock_client.models.generate_content.return_value = mock_response

    monkeypatch.setattr("services.gemini_service.get_gemini_client", lambda: mock_client)

    events = [{"event_type": "failed_login", "username": "admin", "source_ip": "192.168.1.15", "service": "ssh"}]
    res = analyze_security_events(events)
    assert res["ai_status"] == "COMPLETED"
    assert res["incident_type"] == "Brute Force Attack"
    assert res["confidence"] == 0.95


def test_gemini_malformed_json_fallback(monkeypatch):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This is not JSON text at all!"
    mock_client.models.generate_content.return_value = mock_response

    monkeypatch.setattr("services.gemini_service.get_gemini_client", lambda: mock_client)

    events = [{"event_type": "failed_login", "username": "admin", "source_ip": "192.168.1.15", "service": "ssh"}]
    res = analyze_security_events(events)
    assert res["ai_status"] == "FALLBACK"
    assert "Gemini" in res["explanation"]
