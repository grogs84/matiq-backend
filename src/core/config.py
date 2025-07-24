from typing import List

class Settings:
    """Application settings"""
    APP_NAME: str = "Matiq API"
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

settings = Settings()
