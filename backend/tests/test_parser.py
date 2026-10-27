"""
Tests for SentinelAI-X Multi-Format Log Parser
"""

from services.parser_service import parse_log


def test_parse_ssh_failed_password():
    log_text = "Aug 11 10:30:21 server sshd[1234]: Failed password for admin from 192.168.1.15 port 2222 ssh2"
    events = parse_log(log_text)
    assert len(events) == 1
    ev = events[0]
    assert ev["event_type"] == "failed_login"
    assert ev["username"] == "admin"
    assert ev["source_ip"] == "192.168.1.15"
    assert ev["service"] == "ssh"
    assert ev["port"] == 2222
    assert ev["status"] == "failed"


def test_parse_ssh_accepted_login():
    log_text = "Aug 11 10:31:02 server sshd[1235]: Accepted password for user1 from 10.0.0.25 port 45123 ssh2"
    events = parse_log(log_text)
    assert len(events) == 1
    ev = events[0]
    assert ev["event_type"] == "successful_login"
    assert ev["username"] == "user1"
    assert ev["source_ip"] == "10.0.0.25"
    assert ev["status"] == "accepted"


def test_parse_sudo_command():
    log_text = "Aug 12 16:20:11 node sudo: tester : TTY=pts/2 ; PWD=/tmp ; USER=root ; COMMAND=/bin/cat /etc/shadow"
    events = parse_log(log_text)
    assert len(events) == 1
    ev = events[0]
    assert ev["event_type"] == "privileged_command_execution"
    assert ev["username"] == "tester"
    assert ev["service"] == "sudo"


def test_parse_web_access_log():
    log_text = '198.51.100.44 - admin [12/Aug/2026:18:22:01 +0000] "GET /vulnerabilities/sqli/ HTTP/1.1" 500 482'
    events = parse_log(log_text)
    assert len(events) == 1
    ev = events[0]
    assert ev["source_ip"] == "198.51.100.44"
    assert ev["username"] == "admin"
    assert ev["service"] == "http"
    assert ev["status"] == "failed"


def test_parse_json_log():
    json_log = '[{"timestamp": "2026-08-12T19:00:01Z", "event_type": "failed_login", "username": "root", "source_ip": "198.51.100.99", "service": "ssh"}]'
    events = parse_log(json_log)
    assert len(events) == 1
    assert events[0]["username"] == "root"
    assert events[0]["source_ip"] == "198.51.100.99"


def test_parse_csv_log():
    csv_log = "timestamp,event_type,username,source_ip,service\n2026-08-12,failed_login,admin,192.168.1.50,ssh"
    events = parse_log(csv_log)
    assert len(events) == 1
    assert events[0]["username"] == "admin"
    assert events[0]["source_ip"] == "192.168.1.50"


def test_parse_empty_and_malformed():
    assert parse_log("") == []
    assert parse_log("   \n\n  ") == []
    events = parse_log("Random noise line with no structure whatsoever")
    # Shouldn't crash and should return empty or generic
    assert isinstance(events, list)
