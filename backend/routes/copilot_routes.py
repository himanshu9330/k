"""
SentinelAI-X AI Copilot REST Routes
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from schemas.common import ApiResponse
from schemas.copilot import CopilotChatRequest, CopilotChatResponse, CopilotPromptSuggestion
from services.copilot_service import process_copilot_query, get_copilot_suggestions

router = APIRouter(prefix="/copilot", tags=["AI Copilot"])


@router.post("/chat", response_model=ApiResponse[CopilotChatResponse])
def copilot_chat(req: CopilotChatRequest, db: Session = Depends(get_db)):
    """
    Context-aware investigation assistant.
    Answers analyst inquiries, explains risk scores, provides investigation steps,
    and generates response commands with live incident context.
    """
    result = process_copilot_query(
        message=req.message,
        incident_id=req.incident_id,
        chat_history=req.chat_history,
        db=db
    )
    return ApiResponse(
        data=CopilotChatResponse(**result),
        message="Copilot response generated successfully"
    )


@router.get("/suggestions", response_model=ApiResponse[List[CopilotPromptSuggestion]])
def copilot_suggestions():
    """
    Retrieve recommended investigation prompt suggestions for the analyst.
    """
    suggestions = get_copilot_suggestions()
    return ApiResponse(
        data=[CopilotPromptSuggestion(**s) for s in suggestions],
        message="Prompt suggestions retrieved"
    )
