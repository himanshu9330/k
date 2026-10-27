"""
SentinelAI-X Incident Response Action Schemas
===============================================
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ResponseActionSchema(BaseModel):
    id: int
    incident_id: int
    action: str
    reason: str
    priority: str
    risk_level: str
    command_preview: Optional[str] = None
    status: str
    requires_approval: bool
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ActionStatusUpdate(BaseModel):
    status: str  # 'APPROVED', 'REJECTED', 'EXECUTED'


ResponseActionStatusUpdate = ActionStatusUpdate
