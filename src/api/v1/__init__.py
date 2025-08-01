from fastapi import APIRouter

from src.routers.search import router as search_router
from src.routers.person import router as person_router
from src.routers.auth import router as auth_router
from src.routers.school import router as school_router

# Future endpoints will be included here

api_router = APIRouter()

api_router.include_router(search_router, prefix="/search", tags=["search"])
api_router.include_router(person_router, tags=["persons"])
api_router.include_router(auth_router, tags=["authentication"])
api_router.include_router(school_router, tags=["schools"])