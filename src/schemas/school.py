from typing import Optional

from pydantic import BaseModel, Field


class SchoolBase(BaseModel):
    name: str
    location: Optional[str]
    mascot: Optional[str]
    school_type: Optional[str]
    school_url: Optional[str]


class SchoolCreate(SchoolBase):
    """Schema for creating a new school."""
    name: str = Field(..., min_length=1, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    mascot: Optional[str] = Field(None, max_length=100)
    school_type: Optional[str] = Field(None, max_length=50)
    school_url: Optional[str] = Field(None, max_length=500)


class SchoolUpdate(BaseModel):
    """Schema for updating school information."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    location: Optional[str] = Field(None, max_length=200)
    mascot: Optional[str] = Field(None, max_length=100)
    school_type: Optional[str] = Field(None, max_length=50)
    school_url: Optional[str] = Field(None, max_length=500)


class SchoolResponse(SchoolBase):
    school_id: str
    slug: str

    class Config:
        from_attributes = True


class SchoolSearchResult(BaseModel):
    school_id: str
    slug: str
    name: str
    primary_display: str
    metadata: str
    result_type: str = "school"
