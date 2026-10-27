"""
Pydantic Schemas for SentinelAI-X AI Copilot
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CopilotChatRequest(BaseModel):
    message: str = Field(..., description="User's investigation query or instruction")
    incident_id: Optional[str] = Field(None, description="Optional incident ID (e.g. 'INC-000001') to ground response in incident context")
    chat_history: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="Recent conversation turns [{'role': 'user'|'assistant', 'content': '...'}]")


class CopilotChatResponse(BaseModel):
    reply: str
    incident_id: Optional[str] = None
    suggested_followups: List[str] = []
    referenced_evidence: List[str] = []
    mitre_references: List[str] = []
    copilot_mode: str = "CONTEXT_AWARE"  # 'CONTEXT_AWARE', 'GENERAL_SOC', 'FALLBACK'


class CopilotPromptSuggestion(BaseModel):
    id: str
    category: str
    prompt: str
    description: str
