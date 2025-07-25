import os
from typing import List

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost:5432/matiq_db"
    )
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:8000"
    ).split(",")

    SUPABASE_URL: str = os.getenv(
        "SUPABASE_URL", "https://your-supabase-url.supabase.co"
    )
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "your-supabase-anon-key")


settings = Settings()
