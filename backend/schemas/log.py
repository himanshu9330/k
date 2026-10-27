"""
SentinelAI-X Log & Security Event Schemas
===========================================
"""

from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel


class SecurityEventSchema(BaseModel):
    id: Optional[int] = None
    timestamp: Optional[str] = None
    event_type: str
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    username: Optional[str] = None
    service: Optional[str] = None
    port: Optional[int] = None
    status: Optional[str] = None
    raw_log: Optional[str] = None

    class Config:
        from_attributes = True


class SecurityLogResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    log_format: str
    event_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class LogUploadResult(BaseModel):
    log_id: int
    filename: str
    file_size: int
    log_format: str
    event_count: int
    events: List[SecurityEventSchema]
    incident_id: Optional[str] = None
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    ai_status: Optional[str] = None


SecurityLogSchema = SecurityLogResponse
LogUploadResponse = LogUploadResult
