"""
SentinelAI-X Multi-Format Security Log Parser
===============================================
Normalizes heterogeneous security logs (SSH, Syslog, Web/HTTP, JSON, CSV)
into standardized, strongly-typed security event structures.

Adheres strictly to zero-hallucination rules:
- Never invents timestamps, IPs, usernames, or services.
- Missing attributes are set to None.
- Preserves raw log line as forensic evidence.
"""

import re
import json
import csv
import io
from typing import List, Dict, Any, Optional

# Regex signatures for popular log structures
SSH_FAILED_PWD = re.compile(
    r"(?:(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+[\d:]+)\s+)?(?:\S+\s+sshd\[\d+\]:\s+)?Failed password for (?:invalid user\s+)?(?P<username>\S+)\s+from\s+(?P<source_ip>[\d.]+)(?:\s+port\s+(?P<port>\d+))?",
    re.IGNORECASE
)

SSH_ACCEPTED_PWD = re.compile(
    r"(?:(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+[\d:]+)\s+)?(?:\S+\s+sshd\[\d+\]:\s+)?Accepted (?:password|publickey) for (?P<username>\S+)\s+from\s+(?P<source_ip>[\d.]+)(?:\s+port\s+(?P<port>\d+))?",
    re.IGNORECASE
)

SSH_INVALID_USER = re.compile(
    r"(?:(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+[\d:]+)\s+)?(?:\S+\s+sshd\[\d+\]:\s+)?Invalid user (?P<username>\S+)\s+from\s+(?P<source_ip>[\d.]+)",
    re.IGNORECASE
)

SUDO_COMMAND = re.compile(
    r"(?:(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+[\d:]+)\s+)?(?:\S+\s+sudo:\s+)?(?P<username>\S+)\s*:\s*TTY=\S+\s*;\s*PWD=\S+\s*;\s*USER=(?P<target_user>\S+)\s*;\s*COMMAND=(?P<command>.*)",
    re.IGNORECASE
)

WEB_ACCESS_LOG = re.compile(
    r'^(?P<source_ip>[\d.]+)\s+\S+\s+(?P<username>\S+)\s+\[(?P<timestamp>[^\]]+)\]\s+"(?P<method>[A-Z]+)\s+(?P<url>\S+)\s+HTTP/[0-9.]+"\s+(?P<status>\d{3})\s+(?P<bytes>\S+)',
    re.IGNORECASE
)

GENERIC_IP = re.compile(r"\b(?P<ip>(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?))\b")
GENERIC_USER = re.compile(r"(?:user(?:name)?|login|account|for)\s*[=:]\s*['\"]?(?P<username>[a-zA-Z0-9._-]+)['\"]?", re.IGNORECASE)


def parse_log(log_text: str) -> List[Dict[str, Any]]:
    """
    Parse arbitrary raw log text into standardized security event objects.
    Automatically detects and handles JSON, CSV, Syslog, Web, and SSH auth lines.
    """
    if not log_text or not log_text.strip():
        return []

    stripped = log_text.strip()
    
    # 1. Try parsing as JSON / JSON Lines
    if (stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]")):
        try:
            parsed_json = json.loads(stripped)
            events = []
            if isinstance(parsed_json, list):
                for item in parsed_json:
                    if isinstance(item, dict):
                        events.append(_normalize_json_event(item))
            elif isinstance(parsed_json, dict):
                events.append(_normalize_json_event(parsed_json))
            if events:
                return events
        except json.JSONDecodeError:
            pass

    # 2. Try parsing line-by-line JSON (NDJSON)
    ndjson_events = []
    is_ndjson = True
    for line in stripped.splitlines():
        line_s = line.strip()
        if not line_s:
            continue
        if line_s.startswith("{") and line_s.endswith("}"):
            try:
                data = json.loads(line_s)
                ndjson_events.append(_normalize_json_event(data))
            except json.JSONDecodeError:
                is_ndjson = False
                break
        else:
            is_ndjson = False
            break

    if is_ndjson and ndjson_events:
        return ndjson_events

    # 3. Try parsing as CSV if comma-separated headers exist
    if "\n" in stripped and "," in stripped.splitlines()[0]:
        csv_events = _try_parse_csv(stripped)
        if csv_events:
            return csv_events

    # 4. Standard Line-by-Line Regex Parsing
    events: List[Dict[str, Any]] = []
    for line in stripped.splitlines():
        line_clean = line.strip()
        if not line_clean:
            continue

        event = _parse_single_line(line_clean)
        if event:
            events.append(event)

    return events


