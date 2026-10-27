"""
SentinelAI-X Pydantic Schemas Module
====================================
"""

from schemas.common import ApiResponse, ApiErrorResponse, PaginationMeta
from schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from schemas.log import SecurityLogSchema, SecurityEventSchema, LogUploadResponse
from schemas.risk import RiskFactorSchema, RiskAssessmentSchema, RiskCalculationResult
from schemas.mitre import MitreTechniqueSchema
from schemas.response_action import ResponseActionSchema, ResponseActionStatusUpdate
from schemas.incident import (
    IncidentBase,
    IncidentCreate,
    IncidentResponse,
    IncidentDetailResponse,
    IncidentStatusUpdate,
    IncidentNoteAdd
)
from schemas.timeline import TimelineEventSchema, TimelineEventCreate
from schemas.threat import ThreatIndicatorSchema, ThreatLookupRequest, ThreatEnrichmentResponse
from schemas.copilot import CopilotChatRequest, CopilotChatResponse, CopilotPromptSuggestion
from schemas.report import ReportCreate, ReportResponse
from schemas.audit import AuditLogSchema
from schemas.dashboard import (
    DashboardSummary,
    AttackDistributionItem,
    MitreDistributionItem,
    TopSourceIpItem,
    TopTargetItem,
)

__all__ = [
    "ApiResponse",
    "ApiErrorResponse",
    "PaginationMeta",
    "UserRegister",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    "SecurityLogSchema",
    "SecurityEventSchema",
    "LogUploadResponse",
    "RiskFactorSchema",
    "RiskAssessmentSchema",
    "RiskCalculationResult",
    "MitreTechniqueSchema",
    "ResponseActionSchema",
    "ResponseActionStatusUpdate",
    "IncidentBase",
    "IncidentCreate",
    "IncidentResponse",
    "IncidentDetailResponse",
    "IncidentStatusUpdate",
    "IncidentNoteAdd",
    "TimelineEventSchema",
    "TimelineEventCreate",
    "ThreatIndicatorSchema",
    "ThreatLookupRequest",
    "ThreatEnrichmentResponse",
    "CopilotChatRequest",
    "CopilotChatResponse",
    "CopilotPromptSuggestion",
    "ReportCreate",
    "ReportResponse",
    "AuditLogSchema",
    "DashboardSummary",
    "AttackDistributionItem",
    "MitreDistributionItem",
    "TopSourceIpItem",
    "TopTargetItem",
]
