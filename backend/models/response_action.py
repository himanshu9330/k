"""
SentinelAI-X Incident Response Action Model
=============================================
Stores recommended containment, eradication, and remediation response actions.
Strictly implements Human-in-the-Loop approval workflows: actions are NEVER
executed automatically without authorized analyst review.
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ActionStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"


class ActionPriority(str, enum.Enum):
    P1_CRITICAL = "P1"
    P2_HIGH = "P2"
    P3_MEDIUM = "P3"
    P4_LOW = "P4"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class ResponseAction(Base):
    __tablename__ = "response_actions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)

    action = Column(String(255), nullable=False)  # e.g., 'Block Source IP on Perimeter Firewall'
    reason = Column(Text, nullable=False)  # Technical justification
    priority = Column(String(10), default=ActionPriority.P2_HIGH.value, nullable=False)
    risk_level = Column(String(20), default="LOW", nullable=False)  # Operational risk of executing this action
    command_preview = Column(Text, nullable=True)  # Example CLI/iptables/PowerShell command for analyst reference
    
    status = Column(String(30), default=ActionStatus.PROPOSED.value, index=True, nullable=False)
    requires_approval = Column(Boolean, default=True, nullable=False)

    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    incident = relationship("Incident", back_populates="response_actions")
    approved_by = relationship("User", foreign_keys=[approved_by_id])
