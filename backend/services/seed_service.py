"""
SentinelAI-X Enterprise Demo Data Seeder
========================================
Populates the database with 6 realistic enterprise security incidents,
complete with timeline events, IOC threat indicators, MITRE techniques,
response action proposals, and explainable risk breakdowns.
Ensures the platform is never empty and is immediately demonstrable.
"""

import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from models.incident import Incident, IncidentStatus, IncidentSeverity
from models.risk_assessment import RiskAssessment
from models.response_action import ResponseAction, ActionStatus, ActionPriority
from models.timeline import TimelineEvent
from models.threat import ThreatIndicator
from models.log import SecurityLog
from models.event import SecurityEvent
from services.mitre_service import seed_mitre_database
from services.risk_service import calculate_risk_score


def seed_demo_data_if_empty(db: Session):
    """
    Seeds initial MITRE techniques, realistic demo incidents, and IOCs
    if the database contains no incident records.
    """
    # Ensure MITRE techniques are seeded first
    seed_mitre_database(db)

    # Check if incidents already exist
    count = db.query(Incident).count()
    if count > 0:
        return

    now = datetime.now(timezone.utc)

    # =========================================================================
    # INCIDENT 1: SSH Brute Force Attack (CRITICAL)
    # =========================================================================
    t1 = now - timedelta(hours=3, minutes=15)
    log1 = SecurityLog(
        filename="auth_production_ssh.log",
        file_size=1420,
        log_format="syslog_ssh",
        raw_content="Aug 29 19:45:10 server sshd: Failed password for admin from 192.168.1.15\nAug 29 19:45:14 server sshd: Failed password for admin from 192.168.1.15\nAug 29 19:45:18 server sshd: Failed password for root from 192.168.1.15\nAug 29 19:45:22 server sshd: Failed password for root from 192.168.1.15\nAug 29 19:45:55 server sshd: Accepted password for sarah_admin from 10.0.0.25",
        event_count=5,
        created_at=t1
    )
    db.add(log1)
    db.flush()

    events1 = [
        SecurityEvent(log_id=log1.id, timestamp=t1, event_type="failed_login", source_ip="192.168.1.15", username="admin", service="ssh", port=22, status="failed", raw_log="Aug 29 19:45:10 server sshd: Failed password for admin from 192.168.1.15"),
        SecurityEvent(log_id=log1.id, timestamp=t1 + timedelta(seconds=4), event_type="failed_login", source_ip="192.168.1.15", username="admin", service="ssh", port=22, status="failed", raw_log="Aug 29 19:45:14 server sshd: Failed password for admin from 192.168.1.15"),
        SecurityEvent(log_id=log1.id, timestamp=t1 + timedelta(seconds=8), event_type="failed_login", source_ip="192.168.1.15", username="root", service="ssh", port=22, status="failed", raw_log="Aug 29 19:45:18 server sshd: Failed password for root from 192.168.1.15"),
        SecurityEvent(log_id=log1.id, timestamp=t1 + timedelta(seconds=12), event_type="failed_login", source_ip="192.168.1.15", username="root", service="ssh", port=22, status="failed", raw_log="Aug 29 19:45:22 server sshd: Failed password for root from 192.168.1.15"),
        SecurityEvent(log_id=log1.id, timestamp=t1 + timedelta(seconds=45), event_type="successful_login", source_ip="10.0.0.25", username="sarah_admin", service="ssh", port=22, status="accepted", raw_log="Aug 29 19:45:55 server sshd: Accepted password for sarah_admin from 10.0.0.25")
    ]
    db.add_all(events1)

    inc1 = Incident(
        incident_id="INC-000001",
        title="SSH Credential Brute Force Velocity Burst",
        description="High-velocity automated authentication failure sequence targeting privileged accounts (admin, root) originating from single external IP.",
        incident_type="Brute Force Attack",
        severity=IncidentSeverity.CRITICAL.value,
        risk_score=95,
        risk_level="CRITICAL",
        status=IncidentStatus.INVESTIGATING.value,
        source_ip="192.168.1.15",
        target_service="ssh",
        affected_asset="auth-gateway-prod-01",
        target_accounts=json.dumps(["admin", "root"]),
        failed_attempts=4,
        mitre_technique_id="T1110",
        confidence=0.95,
        ai_status="COMPLETED",
        ai_explanation="Automated password guessing pattern detected. The adversary executed rapid sequential attempts against administrative accounts (admin, root) within a 12-second window. Risk is compounded by privileged user targeting on port 22.",
        investigation_steps=json.dumps([
            "Verify perimeter firewall logs to confirm whether 192.168.1.15 originated additional scans.",
            "Confirm that root and admin passwords remained uncompromised.",
            "Enforce immediate IP block on ingress edge gateway."
        ]),
        analyst_notes="Analyst Sarah Connor: Triage initiated. Source IP added to perimeter block list. Fail2Ban rule applied.",
        log_id=log1.id,
        created_at=t1,
        updated_at=now - timedelta(minutes=45)
    )
    db.add(inc1)
    db.flush()

    risk1_data = calculate_risk_score({"severity": "CRITICAL", "failed_attempts": 4, "target_accounts": ["admin", "root"], "target_service": "ssh", "incident_type": "Brute Force Attack", "confidence": 0.95})
    db.add(RiskAssessment(incident_id=inc1.id, final_score=95, risk_level="CRITICAL", base_score=50, frequency_score=15, privilege_score=15, service_score=10, pattern_score=10, confidence_score=5, formula=risk1_data["formula"], summary=risk1_data["summary"], factors_json=json.dumps(risk1_data["factors"])))

    db.add_all([
        ResponseAction(incident_id=inc1.id, action="Block Attacker IP 192.168.1.15 on Perimeter Firewall", reason="Neutralize ongoing automated credential guessing.", priority=ActionPriority.P1.value, risk_level="LOW", command_preview="iptables -A INPUT -s 192.168.1.15 -j DROP\nufw deny from 192.168.1.15", status=ActionStatus.APPROVED.value, requires_approval=True),
        ResponseAction(incident_id=inc1.id, action="Force Lock and Password Reset on Admin/Root Accounts", reason="Ensure credentials were not partially exposed.", priority=ActionPriority.P2.value, risk_level="MEDIUM", command_preview="passwd -l admin && passwd -l root", status=ActionStatus.PROPOSED.value, requires_approval=True),
        ResponseAction(incident_id=inc1.id, action="Harden SSH Configuration (Disable Password Auth & Root Login)", reason="Eliminates password brute-force attack surface permanently.", priority=ActionPriority.P2.value, risk_level="MEDIUM", command_preview="sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config\nsystemctl reload sshd", status=ActionStatus.PROPOSED.value, requires_approval=True)
    ])

    db.add_all([
        TimelineEvent(incident_id=inc1.id, timestamp=t1, event_type="DETECTION", title="Velocity Anomaly Detected", description="SentinelAI-X log parser flagged 4 consecutive SSH authentication failures from 192.168.1.15.", source="Log Parser", actor="Rule Engine", status_after="OPEN"),
        TimelineEvent(incident_id=inc1.id, timestamp=t1 + timedelta(minutes=1), event_type="AI_ANALYSIS", title="Gemini AI Threat Corroboration", description="Gemini confirmed Brute Force pattern (T1110), calculated 95/100 risk score, and formulated investigation playbook.", source="Google Gemini 3.6 Flash", actor="Gemini AI", status_after="OPEN"),
        TimelineEvent(incident_id=inc1.id, timestamp=t1 + timedelta(minutes=15), event_type="INITIAL_INVESTIGATION", title="Analyst Triage Commenced", description="Security analyst Sarah Connor assigned incident and initiated firewall inspection.", source="SOC Web UI", actor="Sarah Connor (Analyst)", status_after="INVESTIGATING"),
        TimelineEvent(incident_id=inc1.id, timestamp=t1 + timedelta(minutes=25), event_type="CONTAINMENT", title="Perimeter Block Rule Approved", description="Approved P1 firewall block action for source IP 192.168.1.15.", source="SOC Web UI", actor="Sarah Connor (Analyst)", status_after="INVESTIGATING")
    ])

    db.add(ThreatIndicator(
        incident_id=inc1.id,
        indicator_type="IP",
        value="192.168.1.15",
        threat_type="SSH Brute Force Velocity Origin",
        reputation_score=92,
        risk_level="CRITICAL",
        confidence=0.95,
        source="DEMO_LOCAL_INTEL",
        country="Reserved / Internal",
        asn="AS-PRIVATE",
        actor_group="Automated SSH Scanner Node",
        mitre_technique_id="T1110",
        details="Repeated credential guessing burst observed against port 22.",
        first_seen=t1,
        last_seen=t1
    ))

    # =========================================================================
    # INCIDENT 2: Password Spraying Attack (HIGH)
    # =========================================================================
    t2 = now - timedelta(hours=6, minutes=20)
    inc2 = Incident(
        incident_id="INC-000002",
        title="Distributed Identity Password Spraying",
        description="Single external IP attempting authentication across multiple distinct user accounts to evade per-user lockout thresholds.",
        incident_type="Password Spraying Attack",
        severity=IncidentSeverity.HIGH.value,
        risk_score=85,
        risk_level="CRITICAL",
        status=IncidentStatus.OPEN.value,
        source_ip="203.0.113.88",
        target_service="active-directory",
        affected_asset="idp-cluster-node-02",
        target_accounts=json.dumps(["jsmith", "bwayne", "ckent", "dprince", "bbanner"]),
        failed_attempts=5,
        mitre_technique_id="T1110.003",
        confidence=0.90,
        ai_status="COMPLETED",
        ai_explanation="Identified classic horizontal password spray attack (T1110.003). The attacker tested 1 password attempt per unique account across 5 usernames, purposefully evading single-account lockout triggers.",
        investigation_steps=json.dumps([
            "Audit Active Directory sign-in logs for other IP origins with matching user-agent strings.",
            "Verify whether any targeted user account recorded a subsequent successful login.",
            "Implement smart lockout threshold across federated identity providers."
        ]),
        created_at=t2,
        updated_at=t2
    )
    db.add(inc2)
    db.flush()

    risk2_data = calculate_risk_score({"severity": "HIGH", "failed_attempts": 5, "target_accounts": ["jsmith", "bwayne", "ckent", "dprince", "bbanner"], "target_service": "active-directory", "incident_type": "Password Spraying Attack", "confidence": 0.90})
    db.add(RiskAssessment(incident_id=inc2.id, final_score=85, risk_level="CRITICAL", base_score=40, frequency_score=20, privilege_score=0, service_score=10, pattern_score=10, confidence_score=5, formula=risk2_data["formula"], summary=risk2_data["summary"], factors_json=json.dumps(risk2_data["factors"])))

    db.add(ResponseAction(incident_id=inc2.id, action="Block Attacking IP 203.0.113.88 on Ingress Proxy", reason="Stop ongoing horizontal spraying attempts.", priority=ActionPriority.P1.value, risk_level="LOW", command_preview="iptables -A INPUT -s 203.0.113.88 -j DROP", status=ActionStatus.PROPOSED.value, requires_approval=True))
    db.add(TimelineEvent(incident_id=inc2.id, timestamp=t2, event_type="DETECTION", title="Password Spraying Pattern Identified", description="Horizontal multi-user failed authentication pattern detected from 203.0.113.88.", source="Detection Engine", actor="Rule Engine", status_after="OPEN"))
    db.add(ThreatIndicator(incident_id=inc2.id, indicator_type="IP", value="203.0.113.88", threat_type="Distributed Password Spraying Origin", reputation_score=88, risk_level="HIGH", confidence=0.90, source="DEMO_LOCAL_INTEL", country="United States", asn="AS64496 TEST-NET-3", actor_group="Identity Harvesting Actor", mitre_technique_id="T1110.003", details="Attacking identity endpoint with common enterprise password list.", first_seen=t2, last_seen=t2))

    # =========================================================================
    # INCIDENT 3: Sudo Privilege Escalation (CRITICAL)
    # =========================================================================
    t3 = now - timedelta(hours=14)
    inc3 = Incident(
        incident_id="INC-000003",
        title="Unauthorized Sudo Command Execution on /etc/shadow",
        description="Non-root service user executed unauthorized sudo read commands targeting sensitive system password hashes.",
        incident_type="Privilege Escalation Command",
        severity=IncidentSeverity.CRITICAL.value,
        risk_score=90,
        risk_level="CRITICAL",
        status=IncidentStatus.CONTAINED.value,
        source_ip="10.0.2.45",
        target_service="sudo",
        affected_asset="prod-app-server-04",
        target_accounts=json.dumps(["user_test", "root"]),
        failed_attempts=0,
        mitre_technique_id="T1059",
        confidence=0.96,
        ai_status="COMPLETED",
        ai_explanation="Suspicious execution of '/bin/cat /etc/shadow' by non-privileged account 'user_test'. This matches MITRE T1059 / T1003 credential dumping behavior following possible initial access.",
        investigation_steps=json.dumps([
            "Inspect process tree and parent process of user_test session.",
            "Verify if shadow file hashes were exfiltrated over network sockets.",
            "Revoke sudoers privileges for user_test."
        ]),
        analyst_notes="Contained: user_test session terminated and account disabled. Sudoers file restored from version control.",
        created_at=t3,
        updated_at=now - timedelta(hours=2)
    )
    db.add(inc3)
    db.flush()

    risk3_data = calculate_risk_score({"severity": "CRITICAL", "failed_attempts": 1, "target_accounts": ["user_test", "root"], "target_service": "sudo", "incident_type": "Privilege Escalation Command", "confidence": 0.96})
    db.add(RiskAssessment(incident_id=inc3.id, final_score=90, risk_level="CRITICAL", base_score=50, frequency_score=5, privilege_score=15, service_score=10, pattern_score=10, confidence_score=5, formula=risk3_data["formula"], summary=risk3_data["summary"], factors_json=json.dumps(risk3_data["factors"])))
    db.add(ResponseAction(incident_id=inc3.id, action="Immediately Terminate user_test Active Sessions and Lock Account", reason="Halt further unauthorized privilege escalation.", priority=ActionPriority.P1.value, risk_level="MEDIUM", command_preview="pkill -u user_test && passwd -l user_test", status=ActionStatus.EXECUTED.value, requires_approval=True))
    db.add(TimelineEvent(incident_id=inc3.id, timestamp=t3, event_type="DETECTION", title="Privilege Escalation Command Detected", description="Sudo execution of /bin/cat /etc/shadow captured in system logs.", source="Linux Auditd", actor="Detection Engine", status_after="OPEN"))
    db.add(TimelineEvent(incident_id=inc3.id, timestamp=t3 + timedelta(minutes=10), event_type="CONTAINMENT", title="Host Isolation & Session Termination", description="Analyst revoked session and locked compromised account.", source="SOC Web UI", actor="Lead Analyst", status_after="CONTAINED"))

    # =========================================================================
    # INCIDENT 4: Web Application SQLi & Directory Traversal (HIGH)
    # =========================================================================
    t4 = now - timedelta(hours=22)
    inc4 = Incident(
        incident_id="INC-000004",
        title="Web Ingress SQL Injection & Path Traversal Probing",
        description="Automated exploit scanner attempting SQL injection payloads and directory traversal against public web server.",
        incident_type="Web Application Attack",
        severity=IncidentSeverity.HIGH.value,
        risk_score=75,
        risk_level="HIGH",
        status=IncidentStatus.RESOLVED.value,
        source_ip="198.51.100.44",
        target_service="http",
        affected_asset="dmz-web-proxy-01",
        target_accounts=json.dumps(["www-data"]),
        failed_attempts=3,
        mitre_technique_id="T1190",
        confidence=0.88,
        ai_status="COMPLETED",
        ai_explanation="Observed classic URI parameter injection containing 'UNION SELECT' and '../../../../etc/passwd'. The web server responded with HTTP 500 and 403 status codes.",
        investigation_steps=json.dumps([
            "Check web server error logs for potential unhandled database exception disclosures.",
            "Verify WAF rule block statistics for 198.51.100.44."
        ]),
        analyst_notes="Resolved: WAF signature updated, IP added to permanent blocklist.",
        created_at=t4,
        updated_at=now - timedelta(hours=18)
    )
    db.add(inc4)
    db.flush()

    risk4_data = calculate_risk_score({"severity": "HIGH", "failed_attempts": 3, "target_accounts": ["www-data"], "target_service": "http", "incident_type": "Web Application Attack", "confidence": 0.88})
    db.add(RiskAssessment(incident_id=inc4.id, final_score=75, risk_level="HIGH", base_score=40, frequency_score=15, privilege_score=0, service_score=5, pattern_score=10, confidence_score=5, formula=risk4_data["formula"], summary=risk4_data["summary"], factors_json=json.dumps(risk4_data["factors"])))
    db.add(TimelineEvent(incident_id=inc4.id, timestamp=t4, event_type="DETECTION", title="SQLi Signature Match in HTTP Access Log", description="Inbound HTTP GET request containing SQL union syntax blocked by web application tier.", source="Nginx Access Log", actor="Rule Engine", status_after="OPEN"))
    db.add(TimelineEvent(incident_id=inc4.id, timestamp=t4 + timedelta(hours=4), event_type="RESOLUTION", title="WAF Rule Validated & Incident Closed", description="Ingress rule deployed; no further traversal attempts observed.", source="SOC Web UI", actor="Security Analyst", status_after="RESOLVED"))

    # =========================================================================
    # INCIDENT 5: Internal Port Scanning Reconnaissance (MEDIUM)
    # =========================================================================
    t5 = now - timedelta(days=1, hours=8)
    inc5 = Incident(
        incident_id="INC-000005",
        title="Multi-Port Internal Subnet Service Discovery",
        description="Internal host initiated connection requests across 6 distinct destination ports (21, 22, 80, 443, 3306, 8080).",
        incident_type="Network Service Discovery / Port Scan",
        severity=IncidentSeverity.MEDIUM.value,
        risk_score=55,
        risk_level="MEDIUM",
        status=IncidentStatus.RESOLVED.value,
        source_ip="10.0.0.99",
        target_service="multi-port",
        affected_asset="vlan-internal-dev",
        target_accounts=json.dumps([]),
        failed_attempts=6,
        mitre_technique_id="T1046",
        confidence=0.85,
        ai_status="COMPLETED",
        ai_explanation="Network reconnaissance detected (T1046). Host 10.0.0.99 probed standard administrative and database service ports across internal subnet.",
        investigation_steps=json.dumps(["Verify if scanning host belongs to authorized vulnerability scanner subnet."]),
        analyst_notes="False Alarm / Authorized Scan: Confirmed scheduled vulnerability assessment by IT security team.",
        created_at=t5,
        updated_at=t5 + timedelta(hours=1)
    )
    db.add(inc5)
    db.flush()

    risk5_data = calculate_risk_score({"severity": "MEDIUM", "failed_attempts": 6, "target_accounts": [], "target_service": "multi-port", "incident_type": "Network Service Discovery / Port Scan", "confidence": 0.85})
    db.add(RiskAssessment(incident_id=inc5.id, final_score=55, risk_level="MEDIUM", base_score=25, frequency_score=20, privilege_score=0, service_score=0, pattern_score=10, confidence_score=0, formula=risk5_data["formula"], summary=risk5_data["summary"], factors_json=json.dumps(risk5_data["factors"])))
    db.add(TimelineEvent(incident_id=inc5.id, timestamp=t5, event_type="DETECTION", title="Port Scanning Signature Detected", description="Multi-port SYN connection activity detected across 6 ports.", source="Network NetFlow", actor="Rule Engine", status_after="OPEN"))
    db.add(TimelineEvent(incident_id=inc5.id, timestamp=t5 + timedelta(minutes=40), event_type="RESOLUTION", title="Scan Verified as Authorized Audit", description="Internal ticket verified vulnerability assessment window.", source="SOC Web UI", actor="Security Analyst", status_after="RESOLVED"))

    # =========================================================================
    # INCIDENT 6: C2 Domain Beaconing Anomaly (HIGH)
    # =========================================================================
    t6 = now - timedelta(days=2, hours=3)
    inc6 = Incident(
        incident_id="INC-000006",
        title="Periodic C2 DNS Beaconing Anomaly",
        description="Endpoint workstation observed initiating repetitive DNS query intervals to known malicious domain.",
        incident_type="C2 Beaconing Traffic",
        severity=IncidentSeverity.HIGH.value,
        risk_score=78,
        risk_level="HIGH",
        status=IncidentStatus.FALSE_POSITIVE.value,
        source_ip="172.16.50.12",
        target_service="dns",
        affected_asset="workstation-fin-08",
        target_accounts=json.dumps(["finance_user"]),
        failed_attempts=12,
        mitre_technique_id="T1078",
        confidence=0.82,
        ai_status="COMPLETED",
        ai_explanation="Periodic outbound DNS queries matching potential beaconing intervals. Corroborated with threat intelligence domain database.",
        investigation_steps=json.dumps(["Isolate endpoint workstation and inspect local memory and DNS cache."]),
        analyst_notes="False Positive: Query generated by misconfigured legitimate financial data feed plugin.",
        created_at=t6,
        updated_at=t6 + timedelta(hours=3)
    )
    db.add(inc6)
    db.flush()

    risk6_data = calculate_risk_score({"severity": "HIGH", "failed_attempts": 12, "target_accounts": ["finance_user"], "target_service": "dns", "incident_type": "C2 Beaconing Traffic", "confidence": 0.82})
    db.add(RiskAssessment(incident_id=inc6.id, final_score=78, risk_level="HIGH", base_score=40, frequency_score=25, privilege_score=0, service_score=5, pattern_score=5, confidence_score=3, formula=risk6_data["formula"], summary=risk6_data["summary"], factors_json=json.dumps(risk6_data["factors"])))
    db.add(TimelineEvent(incident_id=inc6.id, timestamp=t6, event_type="DETECTION", title="Anomalous DNS Query Frequency Detected", description="12 queries in 60 seconds targeting external domain.", source="DNS Resolver Logs", actor="Rule Engine", status_after="OPEN"))
    db.add(TimelineEvent(incident_id=inc6.id, timestamp=t6 + timedelta(hours=2), event_type="RESOLUTION", title="Marked as False Positive", description="Software vendor verified benign telemetry format.", source="SOC Web UI", actor="Senior Analyst", status_after="FALSE_POSITIVE"))

    # Commit all seeded data
    db.commit()
