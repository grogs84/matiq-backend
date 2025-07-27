from src.schemas.person import PersonSearchResult
from src.schemas.school import SchoolSearchResult
from src.schemas.tournament import TournamentSearchResult
from src.services.search import SearchService


class TestSearchService:

    def test_search_persons_found(self, db_session, sample_data):
        """Test searching for persons returns correct results."""
        service = SearchService()

        # Search for "David" should find David Taylor
        results = service.search_persons(db_session, "David", limit=10)

        assert len(results) == 1
        assert isinstance(results[0], PersonSearchResult)
        assert results[0].search_name == "David Taylor"
        assert results[0].person_id == "1"
        assert "Wrestler at Penn State" in results[0].metadata
        assert "2023" in results[0].metadata
        assert "165 lbs" in results[0].metadata

    def test_search_persons_case_insensitive(self, db_session, sample_data):
        """Test search is case insensitive."""
        service = SearchService()

        # Search for "david" (lowercase) should still find David Taylor
        results = service.search_persons(db_session, "david", limit=10)

        assert len(results) == 1
        assert results[0].search_name == "David Taylor"

    def test_search_persons_partial_match(self, db_session, sample_data):
        """Test partial name matching works."""
        service = SearchService()

        # Search for "Tay" should find Taylor
        results = service.search_persons(db_session, "Tay", limit=10)

        assert len(results) == 1
        assert results[0].search_name == "David Taylor"

    def test_search_persons_no_results(self, db_session, sample_data):
        """Test search with no matches returns empty list."""
        service = SearchService()

        results = service.search_persons(db_session, "NonExistent", limit=10)

        assert len(results) == 0
        assert isinstance(results, list)

    def test_search_persons_limit(self, db_session, sample_data):
        """Test search respects limit parameter."""
        service = SearchService()

        # Search for something that matches both persons but limit to 1
        results = service.search_persons(
            db_session, "", limit=1
        )  # Empty search should match all

        assert len(results) <= 1

    def test_search_schools_found(self, db_session, sample_data):
        """Test searching for schools returns correct results."""
        service = SearchService()

        results = service.search_schools(db_session, "Penn", limit=10)

        assert len(results) == 1
        assert isinstance(results[0], SchoolSearchResult)
        assert results[0].name == "Penn State"
        assert results[0].school_id == "1"
        assert "University Park, PA" in results[0].metadata
        assert "University" in results[0].metadata

    def test_search_schools_case_insensitive(self, db_session, sample_data):
        """Test school search is case insensitive."""
        service = SearchService()

        results = service.search_schools(db_session, "penn", limit=10)

        assert len(results) == 1
        assert results[0].name == "Penn State"

    def test_search_tournaments_found(self, db_session, sample_data):
        """Test searching for tournaments returns correct results."""
        service = SearchService()

        results = service.search_tournaments(db_session, "NCAA", limit=10)

        assert len(results) == 1
        assert isinstance(results[0], TournamentSearchResult)
        assert results[0].name == "NCAA Championships"
        assert results[0].tournament_id == "1"
        assert "March 16, 2023" in results[0].metadata
        assert "Tulsa, OK" in results[0].metadata

    def test_search_tournaments_no_results(self, db_session, sample_data):
        """Test tournament search with no matches returns empty list."""
        service = SearchService()

        results = service.search_tournaments(
            db_session, "NonExistentTournament", limit=10
        )

        assert len(results) == 0
        assert isinstance(results, list)
