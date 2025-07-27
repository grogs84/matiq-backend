from typing import List, Optional, Dict, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy import func


from src.models import Participant, Person, Role, School, Tournament
from src.schemas.person import PersonSearchResult
from src.schemas.school import SchoolSearchResult
from src.schemas.tournament import TournamentSearchResult
    
class PersonService:
    @staticmethod
    def get_person_by_slug(db: Session, slug: str) -> Optional[Dict[str, Any]]:
        """Basic person info with roles"""
        # Query for the person
        person = db.query(Person).filter(Person.slug == slug).first()
        
        if not person:
            return None
        
        # Query for the person's roles
        roles = db.query(Role).filter(Role.person_id == person.person_id).all()
        
        # Return person data with roles
        return {
            "person_id": person.person_id,
            "slug": person.slug,
            "first_name": person.first_name,
            "last_name": person.last_name,
            "search_name": person.search_name,
            "profile_image_url": getattr(person, "profile_image_url", None),
            "date_of_birth": getattr(person, "date_of_birth", None),
            "city_of_origin": getattr(person, "city_of_origin", None),
            "state_of_origin": getattr(person, "state_of_origin", None),
            "roles": [{"role_id": role.role_id, "role_type": role.role_type} for role in roles]
        }
        
    @staticmethod
    def get_wrestler_stats(db: Session, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get wrestling statistics for a person by year and weight class.
        
        Args:
            db: Database session
            slug: Person slug
            
        Returns:
            Wrestling statistics by year or None if not found
        """
        # Query to check if person exists and has wrestler role
        person_role_check = db.execute(
            text("""
            SELECT p.person_id 
            FROM person p
            JOIN role r ON p.person_id = r.person_id
            WHERE p.slug = :slug AND r.role_type = 'wrestler'
            """),
            {"slug": slug}
        ).first()
        
        if not person_role_check:
            return None
            
        # Execute your stats query
        yearly_stats = db.execute(
            text("""
            with match_history as (
              select *
              from wrestler_match_history mh
              where mh.slug = :slug
            ),
            last_match AS (
              SELECT DISTINCT ON (year, weight_class)
                year,
                weight_class,
                round,
                is_winner
              FROM match_history
              ORDER BY year, weight_class, round_order DESC
            ),
            summary AS (
              SELECT
                participant.year,
                participant.weight_class,
                COUNT(m.match_id) AS matches,
                SUM(pm.is_winner::int) AS wins
              FROM person
              JOIN role ON role.person_id = person.person_id
              JOIN participant ON participant.role_id = role.role_id
              JOIN participant_match pm ON pm.participant_id = participant.participant_id
              JOIN match m ON pm.match_id = m.match_id
              WHERE person.slug = :slug
              GROUP BY participant.year, participant.weight_class
            ),
            year_level as (
            SELECT
              s.year,
              s.weight_class::int,
              s.matches,
              s.wins,
              CASE
                WHEN lm.round IN ('1st', '3rd', '5th', '7th') THEN
                  CASE
                    WHEN lm.is_winner THEN cast(left(lm.round, 1) as int)
                    ELSE CAST(left(lm.round, 1) AS INT) + 1
                  END
                ELSE NULL
              END AS placement
            FROM summary s
            LEFT JOIN last_match lm ON s.year = lm.year AND s.weight_class = lm.weight_class
            ORDER BY s.year, s.weight_class
            )

            select year, weight_class, wins, placement
            from year_level
            """),
            {"slug": slug}
        ).fetchall()
        
        # Format results
        stats_list = []
        for stat in yearly_stats:
            stats_list.append({
                "year": stat.year,
                "weight_class": stat.weight_class,
                "wins": stat.wins,
                "placement": stat.placement
            })
        
        return {
            "yearly_stats": stats_list
        }
            
    @staticmethod
    def get_wrestler_matches(
        db: Session, 
        slug: str, 
        year: Optional[int] = None,
        tournament_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Get match history for a wrestler with pagination and filtering.
        
        Uses the materialized view wrestler_match_history for efficient querying.
        
        Args:
            db: Database session
            slug: Person slug
            year: Optional filter by year
            tournament_id: Optional filter by tournament
            page: Page number
            page_size: Results per page
                
        Returns:
            Paginated match results
        """
        # First check if the materialized view exists
        view_exists = db.execute(
            text("""
            SELECT EXISTS (
                SELECT FROM pg_matviews
                WHERE matviewname = 'wrestler_match_history'
            )
            """)
        ).scalar()
        
        if not view_exists:
            # If view doesn't exist, return empty results
            return {
                "matches": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        
        # Check if person exists and has wrestler role
        person_role_check = db.execute(
            text("""
            SELECT p.person_id 
            FROM person p
            JOIN role r ON p.person_id = r.person_id
            WHERE p.slug = :slug AND r.role_type = 'wrestler'
            """),
            {"slug": slug}
        ).first()
        
        if not person_role_check:
            return {
                "matches": [],
                "total": 0,
                "page": page,
                "page_size": page_size
            }
        
        # Build base query
        base_query = "SELECT * FROM wrestler_match_history WHERE wrestler_slug = :slug"
        params = {"slug": slug}
        
        # Add filters
        if year:
            base_query += " AND year = :year"
            params["year"] = year
            
        if tournament_id:
            base_query += " AND tournament_id = :tournament_id"
            params["tournament_id"] = tournament_id
        
        # Get total count
        count_query = f"SELECT COUNT(*) FROM ({base_query}) AS count_query"
        total = db.execute(text(count_query), params).scalar() or 0
        
        # Add sorting
        query = base_query + " ORDER BY year ASC, round_order ASC"
        
        # Add pagination
        query += " LIMIT :limit OFFSET :offset"
        params["limit"] = page_size
        params["offset"] = (page - 1) * page_size
        
        # Execute query
        result = db.execute(text(query), params)
        matches = result.mappings().all()
        
        # Format results
        match_results = []
        for match in matches:
            match_dict = {}
            for column, value in match.items():
                match_dict[column] = value
            match_results.append(match_dict)
        
        return {
            "matches": match_results,
            "total": total,
            "page": page,
            "page_size": page_size
        }
            
    # Future methods for coach role
    @staticmethod
    def get_coach_stats(db, slug):
        """Coach stats (future)"""
        pass