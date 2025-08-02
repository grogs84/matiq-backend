from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid

from src.core.database import get_db
from src.models import Person, Role
from src.schemas.person import (
    PersonProfileResponse, 
    PersonCreate, 
    PersonUpdate, 
    PersonResponse,
    RoleCreate
)
from src.schemas.person_wrestler import WrestlerStatsResponse, WrestlerMatchesResponse
from src.services.profile_service import PersonService
from src.dependencies.auth import require_authenticated_user, get_current_user
from src.core.auth import AuthenticatedUser

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


# Protected endpoints for data modification
@router.post("/", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
def create_person(
    person_data: PersonCreate,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Create a new person (requires authentication).
    
    This endpoint allows authenticated users to create new person records.
    The person will be assigned a unique slug based on their name.
    """
    # Generate unique person_id
    person_id = str(uuid.uuid4())
    
    # Create slug from name (simple implementation)
    slug = f"{person_data.first_name.lower()}-{person_data.last_name.lower()}".replace(" ", "-")
    
    # Check if slug already exists
    existing = db.query(Person).filter(Person.slug == slug).first()
    if existing:
        # Append a number to make it unique
        counter = 1
        while existing:
            new_slug = f"{slug}-{counter}"
            existing = db.query(Person).filter(Person.slug == new_slug).first()
            counter += 1
        slug = new_slug
    
    # Create new person
    new_person = Person(
        person_id=person_id,
        slug=slug,
        first_name=person_data.first_name,
        last_name=person_data.last_name,
        search_name=person_data.search_name or f"{person_data.first_name} {person_data.last_name}",
        date_of_birth=person_data.date_of_birth,
        city_of_origin=person_data.city_of_origin,
        state_of_origin=person_data.state_of_origin
    )
    
    db.add(new_person)
    db.commit()
    db.refresh(new_person)
    
    return PersonResponse(
        person_id=new_person.person_id,
        slug=new_person.slug,
        first_name=new_person.first_name,
        last_name=new_person.last_name,
        search_name=new_person.search_name,
        date_of_birth=new_person.date_of_birth,
        city_of_origin=new_person.city_of_origin,
        state_of_origin=new_person.state_of_origin
    )


@router.put("/{slug}", response_model=PersonResponse)
def update_person(
    slug: str,
    person_data: PersonUpdate,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing person (requires authentication).
    
    This endpoint allows authenticated users to update person information.
    Only provided fields will be updated.
    """
    # Find existing person
    person = db.query(Person).filter(Person.slug == slug).first()
    if not person:
        raise HTTPException(status_code=404, detail=f"Person with slug '{slug}' not found")
    
    # Update provided fields
    update_data = person_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(person, field, value)
    
    # Update search_name if first_name or last_name changed
    if 'first_name' in update_data or 'last_name' in update_data:
        person.search_name = f"{person.first_name} {person.last_name}"
    
    db.commit()
    db.refresh(person)
    
    return PersonResponse(
        person_id=person.person_id,
        slug=person.slug,
        first_name=person.first_name,
        last_name=person.last_name,
        search_name=person.search_name,
        date_of_birth=person.date_of_birth,
        city_of_origin=person.city_of_origin,
        state_of_origin=person.state_of_origin
    )


@router.post("/{slug}/roles", status_code=status.HTTP_201_CREATED)
def assign_role_to_person(
    slug: str,
    role_data: RoleCreate,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Assign a role to a person (requires authentication).
    
    This endpoint allows authenticated users to assign roles (wrestler, coach) to persons.
    """
    # Find the person
    person = db.query(Person).filter(Person.slug == slug).first()
    if not person:
        raise HTTPException(status_code=404, detail=f"Person with slug '{slug}' not found")
    
    # Check if role already exists
    existing_role = db.query(Role).filter(
        Role.person_id == person.person_id,
        Role.role_type == role_data.role_type
    ).first()
    
    if existing_role:
        raise HTTPException(
            status_code=400, 
            detail=f"Person already has role '{role_data.role_type}'"
        )
    
    # Create new role
    new_role = Role(
        role_id=str(uuid.uuid4()),
        person_id=person.person_id,
        role_type=role_data.role_type
    )
    
    db.add(new_role)
    db.commit()
    
    return {
        "message": f"Role '{role_data.role_type}' assigned successfully",
        "person_slug": slug,
        "role_type": role_data.role_type,
        "assigned_by": current_user.email
    }


@router.delete("/{slug}/roles/{role_type}", status_code=status.HTTP_204_NO_CONTENT)
def remove_role_from_person(
    slug: str,
    role_type: str,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Remove a role from a person (requires authentication).
    
    This endpoint allows authenticated users to remove roles from persons.
    """
    # Find the person
    person = db.query(Person).filter(Person.slug == slug).first()
    if not person:
        raise HTTPException(status_code=404, detail=f"Person with slug '{slug}' not found")
    
    # Find the role
    role = db.query(Role).filter(
        Role.person_id == person.person_id,
        Role.role_type == role_type
    ).first()
    
    if not role:
        raise HTTPException(
            status_code=404, 
            detail=f"Person does not have role '{role_type}'"
        )
    
    # Delete the role
    db.delete(role)
    db.commit()
    
    return None  # 204 No Content