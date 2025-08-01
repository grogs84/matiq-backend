from datetime import date
from typing import Optional, List

from pydantic import BaseModel, Field


class PersonBase(BaseModel):
    first_name: str
    last_name: str
    search_name: Optional[str]
    date_of_birth: Optional[date]
    city_of_origin: Optional[str]
    state_of_origin: Optional[str]


class PersonCreate(PersonBase):
    """Schema for creating a new person."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    search_name: Optional[str] = Field(None, max_length=200)
    date_of_birth: Optional[date] = None
    city_of_origin: Optional[str] = Field(None, max_length=100)
    state_of_origin: Optional[str] = Field(None, max_length=2)


class PersonUpdate(BaseModel):
    """Schema for updating person information."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    search_name: Optional[str] = Field(None, max_length=200)
    date_of_birth: Optional[date] = None
    city_of_origin: Optional[str] = Field(None, max_length=100)
    state_of_origin: Optional[str] = Field(None, max_length=2)


class PersonResponse(PersonBase):
    person_id: str
    slug: str

    class Config:
        from_attributes = True


class PersonSearchResult(BaseModel):
    person_id: str
    slug: str
    search_name: str
    primary_display: str
    metadata: str
    result_type: str = "person"

# New models for the profile API

class RoleResponse(BaseModel):
    role_id: str  # Changed from int to str for UUID
    role_type: str  # 'wrestler', 'coach', etc.
    
    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    """Schema for creating a role assignment."""
    person_id: str = Field(..., description="Person ID to assign role to")
    role_type: str = Field(
        ..., 
        description="Type of role", 
        pattern="^(wrestler|coach|admin|moderator|editor)$"
    )


class PersonProfileResponse(BaseModel):
    person_id: str  # Changed from int to str for UUID
    slug: str
    first_name: str
    last_name: str
    search_name: str
    profile_image_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    city_of_origin: Optional[str] = None
    state_of_origin: Optional[str] = None
    roles: List[RoleResponse] = []
    school: str  # List of school names

    class Config:
        from_attributes = True


