"""
SentinelAI-X Incident Response Recommendation Engine
======================================================
Synthesizes deterministic defensive countermeasures and AI-recommended
mitigations into structured, prioritized response action entities.

STRICT HUMAN-IN-THE-LOOP ARCHITECTURE:
Actions are classified as PROPOSED recommendations with operational risk ratings
and CLI command previews. The system NEVER executes destructive actions automatically.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models.response_action import ResponseAction, ActionStatus, ActionPriority


def generate_response_recommendations(
    analysis: Dict[str, Any],
    source_ip: Optional[str] = None,
    target_service: Optional[str] = None,
    target_accounts: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Generate structured, prioritized defensive response actions.
    Combines rule-based defensive best practices with Gemini recommendations.
    """
    actions: List[Dict[str, Any]] = []
    seen_action_titles = set()

    clean_ip = source_ip or analysis.get("source_ip")
    if clean_ip == "Unknown" or clean_ip == "null":
        clean_ip = None

    service = (target_service or analysis.get("target_service") or "").lower()
    accounts = target_accounts or analysis.get("target_accounts") or []
    if isinstance(accounts, str):
        accounts = [accounts]
    severity = str(analysis.get("severity", "MEDIUM")).upper()

    # 1. IP Containment Action (P1/P2)
    if clean_ip and clean_ip not in ("127.0.0.1", "localhost", "0.0.0.0"):
        actions.append({
            "action": f"Block Threat Actor IP ({clean_ip}) on Perimeter Firewall",
            "reason": f"Active source of repeated malicious authentication attempts targeting {service.upper() or 'services'}.",
            "priority": ActionPriority.P1_CRITICAL.value if severity in ("CRITICAL", "HIGH") else ActionPriority.P2_HIGH.value,
            "risk_level": "LOW",
            "command_preview": f"iptables -A INPUT -s {clean_ip} -j DROP\n# Windows Firewall:\nNew-NetFirewallRule -DisplayName 'Block-{clean_ip}' -Direction Inbound -Action Block -RemoteAddress {clean_ip}",
            "requires_approval": True,
            "status": ActionStatus.PROPOSED.value
        })
        seen_action_titles.add(f"Block Threat Actor IP ({clean_ip}) on Perimeter Firewall")

    # 2. Account Security & Credential Rotation (P2)
    if accounts:
        acc_list_str = ", ".join(str(a) for a in accounts)
        has_privileged = any(str(a).lower() in ("root", "admin", "administrator", "system") for a in accounts)
        actions.append({
            "action": f"Enforce Password Reset & Terminate Active Sessions for [{acc_list_str}]",
            "reason": "Targeted accounts may have experienced credential spray or compromised passwords.",
            "priority": ActionPriority.P1_CRITICAL.value if has_privileged else ActionPriority.P2_HIGH.value,
            "risk_level": "MEDIUM",
            "command_preview": f"# Linux session kill:\npkill -u {accounts[0]} -9\n# Force password change on next login:\npasswd -e {accounts[0]}",
            "requires_approval": True,
            "status": ActionStatus.PROPOSED.value
        })
        seen_action_titles.add(f"Enforce Password Reset & Terminate Active Sessions for [{acc_list_str}]")

    # 3. Service Hardening Actions
    if "ssh" in service:
        actions.append({
            "action": "Harden SSH Configuration (Disable Root Login & Enforce Public Key Auth)",
            "reason": "Prevents password brute-forcing and eliminates single point of compromise on root user.",
            "priority": ActionPriority.P2_HIGH.value,
            "risk_level": "MEDIUM",
            "command_preview": "sed -i 's/^PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config\nsed -i 's/^PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config\nsystemctl reload sshd",
            "requires_approval": True,
            "status": ActionStatus.PROPOSED.value
        })
        actions.append({
            "action": "Deploy Rate Limiting with Fail2Ban on SSH Service",
            "reason": "Automatically bans IP addresses that exhibit continuous failed authentication patterns.",
            "priority": ActionPriority.P3_MEDIUM.value,
            "risk_level": "LOW",
            "command_preview": "apt-get install -y fail2ban && systemctl enable --now fail2ban",
            "requires_approval": True,
            "status": ActionStatus.PROPOSED.value
        })

    # 4. Integrate AI-Generated Recommendations if novel
    raw_ai_actions = analysis.get("recommended_actions") or []
    for raw_act in raw_ai_actions:
        if isinstance(raw_act, str) and raw_act.strip():
            title = raw_act.strip()
            if not any(title.lower() in existing.lower() for existing in seen_action_titles):
                actions.append({
                    "action": title,
                    "reason": "Recommended by AI Security Analysis based on incident context.",
                    "priority": ActionPriority.P3_MEDIUM.value,
                    "risk_level": "LOW",
                    "command_preview": f"# Review security policy: {title}",
                    "requires_approval": True,
                    "status": ActionStatus.PROPOSED.value
                })
                seen_action_titles.add(title)

    # 5. Fallback Default Action if list is still empty
    if not actions:
        actions.append({
            "action": "Perform Detailed Forensic Log Audit and Host Isolation",
            "reason": "Investigate host logs for indicator of compromise persistence.",
            "priority": ActionPriority.P3_MEDIUM.value,
            "risk_level": "LOW",
            "command_preview": "# Audit auth.log and syslog for lateral movement indicators",
            "requires_approval": True,
            "status": ActionStatus.PROPOSED.value
        })

    return actions
