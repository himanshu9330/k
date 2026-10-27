"""
SentinelAI-X Security Log Model
=================================
Stores metadata and raw payloads for uploaded log files.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class SecurityLog(Base):
    __tablename__ = "security_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    log_format = Column(String(50), default="generic", nullable=False)
    raw_content = Column(Text, nullable=True)
    event_count = Column(Integer, default=0, nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    events = relationship("SecurityEvent", back_populates="log", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="log")
