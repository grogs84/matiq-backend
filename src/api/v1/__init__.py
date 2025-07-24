from fastapi import APIRouter
from .items import router as items_router

api_router = APIRouter()

# Include all route modules
api_router.include_router(items_router, prefix="/items", tags=["items"])
