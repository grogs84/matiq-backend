from fastapi import APIRouter

from src.routers.search import router as search_router
from src.routers.person import router as person_router

# Future endpoints will be included here

api_router = APIRouter()

api_router.include_router(search_router, prefix="/search", tags=["search"])
api_router.include_router(person_router, tags=["persons"])