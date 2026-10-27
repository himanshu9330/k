"""
SentinelAI-X MITRE ATT&CK Model
=================================
Stores MITRE enterprise matrix techniques, tactics, descriptions, detection advice,
and mitigation guidance.
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class MitreTechnique(Base):
    __tablename__ = "mitre_techniques"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    technique_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., 'T1110'
    name = Column(String(150), nullable=False)  # e.g., 'Brute Force'
    tactic = Column(String(100), nullable=False)  # e.g., 'Credential Access'
    description = Column(Text, nullable=False)
    detection = Column(Text, nullable=True)
    mitigation = Column(Text, nullable=True)
    url = Column(String(255), nullable=True)

    # Relationships
    incidents = relationship("Incident", back_populates="mitre_technique")
