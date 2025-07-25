from pydantic import BaseModel
from typing import List, Union, Optional
from .person import PersonSearchResult
from .school import SchoolSearchResult
from .tournament import TournamentSearchResult

class GlobalSearchResponse(BaseModel):
    """Response schema for global search results."""
    
    query: str
    results: List[Union[PersonSearchResult, SchoolSearchResult, TournamentSearchResult]]
    total_results: int

class SearchFilters(BaseModel):
    person_state: Optional[str] = None
    role_type: Optional[str] = None
    school_type: Optional[str] = None
    tournament_year: Optional[int] = None