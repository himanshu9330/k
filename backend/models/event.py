"""
SentinelAI-X Security Event Model
===================================
Stores individual parsed and normalized security events extracted from logs.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    log_id = Column(Integer, ForeignKey("security_logs.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(String(50), nullable=True)
    event_type = Column(String(100), index=True, nullable=False)
    source_ip = Column(String(50), index=True, nullable=True)
    destination_ip = Column(String(50), nullable=True)
    username = Column(String(100), index=True, nullable=True)
    service = Column(String(50), index=True, nullable=True)
    port = Column(Integer, nullable=True)
    status = Column(String(50), nullable=True)  # e.g., 'failed', 'accepted', 'blocked'
    raw_log = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    log = relationship("SecurityLog", back_populates="events")
