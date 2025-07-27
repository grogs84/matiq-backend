from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.core.database import get_db
from src.models import Person, Role
from src.schemas.person import PersonProfileResponse
from src.schemas.person_wrestler import WrestlerStatsResponse, WrestlerMatchesResponse
from src.services.profile_service import PersonService

router = APIRouter(
    prefix="/person",
    tags=["person"]
)


@router.get("/{slug}", response_model=PersonProfileResponse)
def get_person_profile(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get a person's profile by slug.
    
    Returns basic information about the person and their roles.
    This serves as the foundation for the tabbed profile interface.
    """
    # Use the PersonService to get person data
    person_data = PersonService.get_person_by_slug(db, slug)
    
    if not person_data:
        raise HTTPException(status_code=404, detail=f"Person with slug '{slug}' not found")
    
    return PersonProfileResponse(**person_data)
    
    return response
    
@router.get("/{slug}/wrestler/stats", response_model=WrestlerStatsResponse)
def get_wrestler_stats(slug: str, db: Session = Depends(get_db)):
    """Get aggregate wrestling statistics"""
    stats = PersonService.get_wrestler_stats(db, slug)
    if not stats:
        raise HTTPException(status_code=404, detail=f"No wrestling stats found for '{slug}'")
    return stats

@router.get("/{slug}/wrestler/matches", response_model=WrestlerMatchesResponse)
def get_wrestler_matches(
    slug: str,
    year: Optional[int] = None,
    tournament_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get match history for a wrestler.
    
    Returns paginated match results with optional filtering by year and tournament.
    Uses the materialized view for optimal performance.
    """
    # First check if person exists
    person = PersonService.get_person_by_slug(db, slug)
    if not person:
        raise HTTPException(status_code=404, detail=f"Person with slug '{slug}' not found")
    
    # Check if person has wrestler role
    if not any(role["role_type"] == "wrestler" for role in person["roles"]):
        raise HTTPException(
            status_code=404, 
            detail=f"Person with slug '{slug}' does not have a wrestler role"
        )
    
    matches = PersonService.get_wrestler_matches(
        db, 
        slug, 
        year=year, 
        tournament_id=tournament_id,
        page=page, 
        page_size=page_size
    )
    return matches