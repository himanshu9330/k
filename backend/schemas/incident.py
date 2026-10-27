"""
SentinelAI-X Incident Pydantic Schemas
"""

from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict

from schemas.risk import RiskAssessmentSchema
from schemas.mitre import MitreTechniqueSchema
from schemas.response_action import ResponseActionSchema
from schemas.log import SecurityEventSchema
from schemas.timeline import TimelineEventSchema
from schemas.threat import ThreatIndicatorSchema


class IncidentBase(BaseModel):
    title: str
    incident_type: str
    severity: str
    risk_score: int
    risk_level: str
    status: str
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    target_service: Optional[str] = None
    affected_asset: Optional[str] = None
    target_accounts: List[str] = []
    failed_attempts: int = 0
    mitre_technique_id: Optional[str] = None
    confidence: float = 0.0
    ai_status: str = "COMPLETED"


class IncidentCreate(IncidentBase):
    log_id: Optional[int] = None
    ai_explanation: Optional[str] = None
    investigation_steps: List[str] = []


class IncidentStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


class IncidentNoteAdd(BaseModel):
    note: str


class IncidentResponse(IncidentBase):
    id: int
    incident_id: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidentDetailResponse(IncidentResponse):
    ai_explanation: Optional[str] = None
    investigation_steps: List[str] = []
    analyst_notes: Optional[str] = None
    mitre_technique: Optional[MitreTechniqueSchema] = None
    risk_assessment: Optional[RiskAssessmentSchema] = None
    response_actions: List[ResponseActionSchema] = []
    evidence_events: List[SecurityEventSchema] = []
    timeline_events: List[TimelineEventSchema] = []
    threat_indicators: List[ThreatIndicatorSchema] = []

    model_config = ConfigDict(from_attributes=True)
