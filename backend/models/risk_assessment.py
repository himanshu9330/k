"""
SentinelAI-X Risk Assessment Entity Model
===========================================
Persists deterministic mathematical score calculations, formula breakdowns,
and individual risk factor weights for an incident.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), unique=True, nullable=False)

    base_score = Column(Integer, default=0, nullable=False)
    frequency_score = Column(Integer, default=0, nullable=False)
    privilege_score = Column(Integer, default=0, nullable=False)
    service_score = Column(Integer, default=0, nullable=False)
    pattern_score = Column(Integer, default=0, nullable=False)
    confidence_score = Column(Integer, default=0, nullable=False)

    final_score = Column(Integer, nullable=False)
    risk_level = Column(String(20), nullable=False)

    formula = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    factors_json = Column(Text, nullable=False)  # Serialized JSON of all detailed factor objects

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    incident = relationship("Incident", back_populates="risk_assessment")
