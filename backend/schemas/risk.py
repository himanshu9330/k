"""
SentinelAI-X Risk Assessment Schemas
======================================
"""

from typing import List, Optional
from pydantic import BaseModel


class RiskFactorSchema(BaseModel):
    name: str
    score: int
    max_score: int
    description: str
    evidence: Optional[str] = None


class RiskAssessmentSchema(BaseModel):
    risk_score: int
    risk_level: str
    base_score: Optional[int] = 0
    frequency_score: Optional[int] = 0
    privilege_score: Optional[int] = 0
    service_score: Optional[int] = 0
    pattern_score: Optional[int] = 0
    confidence_score: Optional[int] = 0
    formula: str
    summary: str
    factors: List[RiskFactorSchema] = []

    class Config:
        from_attributes = True


RiskCalculationResult = RiskAssessmentSchema
