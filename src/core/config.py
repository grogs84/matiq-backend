from typing import List

class Settings:
    app_name: str = "Matiq API"
    version: str = "1.0.0"
    api_v1_str: str = "/api/v1"
    
    # CORS settings
    backend_cors_origins: List[str] = ["http://localhost:5173"]
    
    # Database settings (for future use)
    database_url: str = "sqlite:///./matiq.db"

settings = Settings()
