from fastapi import APIRouter
from .v1 import api_router as api_v1_router

api_router = APIRouter()

# Include versioned API routers
api_router.include_router(api_v1_router, prefix="/v1")
