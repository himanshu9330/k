"""
SentinelAI-X: Generative AI Powered Cybersecurity Incident Detection,
Analysis and Response Platform
========================================================================
Main FastAPI Application Entrypoint.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import init_db, get_db, SessionLocal
from services.seed_service import seed_demo_data_if_empty

# Routers
from routes.auth_routes import router as auth_router
from routes.log_routes import router as log_router
from routes.incident_routes import router as incident_router
from routes.dashboard_routes import router as dashboard_router
from routes.mitre_routes import router as mitre_router
from routes.audit_routes import router as audit_router
from routes.threat_routes import router as threat_router
from routes.copilot_routes import router as copilot_router
from routes.report_routes import router as report_router

# Backwards compatibility services
from services.parser_service import parse_log
from services.gemini_service import analyze_security_events
from services.risk_service import calculate_risk_score


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup and shutdown handler."""
    # Initialize database schema
    init_db()
    
    # Seed initial MITRE techniques and demo incidents if empty
    db = SessionLocal()
    try:
        seed_demo_data_if_empty(db)
    finally:
        db.close()

    yield


app = FastAPI(
    title=settings.PROJECT_TITLE,
    description="Generative AI Powered Cybersecurity Incident Detection, Analysis, Risk Assessment, and Response Platform",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers under /api prefix
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(log_router, prefix=settings.API_V1_PREFIX)
app.include_router(incident_router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)
app.include_router(mitre_router, prefix=settings.API_V1_PREFIX)
app.include_router(threat_router, prefix=settings.API_V1_PREFIX)
app.include_router(copilot_router, prefix=settings.API_V1_PREFIX)
app.include_router(report_router, prefix=settings.API_V1_PREFIX)
app.include_router(audit_router, prefix=settings.API_V1_PREFIX)


# =============================================================================
# Root & Operational Health Endpoints
# =============================================================================

@app.get("/", tags=["Health"])
def root():
    """Root platform discovery endpoint."""
    return {
        "project": settings.PROJECT_NAME,
        "title": settings.PROJECT_TITLE,
        "message": "SentinelAI-X SOC Engine is active and operational 🚀",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_prefix": settings.API_V1_PREFIX
    }


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """System health check endpoint."""
    return {
        "status": "healthy",
        "message": "API is working correctly",
        "model": settings.GEMINI_MODEL,
        "database": "connected"
    }


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Sanitizes unhandled internal exceptions to prevent stack trace leakage."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred during processing. Please verify input data or retry.",
                "details": None
            }
        }
    )