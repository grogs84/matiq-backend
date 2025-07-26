from typing import Optional

from pydantic import BaseModel


class SchoolBase(BaseModel):
    name: str
    location: Optional[str]
    mascot: Optional[str]
    school_type: Optional[str]
    school_url: Optional[str]


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
