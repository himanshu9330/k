"""
SentinelAI-X Dashboard & Analytics Schemas
============================================
"""

from typing import List, Dict, Any
from pydantic import BaseModel
from schemas.incident import IncidentResponse


class SeverityCounts(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class StatusCounts(BaseModel):
    open: int = 0
    investigating: int = 0
    contained: int = 0
    resolved: int = 0
    false_positive: int = 0


class KeyMetric(BaseModel):
    name: str
    value: int
    change_pct: float = 0.0


class DashboardSummary(BaseModel):
    total_incidents: int
    severity_breakdown: SeverityCounts
    status_breakdown: StatusCounts
    average_risk_score: float
    total_logs_processed: int
    total_events_normalized: int
    pending_response_actions: int
    recent_incidents: List[IncidentResponse]


class AttackDistributionItem(BaseModel):
    incident_type: str
    count: int
    percentage: float


class MitreDistributionItem(BaseModel):
    technique_id: str
    technique_name: str
    tactic: str
    count: int


class TopTargetItem(BaseModel):
    target: str
    count: int
    service: str


class TopSourceIpItem(BaseModel):
    source_ip: str
    incident_count: int
    failed_attempts: int
    severity: str
