from pydantic import BaseModel


class TournamentSearchResult(BaseModel):
    tournament_id: str
    slug: str
    name: str
    primary_display: str
    metadata: str
    result_type: str = "tournament"
