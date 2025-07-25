from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models import Participant, Person, Role, School, Tournament
from src.schemas.person import PersonSearchResult
from src.schemas.school import SchoolSearchResult
from src.schemas.tournament import TournamentSearchResult


class SearchService:
    """Service for handling search operations across different models."""

    @staticmethod
    def search_persons(
        db: Session, query: str, limit: int = 10
    ) -> List[PersonSearchResult]:
        """
        Search for persons.search_name based on query.
        For each person match the query this function finds
        the person_id and constructs a PersonSearchResult.
        The PersonSearchResult is the person, with their most
        recent school and year information, plus the roles they have.

        :param db: Database session
        :param query: Search query string
        :param limit: Maximum number of results to return
        :return: List of PersonSearchResult
        """
        search_term = f"%{query.lower()}%"

        person_subquery = (
            db.query(
                Person.person_id,
                Person.search_name,
                Role.role_type,
                Participant.year,
                School.name.label("school_name"),
                Participant.weight_class,
                func.row_number()
                .over(partition_by=Person.person_id, order_by=Participant.year.desc())
                .label("row_number"),
            )
            .join(Role, Person.person_id == Role.person_id)
            .join(Participant, Role.role_id == Participant.role_id)
            .join(School, Participant.school_id == School.school_id)
            .filter(Person.search_name.ilike(search_term))
            .subquery()
        )

        results = (
            db.query(
                person_subquery.c.person_id,
                person_subquery.c.search_name,
                person_subquery.c.role_type,
                person_subquery.c.year,
                person_subquery.c.school_name,
                person_subquery.c.weight_class,
            )
            .filter(person_subquery.c.row_number == 1)
            .limit(limit)
            .all()
        )

        person_results = []
        for result in results:
            # Build metadata: "Wrestler at Iowa State (2023, 165 lbs)"
            current_role = (
                result.role_type.title() if result.role_type else "Participant"
            )
            metadata = f"{current_role} at {result.school_name}"

            if result.year:
                year_info = f" ({result.year}"
                if result.role_type == "wrestler" and result.weight_class:
                    year_info += f", {result.weight_class} lbs"
                year_info += ")"
                metadata += year_info

            person_results.append(
                PersonSearchResult(
                    person_id=result.person_id,
                    search_name=result.search_name,
                    primary_display=result.search_name,
                    metadata=metadata,
                )
            )

        return person_results

    @staticmethod
    def search_schools(
        db: Session, query: str, limit: int = 10
    ) -> List[SchoolSearchResult]:
        """Search for schools"""
        search_term = f"%{query.lower()}%"

        results = (
            db.query(School).filter(School.name.ilike(search_term)).limit(limit).all()
        )

        school_results = []
        for school in results:
            metadata_parts = []
            if school.location:
                metadata_parts.append(school.location)
            if school.school_type:
                metadata_parts.append(school.school_type)

            school_results.append(
                SchoolSearchResult(
                    school_id=school.school_id,
                    name=school.name,
                    primary_display=school.name,
                    metadata=" • ".join(metadata_parts) if metadata_parts else "School",
                )
            )

        return school_results

    @staticmethod
    def search_tournaments(
        db: Session, query: str, limit: int = 10
    ) -> List[TournamentSearchResult]:
        """Search for tournaments"""
        search_term = f"%{query.lower()}%"

        results = (
            db.query(Tournament)
            .filter(Tournament.name.ilike(search_term))
            .limit(limit)
            .all()
        )

        tournament_results = []
        for tournament in results:
            metadata_parts = []
            if tournament.date:
                metadata_parts.append(tournament.date.strftime("%B %d, %Y"))
            if tournament.location:
                metadata_parts.append(tournament.location)

            tournament_results.append(
                TournamentSearchResult(
                    tournament_id=tournament.tournament_id,
                    name=tournament.name,
                    primary_display=tournament.name,
                    metadata=(
                        " • ".join(metadata_parts) if metadata_parts else "Tournament"
                    ),
                )
            )

        return tournament_results
