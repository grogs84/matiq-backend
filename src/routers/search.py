from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.schemas.search import GlobalSearchResponse
from src.services.search import SearchService

router = APIRouter()

# Global search endpoint. this endpoint gives api/v1/search/ as the path
# when more search enpoints are added we can modify the get("/") path to something more specific
# for now this is a catch-all for searching across persons, schools, and tournaments
@router.get("/", response_model=GlobalSearchResponse)
def global_search(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results to return"),
    db: Session = Depends(get_db)
) -> GlobalSearchResponse:
    """
    Perform a global search across persons, schools, and tournaments.
    
    :param q: Search query string
    :param limit: Maximum number of results to return
    :param db: Database session dependency
    :return: Global search results
    """
    service = SearchService()

    persons = service.search_persons(db, q, limit)
    schools = service.search_schools(db, q, limit)
    tournaments = service.search_tournaments(db, q, limit)

    # Combine all results
    all_results = persons + schools + tournaments
    
    return GlobalSearchResponse(
        query=q,
        results=all_results,
        total_results=len(all_results)
    )