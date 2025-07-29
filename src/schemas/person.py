from datetime import date
from typing import Optional, List

from pydantic import BaseModel


class PersonBase(BaseModel):
    first_name: str
    last_name: str
    search_name: Optional[str]
    date_of_birth: Optional[date]
    city_of_origin: Optional[str]
    state_of_origin: Optional[str]


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


