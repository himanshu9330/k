"""
SentinelAI-X MITRE ATT&CK Schemas
===================================
"""

from typing import Optional
from pydantic import BaseModel


class MitreTechniqueSchema(BaseModel):
    technique_id: str
    name: str
    tactic: str
    description: str
    detection: Optional[str] = None
    mitigation: Optional[str] = None
    url: Optional[str] = None

    class Config:
        from_attributes = True
