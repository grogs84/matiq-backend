from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid

from src.core.database import get_db
from src.models.school import School
from src.schemas.school import (
    SchoolResponse, 
    SchoolCreate, 
    SchoolUpdate
)
from src.dependencies.auth import require_authenticated_user, get_current_user
from src.core.auth import AuthenticatedUser

router = APIRouter(
    prefix="/school",
    tags=["school"]
)


@router.get("/{slug}", response_model=SchoolResponse)
def get_school(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get a school by slug.
    
    Returns basic information about the school.
    """
    school = db.query(School).filter(School.slug == slug).first()
    
    if not school:
        raise HTTPException(status_code=404, detail=f"School with slug '{slug}' not found")
    
    return SchoolResponse(
        school_id=school.school_id,
        slug=school.slug,
        name=school.name,
        location=school.location,
        mascot=school.mascot,
        school_type=school.school_type,
        school_url=school.school_url
    )


@router.get("/", response_model=List[SchoolResponse])
def list_schools(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List schools with pagination.
    
    Returns a list of schools with basic information.
    """
    schools = db.query(School).offset(offset).limit(limit).all()
    
    return [
        SchoolResponse(
            school_id=school.school_id,
            slug=school.slug,
            name=school.name,
            location=school.location,
            mascot=school.mascot,
            school_type=school.school_type,
            school_url=school.school_url
        )
        for school in schools
    ]


# Protected endpoints for data modification
@router.post("/", response_model=SchoolResponse, status_code=status.HTTP_201_CREATED)
def create_school(
    school_data: SchoolCreate,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Create a new school (requires authentication).
    
    This endpoint allows authenticated users to create new school records.
    The school will be assigned a unique slug based on its name.
    """
    # Generate unique school_id
    school_id = str(uuid.uuid4())
    
    # Create slug from name (simple implementation)
    slug = school_data.name.lower().replace(" ", "-").replace(".", "").replace(",", "")
    
    # Check if slug already exists
    existing = db.query(School).filter(School.slug == slug).first()
    if existing:
        # Append a number to make it unique
        counter = 1
        while existing:
            new_slug = f"{slug}-{counter}"
            existing = db.query(School).filter(School.slug == new_slug).first()
            counter += 1
        slug = new_slug
    
    # Create new school
    new_school = School(
        school_id=school_id,
        slug=slug,
        name=school_data.name,
        location=school_data.location,
        mascot=school_data.mascot,
        school_type=school_data.school_type,
        school_url=school_data.school_url
    )
    
    db.add(new_school)
    db.commit()
    db.refresh(new_school)
    
    return SchoolResponse(
        school_id=new_school.school_id,
        slug=new_school.slug,
        name=new_school.name,
        location=new_school.location,
        mascot=new_school.mascot,
        school_type=new_school.school_type,
        school_url=new_school.school_url
    )


@router.put("/{slug}", response_model=SchoolResponse)
def update_school(
    slug: str,
    school_data: SchoolUpdate,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing school (requires authentication).
    
    This endpoint allows authenticated users to update school information.
    Only provided fields will be updated.
    """
    # Find existing school
    school = db.query(School).filter(School.slug == slug).first()
    if not school:
        raise HTTPException(status_code=404, detail=f"School with slug '{slug}' not found")
    
    # Update provided fields
    update_data = school_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(school, field, value)
    
    db.commit()
    db.refresh(school)
    
    return SchoolResponse(
        school_id=school.school_id,
        slug=school.slug,
        name=school.name,
        location=school.location,
        mascot=school.mascot,
        school_type=school.school_type,
        school_url=school.school_url
    )


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_school(
    slug: str,
    current_user: AuthenticatedUser = Depends(require_authenticated_user),
    db: Session = Depends(get_db)
):
    """
    Delete a school (requires authentication).
    
    This endpoint allows authenticated users to delete school records.
    This is a permanent operation and should be used with caution.
    """
    # Find the school
    school = db.query(School).filter(School.slug == slug).first()
    if not school:
        raise HTTPException(status_code=404, detail=f"School with slug '{slug}' not found")
    
    # Delete the school
    db.delete(school)
    db.commit()
    
    return None  # 204 No Content
