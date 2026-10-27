"""
SentinelAI-X Incident Report Entity Model
=========================================
Stores generated CISO Executive Briefings, Technical Incident Reports,
and Compliance Audit Reports.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., 'REP-000001'
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True)
    
    report_type = Column(String(50), default="EXECUTIVE_BRIEFING", nullable=False)  # 'EXECUTIVE_BRIEFING', 'TECHNICAL_FORENSIC', 'COMPLIANCE_AUDIT'
    title = Column(String(255), nullable=False)
    classification = Column(String(50), default="RESTRICTED / SOC INTERNAL", nullable=False)
    
    executive_summary = Column(Text, nullable=False)
    threat_summary = Column(Text, nullable=True)
    mitre_analysis = Column(Text, nullable=True)
    recommended_actions = Column(Text, nullable=True)  # JSON array
    analyst_notes = Column(Text, nullable=True)
    resolution = Column(Text, nullable=True)
    
    generated_by = Column(String(100), default="SentinelAI-X Engine", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)

    # Relationship
    incident = relationship("Incident", back_populates="reports")
