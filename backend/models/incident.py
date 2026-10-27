"""
SentinelAI-X Incident Entity Model
====================================
Primary unit of work for security operations analysts.
Tracks threat type, severity, risk score, MITRE ATT&CK technique,
AI analysis, lifecycle status, timeline, and investigative steps.
"""

import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class IncidentStatus(str, enum.Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    CONTAINED = "CONTAINED"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class IncidentSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., 'INC-000001'
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    incident_type = Column(String(100), index=True, nullable=False)
    severity = Column(String(20), default=IncidentSeverity.MEDIUM.value, index=True, nullable=False)
    risk_score = Column(Integer, default=0, index=True, nullable=False)
    risk_level = Column(String(20), default="MEDIUM", nullable=False)
    status = Column(String(30), default=IncidentStatus.OPEN.value, index=True, nullable=False)
    
    # Target telemetry
    source_ip = Column(String(50), index=True, nullable=True)
    destination_ip = Column(String(50), nullable=True)
    target_service = Column(String(50), index=True, nullable=True)
    affected_asset = Column(String(100), nullable=True)  # e.g., 'auth-prod-01', 'db-primary'
    target_accounts = Column(Text, nullable=True)  # JSON string array of affected accounts
    failed_attempts = Column(Integer, default=0, nullable=False)

    # MITRE ATT&CK reference
    mitre_technique_id = Column(String(50), ForeignKey("mitre_techniques.technique_id"), nullable=True)
    confidence = Column(Float, default=0.0, nullable=False)

    # AI vs Rule Engine state
    ai_status = Column(String(50), default="COMPLETED", nullable=False)  # 'COMPLETED', 'FALLBACK', 'UNAVAILABLE'
    ai_explanation = Column(Text, nullable=True)
    investigation_steps = Column(Text, nullable=True)  # JSON array of recommended investigation steps
    analyst_notes = Column(Text, nullable=True)  # Free-form analyst notes & triage observations

    # Parent log reference
    log_id = Column(Integer, ForeignKey("security_logs.id"), nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    log = relationship("SecurityLog", back_populates="incidents")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    risk_assessment = relationship("RiskAssessment", back_populates="incident", uselist=False, cascade="all, delete-orphan")
    mitre_technique = relationship("MitreTechnique", foreign_keys=[mitre_technique_id], back_populates="incidents")
    response_actions = relationship("ResponseAction", back_populates="incident", cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="incident", cascade="all, delete-orphan", order_by="TimelineEvent.timestamp")
    threat_indicators = relationship("ThreatIndicator", back_populates="incident")
    reports = relationship("Report", back_populates="incident")
