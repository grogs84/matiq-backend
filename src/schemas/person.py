from datetime import date
from typing import Optional

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

    class Config:
        from_attributes = True


class PersonSearchResult(BaseModel):
    person_id: str
    search_name: str
    primary_display: str
    metadata: str
    result_type: str = "person"
