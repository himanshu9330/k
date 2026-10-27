"""
Pydantic Schemas for Security Reports
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class ReportCreate(BaseModel):
    incident_id: Optional[str] = None
    report_type: str = "EXECUTIVE_BRIEFING"  # 'EXECUTIVE_BRIEFING', 'TECHNICAL_FORENSIC', 'COMPLIANCE_AUDIT'
    title: Optional[str] = None
    analyst_notes: Optional[str] = None


class ReportResponse(BaseModel):
    id: int
    report_id: str
    incident_id: Optional[int] = None
    report_type: str
    title: str
    classification: str
    executive_summary: str
    threat_summary: Optional[str] = None
    mitre_analysis: Optional[str] = None
    recommended_actions: Optional[str] = None
    analyst_notes: Optional[str] = None
    resolution: Optional[str] = None
    generated_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
