"""
SentinelAI-X Risk Engine Compatibility Module
===============================================
Re-exports calculate_risk_score from risk_service to maintain
backwards compatibility across the backend.
"""

from services.risk_service import (
    calculate_risk_score,
    RiskFactorBreakdown,
    RiskAssessmentResult,
    PRIVILEGED_ACCOUNTS,
    SENSITIVE_SERVICES,
    SEVERITY_BASE_SCORES
)

__all__ = [
    "calculate_risk_score",
    "RiskFactorBreakdown",
    "RiskAssessmentResult",
    "PRIVILEGED_ACCOUNTS",
    "SENSITIVE_SERVICES",
    "SEVERITY_BASE_SCORES"
]