"""
Tests for End-to-End Incident Pipeline & REST Endpoints
"""

import io


def test_end_to_end_log_upload_and_incident(client, monkeypatch):
    # Ensure offline deterministic execution for unit test
    monkeypatch.setattr("services.gemini_service.get_gemini_client", lambda: None)
    monkeypatch.setattr("services.copilot_service.get_gemini_client", lambda: None)

    log_content = (
        "Aug 11 10:30:21 server sshd: Failed password for admin from 192.168.1.15\n"
        "Aug 11 10:30:25 server sshd: Failed password for admin from 192.168.1.15\n"
        "Aug 11 10:30:29 server sshd: Failed password for admin from 192.168.1.15\n"
        "Aug 11 10:35:41 server sshd: Failed password for root from 192.168.1.15\n"
    )

    file_obj = io.BytesIO(log_content.encode("utf-8"))
    response = client.post(
        "/api/logs/upload",
        files={"file": ("test_security.log", file_obj, "text/plain")}
    )

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    data = res_data["data"]
    assert data["event_count"] == 4
    assert data["incident_id"] is not None
    incident_id = data["incident_id"]

    # Retrieve incident details
    detail_res = client.get(f"/api/incidents/{incident_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()["data"]
    assert detail["incident_id"] == incident_id
    assert detail["status"] == "OPEN"
    assert detail["risk_score"] > 50
    assert detail["mitre_technique"] is not None
    assert len(detail["response_actions"]) > 0
    assert len(detail["timeline_events"]) >= 2
    assert len(detail["threat_indicators"]) >= 1

    # Update incident status
    patch_res = client.patch(
        f"/api/incidents/{incident_id}/status",
        json={"status": "INVESTIGATING", "notes": "Analyst triage started"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["status"] == "INVESTIGATING"

    # Add analyst note
    note_res = client.post(
        f"/api/incidents/{incident_id}/notes",
        json={"note": "Verified source IP on perimeter edge firewall."}
    )
    assert note_res.status_code == 200
    assert "Verified source IP" in note_res.json()["data"]["analyst_notes"]

    # Approve first response action
    action_id = detail["response_actions"][0]["id"]
    action_res = client.post(
        f"/api/incidents/{incident_id}/response-actions/{action_id}/status",
        json={"status": "APPROVED"}
    )
    assert action_res.status_code == 200
    assert action_res.json()["data"]["status"] == "APPROVED"

    # Generate Report
    report_res = client.get(f"/api/incidents/{incident_id}/report")
    assert report_res.status_code == 200
    report = report_res.json()["data"]
    assert "report_id" in report
    assert "executive_summary" in report

    # Test Threat Intelligence Lookup
    threat_res = client.post(
        "/api/threats/lookup",
        json={"indicator": "192.168.1.15", "indicator_type": "IP"}
    )
    assert threat_res.status_code == 200
    assert threat_res.json()["data"]["indicator"] == "192.168.1.15"

    # Test Copilot Suggestions & Chat
    sug_res = client.get("/api/copilot/suggestions")
    assert sug_res.status_code == 200
    assert len(sug_res.json()["data"]) > 0

    chat_res = client.post(
        "/api/copilot/chat",
        json={"message": "What is the recommended containment strategy?", "incident_id": incident_id}
    )
    assert chat_res.status_code == 200
    assert "reply" in chat_res.json()["data"]
