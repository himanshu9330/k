"""
SentinelAI-X Forensic Audit Logging Service
=============================================
Maintains an immutable audit trail for security operations.
Automatically sanitizes and masks sensitive parameters.
"""

import json
import logging
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.audit import AuditLog
from models.user import User

logger = logging.getLogger("sentinelai.audit")

SENSITIVE_KEYS = {"password", "token", "key", "secret", "api_key", "access_token", "hash"}


def sanitize_audit_data(data: Any) -> Any:
    """Recursively mask sensitive keys in audit logs."""
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if any(sens in k.lower() for sens in SENSITIVE_KEYS):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = sanitize_audit_data(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_audit_data(item) for item in data]
    return data


def log_audit_event(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    user: Optional[User] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """
    Persist an audit trail entry in the database.
    """
    clean_details_str = None
    if details:
        sanitized = sanitize_audit_data(details)
        clean_details_str = json.dumps(sanitized, default=str)

    audit_entry = AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else "SYSTEM_AUTOMATION",
        action=action.upper(),
        entity_type=entity_type.upper(),
        entity_id=str(entity_id) if entity_id else None,
        details=clean_details_str,
        ip_address=ip_address
    )

    db.add(audit_entry)
    try:
        db.commit()
        db.refresh(audit_entry)
        logger.info(f"Audit log recorded: [{audit_entry.action}] on {audit_entry.entity_type}:{audit_entry.entity_id} by {audit_entry.username}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to record audit log: {e}")

    return audit_entry


def get_audit_logs(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    search: Optional[str] = None
) -> Tuple[List[AuditLog], int]:
    """Retrieve filtered, paginated audit logs."""
    query = db.query(AuditLog)

    if action:
        query = query.filter(AuditLog.action == action.upper())
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type.upper())
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (AuditLog.username.ilike(search_pattern)) |
            (AuditLog.details.ilike(search_pattern)) |
            (AuditLog.entity_id.ilike(search_pattern))
        )

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(page_size).all()

    return items, total
