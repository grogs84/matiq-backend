from fastapi import APIRouter

# Import v1 router (currently empty but ready for endpoints)
from .v1 import api_router as api_v1_router

api_router = APIRouter()

# Include versioned API routers
api_router.include_router(api_v1_router)
