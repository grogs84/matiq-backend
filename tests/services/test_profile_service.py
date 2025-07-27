import pytest
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.services.profile_service import PersonService
from src.models import Person, Role


class TestPersonService:
    """Test cases for PersonService"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_person(self):
        person = Mock()
        person.person_id = "550e8400-e29b-41d4-a716-446655440000"
        person.slug = "david-taylor"
        person.first_name = "David"
        person.last_name = "Taylor"
        person.search_name = "david taylor"
        person.profile_image_url = None
        person.date_of_birth = "1990-12-05"
        person.city_of_origin = "St. Paris"
        person.state_of_origin = "OH"
        return person
    
    @pytest.fixture
    def sample_role(self):
        role = Mock()
        role.role_id = "660e8400-e29b-41d4-a716-446655440001"
        role.role_type = "wrestler"
        return role
    
    def test_get_person_by_slug_success(self, mock_db, sample_person, sample_role):
        """Test successful person retrieval by slug"""
        # Arrange
        mock_db.query.return_value.filter.return_value.first.return_value = sample_person
        mock_db.query.return_value.filter.return_value.all.return_value = [sample_role]
        
        # Act
        result = PersonService.get_person_by_slug(mock_db, "david-taylor")
        
        # Assert
        assert result is not None
        assert result["person_id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert result["slug"] == "david-taylor"
        assert result["first_name"] == "David"
        assert result["last_name"] == "Taylor"
        assert len(result["roles"]) == 1
        assert result["roles"][0]["role_type"] == "wrestler"
    
    def test_get_person_by_slug_not_found(self, mock_db):
        """Test person not found by slug"""
        # Arrange
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = PersonService.get_person_by_slug(mock_db, "nonexistent-person")
        
        # Assert
        assert result is None
    
    def test_get_wrestler_stats_success(self, mock_db):
        """Test successful wrestler stats retrieval"""
        # Arrange
        mock_person_check = Mock()
        mock_person_check.person_id = "550e8400-e29b-41d4-a716-446655440000"
        
        mock_stat_row = Mock()
        mock_stat_row.year = 2023
        mock_stat_row.weight_class = 184
        mock_stat_row.wins = 15
        mock_stat_row.placement = 1
        
        mock_db.execute.side_effect = [
            Mock(first=Mock(return_value=mock_person_check)),  # Person role check
            Mock(fetchall=Mock(return_value=[mock_stat_row]))   # Stats query
        ]
        
        # Act
        result = PersonService.get_wrestler_stats(mock_db, "david-taylor")
        
        # Assert
        assert result is not None
        assert len(result["yearly_stats"]) == 1
        assert result["yearly_stats"][0]["year"] == 2023
        assert result["yearly_stats"][0]["weight_class"] == 184
        assert result["yearly_stats"][0]["wins"] == 15
        assert result["yearly_stats"][0]["placement"] == 1
    
    def test_get_wrestler_stats_no_wrestler_role(self, mock_db):
        """Test wrestler stats when person has no wrestler role"""
        # Arrange
        mock_db.execute.return_value.first.return_value = None
        
        # Act
        result = PersonService.get_wrestler_stats(mock_db, "john-doe")
        
        # Assert
        assert result is None
    
    def test_get_wrestler_matches_success(self, mock_db):
        """Test successful wrestler matches retrieval"""
        # Arrange
        # Mock view exists check
        mock_db.execute.side_effect = [
            Mock(scalar=Mock(return_value=True)),  # View exists
            Mock(first=Mock(return_value=Mock(person_id="test-id"))),  # Person check
            Mock(scalar=Mock(return_value=5)),  # Total count
            Mock(mappings=Mock(return_value=Mock(all=Mock(return_value=[
                {
                    "year": 2023,
                    "weight_class": "184",
                    "round": "Final",
                    "wrestler_name": "David Taylor",
                    "opponent_name": "John Doe",
                    "is_winner": True
                }
            ]))))  # Matches query
        ]
        
        # Act
        result = PersonService.get_wrestler_matches(mock_db, "david-taylor")
        
        # Assert
        assert result["total"] == 5
        assert len(result["matches"]) == 1
        assert result["matches"][0]["wrestler_name"] == "David Taylor"
        assert result["matches"][0]["is_winner"] is True
        assert result["page"] == 1
        assert result["page_size"] == 20
    
    def test_get_wrestler_matches_view_not_exists(self, mock_db):
        """Test wrestler matches when materialized view doesn't exist"""
        # Arrange
        mock_db.execute.return_value.scalar.return_value = False
        
        # Act
        result = PersonService.get_wrestler_matches(mock_db, "david-taylor")
        
        # Assert
        assert result["matches"] == []
        assert result["total"] == 0
        assert result["page"] == 1
        assert result["page_size"] == 20
    
    def test_get_wrestler_matches_no_wrestler_role(self, mock_db):
        """Test wrestler matches when person has no wrestler role"""
        # Arrange
        mock_db.execute.side_effect = [
            Mock(scalar=Mock(return_value=True)),   # View exists
            Mock(first=Mock(return_value=None))     # No wrestler role
        ]
        
        # Act
        result = PersonService.get_wrestler_matches(mock_db, "john-doe")
        
        # Assert
        assert result["matches"] == []
        assert result["total"] == 0
    
    def test_get_wrestler_matches_with_filters(self, mock_db):
        """Test wrestler matches with year filter"""
        # Arrange
        mock_db.execute.side_effect = [
            Mock(scalar=Mock(return_value=True)),  # View exists
            Mock(first=Mock(return_value=Mock(person_id="test-id"))),  # Person check
            Mock(scalar=Mock(return_value=2)),  # Total count
            Mock(mappings=Mock(return_value=Mock(all=Mock(return_value=[]))))  # Matches
        ]
        
        # Act
        result = PersonService.get_wrestler_matches(
            mock_db, 
            "david-taylor", 
            year=2023, 
            page=2, 
            page_size=10
        )
        
        # Assert
        assert result["total"] == 2
        assert result["page"] == 2
        assert result["page_size"] == 10
        
        # Verify SQL was called with filters
        assert mock_db.execute.call_count == 4  # View check, person check, count, data query
    
    def test_get_coach_stats_placeholder(self, mock_db):
        """Test coach stats placeholder method"""
        # Act
        result = PersonService.get_coach_stats(mock_db, "coach-slug")
        
        # Assert
        assert result is None  # Currently returns None (placeholder)
