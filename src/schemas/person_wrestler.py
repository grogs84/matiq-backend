from datetime import date
from typing import List, Optional, Any
from pydantic import BaseModel



class WrestlerYearlyStats(BaseModel):
    year: int
    weight_class: int  # Using int since your query casts it to int
    wins: int
    placement: Optional[int] = None  # Can be null
    
    class Config:
        from_attributes = True

class WrestlerStatsResponse(BaseModel):
    yearly_stats: List[WrestlerYearlyStats]

class WrestlerMatchResult(BaseModel):
    year: int
    weight_class: str
    round: str
    round_order: int
    wrestler_name: str
    wrestler_person_id: str
    wrestler_school_name: str
    is_winner: bool
    opponent_name: str
    opponent_slug: str
    opponent_person_id: str
    opponent_school_name: str
    result_type: str
    score: Optional[str] = None
    
    class Config:
        from_attributes = True

class WrestlerMatchesResponse(BaseModel):
    matches: List[WrestlerMatchResult]
    total: int
    page: int
    page_size: int

class PaginatedResponse(BaseModel):
    """Base class for paginated responses"""
    total: int
    page: int
    page_size: int
