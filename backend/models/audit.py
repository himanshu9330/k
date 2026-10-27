"""
SentinelAI-X Audit Log Model
==============================
Maintains an immutable forensic audit trail of all security operations,
analyst status updates, response action approvals, and AI execution traces.
NEVER records credentials, secrets, or API keys.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    username = Column(String(100), nullable=True)  # Snapshot of username for fast audit querying
    action = Column(String(100), index=True, nullable=False)  # e.g., 'LOG_UPLOAD', 'INCIDENT_STATUS_UPDATE'
    entity_type = Column(String(50), index=True, nullable=False)  # 'INCIDENT', 'LOG', 'RESPONSE_ACTION', 'AUTH'
    entity_id = Column(String(100), index=True, nullable=True)
    details = Column(Text, nullable=True)  # JSON string of contextual non-sensitive details
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)

    # Relationships
    user = relationship("User")
