"""
Pydantic Schemas for Incident Timeline Events
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class TimelineEventCreate(BaseModel):
    event_type: str
    title: str
    description: str
    source: Optional[str] = "Security Analyst"
    actor: Optional[str] = "Analyst"
    status_after: Optional[str] = None


class TimelineEventSchema(BaseModel):
    id: int
    incident_id: int
    timestamp: datetime
    event_type: str
    title: str
    description: str
    source: str
    actor: str
    status_after: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
