"""
Pydantic Schemas for Threat Intelligence & Indicators of Compromise (IOCs)
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class ThreatIndicatorSchema(BaseModel):
    id: int
    incident_id: Optional[int] = None
    indicator_type: str
    value: str
    threat_type: str
    reputation_score: int
    risk_level: str
    confidence: float
    source: str
    country: Optional[str] = None
    asn: Optional[str] = None
    actor_group: Optional[str] = None
    mitre_technique_id: Optional[str] = None
    details: Optional[str] = None
    first_seen: datetime
    last_seen: datetime

    model_config = ConfigDict(from_attributes=True)


class ThreatLookupRequest(BaseModel):
    indicator: str = Field(..., description="IP, Domain, Hash (MD5/SHA256), or URL to enrich")
    indicator_type: Optional[str] = Field(None, description="Optional type: IP, DOMAIN, HASH, URL")


class ThreatEnrichmentResponse(BaseModel):
    indicator: str
    indicator_type: str
    reputation_score: int  # 0 to 100
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    threat_classification: str
    confidence: float
    source_provenance: str  # e.g., 'DEMO_LOCAL_INTEL', 'COMMUNITY_FEED', 'OTX_INTEGRATION_READY'
    is_malicious: bool
    country: Optional[str] = None
    asn: Optional[str] = None
    actor_group: Optional[str] = None
    mitre_techniques: List[str] = []
    associated_attacks: List[str] = []
    recommended_mitigation: str
    raw_details: Dict[str, Any] = {}
