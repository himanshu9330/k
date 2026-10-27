"""
SentinelAI-X Audit Trail Schemas
==================================
"""

from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel


class AuditLogSchema(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True
