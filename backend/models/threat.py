"""
SentinelAI-X Threat & Indicator of Compromise (IOC) Model
=========================================================
Tracks actionable indicators (IPs, Domains, Hashes, URLs, Signatures)
and their threat intelligence reputation and enrichment data.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base


class ThreatIndicator(Base):
    __tablename__ = "threat_indicators"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True, index=True)
    
    indicator_type = Column(String(50), nullable=False, index=True)  # 'IP', 'DOMAIN', 'HASH_SHA256', 'HASH_MD5', 'URL', 'SIGNATURE'
    value = Column(String(500), nullable=False, index=True)
    threat_type = Column(String(100), default="Suspicious Activity", nullable=False)
    
    reputation_score = Column(Integer, default=50, nullable=False)  # 0 (Benign) to 100 (Malicious)
    risk_level = Column(String(20), default="MEDIUM", nullable=False)  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    confidence = Column(Float, default=0.85, nullable=False)
    
    # Enrichment metadata
    source = Column(String(100), default="DEMO_LOCAL_INTEL", nullable=False)
    country = Column(String(100), nullable=True)
    asn = Column(String(100), nullable=True)
    actor_group = Column(String(100), nullable=True)
    mitre_technique_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)  # JSON or text description
    
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    incident = relationship("Incident", back_populates="threat_indicators")