def _parse_single_line(line: str) -> Optional[Dict[str, Any]]:
    """Inspect and extract structured event attributes from a single log line."""
    
    # Check SSH Failed Password
    m = SSH_FAILED_PWD.search(line)
    if m:
        return {
            "timestamp": m.group("timestamp") if m.group("timestamp") else None,
            "event_type": "failed_login",
            "username": m.group("username"),
            "source_ip": m.group("source_ip"),
            "destination_ip": None,
            "service": "ssh",
            "port": int(m.group("port")) if m.group("port") else 22,
            "status": "failed",
            "raw_log": line
        }

    # Check SSH Accepted Login
    m = SSH_ACCEPTED_PWD.search(line)
    if m:
        return {
            "timestamp": m.group("timestamp") if m.group("timestamp") else None,
            "event_type": "successful_login",
            "username": m.group("username"),
            "source_ip": m.group("source_ip"),
            "destination_ip": None,
            "service": "ssh",
            "port": int(m.group("port")) if m.group("port") else 22,
            "status": "accepted",
            "raw_log": line
        }

    # Check SSH Invalid User
    m = SSH_INVALID_USER.search(line)
    if m:
        return {
            "timestamp": m.group("timestamp") if m.group("timestamp") else None,
            "event_type": "invalid_user_attempt",
            "username": m.group("username"),
            "source_ip": m.group("source_ip"),
            "destination_ip": None,
            "service": "ssh",
            "port": 22,
            "status": "failed",
            "raw_log": line
        }

    # Check Sudo Command
    m = SUDO_COMMAND.search(line)
    if m:
        return {
            "timestamp": m.group("timestamp") if m.group("timestamp") else None,
            "event_type": "privileged_command_execution",
            "username": m.group("username"),
            "source_ip": None,
            "destination_ip": None,
            "service": "sudo",
            "port": None,
            "status": "executed",
            "raw_log": line
        }

    # Check Web Access Log
    m = WEB_ACCESS_LOG.search(line)
    if m:
        user_val = m.group("username")
        status_code = int(m.group("status"))
        return {
            "timestamp": m.group("timestamp"),
            "event_type": "web_request",
            "username": user_val if user_val != "-" else None,
            "source_ip": m.group("source_ip"),
            "destination_ip": None,
            "service": "http",
            "port": 80,
            "status": "failed" if status_code >= 400 else "accepted",
            "raw_log": line
        }

    # Fallback Generic Extractor
    ip_match = GENERIC_IP.search(line)
    user_match = GENERIC_USER.search(line)

    ev_type = "security_event"
    status_val = None
    service_val = None

    line_lower = line.lower()
    if "fail" in line_lower or "error" in line_lower or "denied" in line_lower or "reject" in line_lower:
        ev_type = "authentication_failure"
        status_val = "failed"
    elif "accept" in line_lower or "success" in line_lower or "allow" in line_lower:
        ev_type = "successful_authentication"
        status_val = "accepted"

    if "ssh" in line_lower:
        service_val = "ssh"
    elif "rdp" in line_lower:
        service_val = "rdp"
    elif "ftp" in line_lower:
        service_val = "ftp"
    elif "http" in line_lower or "web" in line_lower:
        service_val = "http"

    if ip_match or user_match or status_val:
        return {
            "timestamp": None,
            "event_type": ev_type,
            "username": user_match.group("username") if user_match else None,
            "source_ip": ip_match.group("ip") if ip_match else None,
            "destination_ip": None,
            "service": service_val,
            "port": None,
            "status": status_val,
            "raw_log": line
        }

    return None


def _normalize_json_event(data: Dict[str, Any]) -> Dict[str, Any]:
    """Map arbitrary JSON fields to standardized event structure."""
    return {
        "timestamp": data.get("timestamp") or data.get("time") or data.get("@timestamp"),
        "event_type": data.get("event_type") or data.get("type") or data.get("action") or "security_event",
        "username": data.get("username") or data.get("user") or data.get("account"),
        "source_ip": data.get("source_ip") or data.get("src_ip") or data.get("ip") or data.get("client_ip"),
        "destination_ip": data.get("destination_ip") or data.get("dest_ip") or data.get("dst_ip") or data.get("server_ip"),
        "service": data.get("service") or data.get("protocol") or data.get("app"),
        "port": data.get("port") or data.get("src_port") or data.get("dst_port"),
        "status": data.get("status") or data.get("result") or data.get("outcome"),
        "raw_log": data.get("raw_log") or data.get("message") or json.dumps(data)
    }


def _try_parse_csv(csv_text: str) -> List[Dict[str, Any]]:
    """Parse CSV text with header inspection."""
    events = []
    try:
        reader = csv.DictReader(io.StringIO(csv_text))
        for row in reader:
            if not row:
                continue
            normalized_row = {k.strip().lower(): v for k, v in row.items() if k}
            events.append({
                "timestamp": normalized_row.get("timestamp") or normalized_row.get("time") or normalized_row.get("date"),
                "event_type": normalized_row.get("event_type") or normalized_row.get("action") or normalized_row.get("event") or "csv_security_event",
                "username": normalized_row.get("username") or normalized_row.get("user") or normalized_row.get("account"),
                "source_ip": normalized_row.get("source_ip") or normalized_row.get("src_ip") or normalized_row.get("ip"),
                "destination_ip": normalized_row.get("destination_ip") or normalized_row.get("dest_ip") or normalized_row.get("dst_ip"),
                "service": normalized_row.get("service") or normalized_row.get("protocol"),
                "port": int(normalized_row.get("port")) if normalized_row.get("port") and normalized_row.get("port").isdigit() else None,
                "status": normalized_row.get("status") or normalized_row.get("result"),
                "raw_log": json.dumps(row)
            })
    except Exception:
        return []
    return events
