from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api import api_router

app = FastAPI(
    title="Matiq API",
    description="A modern web application API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    """Root endpoint"""
    return {"message": "Welcome to Matiq API"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
