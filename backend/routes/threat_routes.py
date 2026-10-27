"""
SentinelAI-X Threat Intelligence & IOC REST Routes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from models.threat import ThreatIndicator
from schemas.common import ApiResponse
from schemas.threat import ThreatLookupRequest, ThreatEnrichmentResponse, ThreatIndicatorSchema
from services.threat_service import enrich_indicator

router = APIRouter(prefix="/threats", tags=["Threat Intelligence"])


@router.post("/lookup", response_model=ApiResponse[ThreatEnrichmentResponse])
def lookup_threat_indicator(req: ThreatLookupRequest):
    """
    Enrich an IP address, domain, file hash, or URL with reputation scores,
    threat classifications, and MITRE ATT&CK techniques.
    """
    data = enrich_indicator(req.indicator, req.indicator_type)
    return ApiResponse(
        data=ThreatEnrichmentResponse(**data),
        message=f"Threat intelligence enrichment completed for {req.indicator}"
    )


@router.get("/indicators", response_model=ApiResponse[List[ThreatIndicatorSchema]])
def list_threat_indicators(
    indicator_type: Optional[str] = Query(None, description="Filter by type: IP, DOMAIN, HASH_MD5, HASH_SHA256, URL"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    List all active Indicators of Compromise (IOCs) recorded across security incidents.
    """
    query = db.query(ThreatIndicator)
    if indicator_type:
        query = query.filter(ThreatIndicator.indicator_type == indicator_type.upper())
    
    indicators = query.order_by(desc(ThreatIndicator.last_seen)).limit(limit).all()
    return ApiResponse(
        data=[ThreatIndicatorSchema.model_validate(i) for i in indicators],
        message="Threat indicators retrieved successfully"
    )
