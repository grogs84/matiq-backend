#!/usr/bin/env python3
"""
Entry point for the Matiq API application.
This file imports and runs the FastAPI app from the src package.
"""

if __name__ == "__main__":
    import uvicorn
    from src.main import app
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload for development
    )
