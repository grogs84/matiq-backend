from pydantic import BaseModel
from typing import List, Union, Optional

class TournamentSearchResult(BaseModel):
    tournament_id: str
    name: str
    primary_display: str
    metadata: str
    result_type: str = "tournament"