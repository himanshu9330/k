"""
Tests for SentinelAI-X Deterministic Rule-Based Detection Engine
"""

from services.detection_service import detect_threats


def test_detect_brute_force():
    events = [
        {"event_type": "failed_login", "username": "admin", "source_ip": "192.168.1.15", "service": "ssh", "status": "failed"},
        {"event_type": "failed_login", "username": "admin", "source_ip": "192.168.1.15", "service": "ssh", "status": "failed"},
        {"event_type": "failed_login", "username": "admin", "source_ip": "192.168.1.15", "service": "ssh", "status": "failed"},
        {"event_type": "failed_login", "username": "root", "source_ip": "192.168.1.15", "service": "ssh", "status": "failed"},
    ]
    res = detect_threats(events)
    assert res["incident_type"] == "Brute Force Attack"
    assert res["severity"] == "HIGH"
    assert res["source_ip"] == "192.168.1.15"
    assert res["failed_attempts"] == 4
    assert "admin" in res["target_accounts"]
    assert "root" in res["target_accounts"]
    assert res["mitre_technique"] == "T1110"


def test_detect_password_spray():
    events = [
        {"event_type": "failed_login", "username": "user1", "source_ip": "203.0.113.88", "service": "ssh", "status": "failed"},
        {"event_type": "failed_login", "username": "user2", "source_ip": "203.0.113.88", "service": "ssh", "status": "failed"},
        {"event_type": "failed_login", "username": "user3", "source_ip": "203.0.113.88", "service": "ssh", "status": "failed"},
    ]
    res = detect_threats(events)
    assert res["incident_type"] == "Password Spray Attack"
    assert res["severity"] == "HIGH"
    assert len(res["target_accounts"]) == 3
    assert res["mitre_technique"] == "T1110.003"


def test_detect_privilege_escalation():
    events = [
        {
            "event_type": "privileged_command_execution",
            "username": "tester",
            "service": "sudo",
            "status": "executed",
            "raw_log": "sudo: tester : COMMAND=/bin/cat /etc/shadow"
        }
    ]
    res = detect_threats(events)
    assert res["incident_type"] == "Suspicious Privilege Escalation / Command Execution"
    assert res["severity"] == "CRITICAL"
    assert res["mitre_technique"] == "T1059"


def test_detect_port_scan():
    events = [
        {"event_type": "connection_attempt", "source_ip": "10.0.0.99", "port": 21, "status": "failed"},
        {"event_type": "connection_attempt", "source_ip": "10.0.0.99", "port": 22, "status": "failed"},
        {"event_type": "connection_attempt", "source_ip": "10.0.0.99", "port": 80, "status": "failed"},
        {"event_type": "connection_attempt", "source_ip": "10.0.0.99", "port": 443, "status": "failed"},
    ]
    res = detect_threats(events)
    assert res["incident_type"] == "Network Service Discovery / Port Scan"
    assert res["mitre_technique"] == "T1046"
