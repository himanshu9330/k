"""
SentinelAI-X User & Auth Schemas
==================================
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(pattern=r"^[\w\.\+-]+@[\w\.-]+\.\w+$")
    password: str = Field(min_length=6, max_length=128)
    full_name: Optional[str] = None
    role: Optional[str] = "ANALYST"


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


TokenResponse = Token
