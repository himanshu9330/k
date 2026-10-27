"""
SentinelAI-X Deterministic Rule-Based Threat Detection Engine
===============================================================
Analyzes normalized event streams and applies heuristic security signatures
to identify cyber threats prior to or independent of Generative AI.

Ensures the platform maintains reliable, deterministic detection capabilities
even if external AI services are offline or degraded.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict


def detect_threats(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluate normalized security events against deterministic detection rules.

    Returns:
        Structured dictionary containing incident classification, severity,
        target parameters, and matched rule evidence.
    """
    if not events:
        return {
            "incident_type": "No Activity",
            "severity": "LOW",
            "source_ip": "Unknown",
            "target_service": "Unknown",
            "target_accounts": [],
            "failed_attempts": 0,
            "mitre_technique": "None",
            "confidence": 0.0,
            "evidence": ["No events supplied for analysis."],
            "matched_rules": []
        }

    # Aggregate telemetry by source IP and user
    ip_failed_counts = defaultdict(int)
    ip_targeted_users = defaultdict(set)
    ip_targeted_services = defaultdict(set)
    ip_targeted_ports = defaultdict(set)
    
    suspicious_commands = []
    web_attacks = []
    all_users = set()
    all_services = set()
    all_source_ips = set()

    for ev in events:
        ip = ev.get("source_ip")
        user = ev.get("username")
        svc = ev.get("service")
        port = ev.get("port")
        status = str(ev.get("status", "")).lower()
        ev_type = str(ev.get("event_type", "")).lower()
        raw = str(ev.get("raw_log", ""))

        if ip:
            all_source_ips.add(ip)
        if user:
            all_users.add(user)
        if svc:
            all_services.add(svc)

        # Track failed authentication
        if status == "failed" or "fail" in ev_type or "invalid" in ev_type:
            if ip:
                ip_failed_counts[ip] += 1
                if user:
                    ip_targeted_users[ip].add(user)
                if svc:
                    ip_targeted_services[ip].add(svc)
                if port:
                    ip_targeted_ports[ip].add(port)

        # Check for suspicious command executions
        if "sudo" in ev_type or "command" in ev_type or "privilege" in ev_type:
            for pattern in ["/etc/shadow", "/etc/passwd", "chmod 777", "curl", "wget", "nmap", "nc -e", "bash -i"]:
                if pattern in raw:
                    suspicious_commands.append({"user": user, "pattern": pattern, "raw": raw})

        # Check for web application injection / traversal
        for pattern in ["../", "..\\", "UNION SELECT", "' OR '1'='1", "<script>", "etc/passwd"]:
            if pattern in raw:
                web_attacks.append({"ip": ip, "pattern": pattern, "raw": raw})

    # -------------------------------------------------------------------------
    # RULE 1: Privilege Escalation / Sensitive Command Execution
    # -------------------------------------------------------------------------
    if suspicious_commands:
        target_user = suspicious_commands[0]["user"] or "root"
        return {
            "incident_type": "Suspicious Privilege Escalation / Command Execution",
            "severity": "CRITICAL",
            "source_ip": list(all_source_ips)[0] if all_source_ips else "localhost",
            "target_service": "sudo",
            "target_accounts": [target_user],
            "failed_attempts": 0,
            "mitre_technique": "T1059",
            "confidence": 0.95,
            "explanation": f"Detected execution of high-risk utility/file access: {suspicious_commands[0]['pattern']}",
            "evidence": [cmd["raw"] for cmd in suspicious_commands],
            "matched_rules": ["RULE_PRIVILEGE_ESCALATION_COMMAND"]
        }

    # -------------------------------------------------------------------------
    # RULE 2: Web Application Attack / Directory Traversal / SQLi
    # -------------------------------------------------------------------------
    if web_attacks:
        src_ip = web_attacks[0]["ip"] or "Unknown"
        return {
            "incident_type": "Web Application Exploitation Attempt",
            "severity": "HIGH",
            "source_ip": src_ip,
            "target_service": "http",
            "target_accounts": [],
            "failed_attempts": len(web_attacks),
            "mitre_technique": "T1190",
            "confidence": 0.90,
            "explanation": f"Observed web attack payload pattern '{web_attacks[0]['pattern']}' from {src_ip}.",
            "evidence": [w["raw"] for w in web_attacks],
            "matched_rules": ["RULE_WEB_EXPLOITATION_SIGNATURE"]
        }

    # -------------------------------------------------------------------------
    # RULE 3: Password Spray Attack (Single IP, Multiple Target Accounts >= 3)
    # -------------------------------------------------------------------------
    for ip, users in ip_targeted_users.items():
        if len(users) >= 3 and ip_failed_counts[ip] >= 3:
            return {
                "incident_type": "Password Spray Attack",
                "severity": "HIGH",
                "source_ip": ip,
                "target_service": list(ip_targeted_services[ip])[0] if ip_targeted_services[ip] else "ssh",
                "target_accounts": sorted(list(users)),
                "failed_attempts": ip_failed_counts[ip],
                "mitre_technique": "T1110.003",
                "confidence": 0.92,
                "explanation": f"Source IP {ip} attempted failed logins across {len(users)} distinct accounts ({', '.join(sorted(list(users)))}).",
                "evidence": [f"Source {ip} targeted accounts: {', '.join(sorted(list(users)))} with {ip_failed_counts[ip]} total failed attempts."],
                "matched_rules": ["RULE_PASSWORD_SPRAY_DETECTION"]
            }

    # -------------------------------------------------------------------------
    # RULE 4: Port Scanning / Multi-Port Reconnaissance (>= 4 Distinct Ports)
    # -------------------------------------------------------------------------
    for ip, ports in ip_targeted_ports.items():
        if len(ports) >= 4:
            return {
                "incident_type": "Network Service Discovery / Port Scan",
                "severity": "MEDIUM",
                "source_ip": ip,
                "target_service": "multi-port",
                "target_accounts": [],
                "failed_attempts": len(ports),
                "mitre_technique": "T1046",
                "confidence": 0.88,
                "explanation": f"Source IP {ip} initiated connection requests across {len(ports)} distinct ports ({', '.join(str(p) for p in sorted(list(ports)))}).",
                "evidence": [f"Ports probed by {ip}: {sorted(list(ports))}"],
                "matched_rules": ["RULE_PORT_SCAN_RECON"]
            }

    # -------------------------------------------------------------------------
    # RULE 5: Brute Force Attack (Single IP, >= 3 Failed Attempts)
    # -------------------------------------------------------------------------
    for ip, count in ip_failed_counts.items():
        if count >= 3:
            users = sorted(list(ip_targeted_users[ip])) if ip in ip_targeted_users else list(all_users)
            svcs = list(ip_targeted_services[ip]) if ip in ip_targeted_services else list(all_services)
            return {
                "incident_type": "Brute Force Attack",
                "severity": "HIGH",
                "source_ip": ip,
                "target_service": svcs[0] if svcs else "ssh",
                "target_accounts": users,
                "failed_attempts": count,
                "mitre_technique": "T1110",
                "confidence": 0.95,
                "explanation": f"Observed {count} repeated authentication failures originating from source IP {ip}.",
                "evidence": [f"Failed authentication attempts from {ip}: count = {count}, target accounts = {users}"],
                "matched_rules": ["RULE_BRUTE_FORCE_VELOCITY"]
            }

    # -------------------------------------------------------------------------
    # RULE 6: Low Volume Authentication Failure (1-2 Failed Attempts)
    # -------------------------------------------------------------------------
    for ip, count in ip_failed_counts.items():
        users = sorted(list(ip_targeted_users[ip])) if ip in ip_targeted_users else list(all_users)
        svcs = list(ip_targeted_services[ip]) if ip in ip_targeted_services else list(all_services)
        return {
            "incident_type": "Authentication Failure",
            "severity": "LOW",
            "source_ip": ip,
            "target_service": svcs[0] if svcs else "ssh",
            "target_accounts": users,
            "failed_attempts": count,
            "mitre_technique": "T1110.001",
            "confidence": 0.70,
            "explanation": f"Recorded {count} isolated failed authentication attempt(s) from {ip}.",
            "evidence": [f"Isolated failed attempt(s) from {ip}"],
            "matched_rules": ["RULE_ISOLATED_AUTH_FAILURE"]
        }

    # -------------------------------------------------------------------------
    # RULE 7: Normal Activity / Successful Logins
    # -------------------------------------------------------------------------
    return {
        "incident_type": "Normal Security Telemetry",
        "severity": "LOW",
        "source_ip": list(all_source_ips)[0] if all_source_ips else "Unknown",
        "target_service": list(all_services)[0] if all_services else "general",
        "target_accounts": list(all_users),
        "failed_attempts": 0,
        "mitre_technique": "T1078",
        "confidence": 0.60,
        "explanation": "Events represent routine legitimate activity with no identified malicious anomalies.",
        "evidence": [f"Processed {len(events)} normal event entries."],
        "matched_rules": ["RULE_ROUTINE_TELEMETRY"]
    }
