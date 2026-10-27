"""
SentinelAI-X Authentication & User Management Routes
======================================================
Endpoints for user registration, token generation (login),
and profile retrieval with RBAC metadata.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from models.user import User, UserRole
from schemas.user import UserRegister, UserLogin, UserResponse, Token
from schemas.common import ApiResponse, ApiErrorResponse
from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_auth
)
from services.audit_service import log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ApiResponse[UserResponse])
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    """Register a new user account (Default role: ANALYST)."""
    existing_user = db.query(User).filter(
        (User.username == payload.username) | (User.email == payload.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email is already registered"
        )

    # Assign role (default to ANALYST if first user is ADMIN)
    total_users = db.query(User).count()
    assigned_role = UserRole.ADMIN.value if total_users == 0 else (
        payload.role.upper() if payload.role and payload.role.upper() in UserRole.__members__ else UserRole.ANALYST.value
    )

    new_user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=assigned_role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_audit_event(
        db=db,
        action="USER_REGISTRATION",
        entity_type="USER",
        entity_id=str(new_user.id),
        details={"username": new_user.username, "role": new_user.role},
        user=new_user
    )

    return ApiResponse(data=UserResponse.model_validate(new_user), message="User account registered successfully")


@router.post("/login", response_model=ApiResponse[Token])
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    """Authenticate with username and password to obtain JWT access token."""
    user = db.query(User).filter(User.username == payload.username).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    token_str = create_access_token(data={"sub": user.username, "role": user.role})

    log_audit_event(
        db=db,
        action="USER_LOGIN",
        entity_type="AUTH",
        entity_id=str(user.id),
        details={"username": user.username, "role": user.role},
        user=user
    )

    return ApiResponse(
        data=Token(
            access_token=token_str,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        ),
        message="Authentication successful"
    )


@router.get("/me", response_model=ApiResponse[UserResponse])
def get_current_user_profile(current_user: User = Depends(require_auth)):
    """Retrieve profile and role metadata of the authenticated user."""
    return ApiResponse(data=UserResponse.model_validate(current_user), message="Profile retrieved")
