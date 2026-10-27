"""
SentinelAI-X Incident Timeline Event Entity Model
=================================================
Tracks chronological events throughout an incident's lifecycle:
Detection -> Investigation -> AI Analysis -> Containment -> Recovery -> Resolution.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class TimelineEvent(Base):
    __tablename__ = "incident_timeline_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
    
    event_type = Column(String(50), nullable=False)  # 'DETECTION', 'INITIAL_INVESTIGATION', 'AI_ANALYSIS', 'THREAT_CONFIRMED', 'CONTAINMENT', 'RECOVERY', 'RESOLUTION', 'NOTE_ADDED'
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    source = Column(String(100), default="SentinelAI-X Engine", nullable=False)
    actor = Column(String(100), default="System", nullable=False)  # 'Rule Engine', 'Gemini AI', 'Security Analyst', 'SOC Admin'
    status_after = Column(String(50), nullable=True)  # Incident status following this event

    # Relationship
    incident = relationship("Incident", back_populates="timeline_events")
