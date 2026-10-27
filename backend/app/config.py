"""
SentinelAI-X Core Configuration Module
========================================
Centralizes environment settings, security keys, database URLs,
and Gemini AI model configurations.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root or backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Settings:
    PROJECT_NAME: str = "SentinelAI-X"
    PROJECT_TITLE: str = "SentinelAI-X: Generative AI Powered Cybersecurity Incident Response System"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'sentinelai.db'}"
    )

    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sentinelai-super-secret-security-key-production-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    # File Ingestion Limits
    MAX_UPLOAD_SIZE_BYTES: int = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(10 * 1024 * 1024)))  # 10 MB
    ALLOWED_EXTENSIONS: set = {".log", ".txt", ".json", ".csv"}


settings = Settings()
