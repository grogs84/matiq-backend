import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.main import app
from src.services.profile_service import PersonService
from src.schemas.person import PersonProfileResponse
from src.schemas.person_wrestler import WrestlerStatsResponse, WrestlerMatchesResponse


class TestPersonProfileAPI:
    """Test cases for person profile API endpoints"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_person_data(self):
        return {
            "person_id": "550e8400-e29b-41d4-a716-446655440000",
            "slug": "david-taylor",
            "first_name": "David",
            "last_name": "Taylor",
            "search_name": "david taylor",
            "profile_image_url": None,
            "date_of_birth": "1990-12-05",
            "city_of_origin": "St. Paris",
            "state_of_origin": "OH",
            "roles": [
                {
                    "role_id": "660e8400-e29b-41d4-a716-446655440001",
                    "role_type": "wrestler"
                }
            ]
        }
    
    @patch('src.routers.person.get_db')
    @patch('src.services.profile_service.PersonService.get_person_by_slug')
    def test_get_person_profile_success(self, mock_get_person, mock_get_db, client, sample_person_data):
        """Test successful person profile retrieval"""
        # Arrange
        mock_get_db.return_value = Mock()
        mock_get_person.return_value = sample_person_data
        
        # Act
        response = client.get("/api/v1/person/david-taylor")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "david-taylor"
        assert data["first_name"] == "David"
        assert data["last_name"] == "Taylor"
        assert len(data["roles"]) == 1
        assert data["roles"][0]["role_type"] == "wrestler"
    
    @patch('src.routers.person.get_db')
    @patch('src.services.profile_service.PersonService.get_person_by_slug')
    def test_get_person_profile_not_found(self, mock_get_person, mock_get_db, client):
        """Test person profile not found"""
        # Arrange
        mock_get_db.return_value = Mock()
        mock_get_person.return_value = None
        
        # Act
        response = client.get("/api/v1/person/nonexistent-person")
        
        # Assert
        assert response.status_code == 404
        assert "Person with slug 'nonexistent-person' not found" in response.json()["detail"]
    
    @patch('src.routers.person.get_db')
    @patch('src.services.profile_service.PersonService.get_wrestler_stats')
    def test_get_wrestler_stats_success(self, mock_get_stats, mock_get_db, client):
        """Test successful wrestler stats retrieval"""
        # Arrange
        mock_get_db.return_value = Mock()
        mock_stats_data = {
            "yearly_stats": [
                {
                    "year": 2023,
                    "weight_class": 184,
                    "wins": 15,
                    "placement": 1
                },
                {
                    "year": 2022,
                    "weight_class": 184,
                    "wins": 12,
                    "placement": 2
                }
            ]
        }
        mock_get_stats.return_value = mock_stats_data
        
        # Act
        response = client.get("/api/v1/person/david-taylor/wrestler/stats")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["yearly_stats"]) == 2
        assert data["yearly_stats"][0]["year"] == 2023
        assert data["yearly_stats"][0]["wins"] == 15
        assert data["yearly_stats"][0]["placement"] == 1
    
    @patch('src.routers.person.get_db')
    @patch('src.services.profile_service.PersonService.get_wrestler_matches')
    def test_get_wrestler_matches_success(self, mock_get_matches, mock_get_db, client):
        """Test successful wrestler matches retrieval"""
        # Arrange
        mock_get_db.return_value = Mock()
        mock_matches_data = {
            "matches": [
                {
                    "year": 2023,
                    "weight_class": "184",
                    "round": "Final",
                    "round_order": 1,
                    "wrestler_name": "David Taylor",
                    "wrestler_person_id": "550e8400-e29b-41d4-a716-446655440000",
                    "wrestler_school_name": "Penn State",
                    "is_winner": True,
                    "opponent_name": "John Doe",
                    "opponent_slug": "john-doe",
                    "opponent_person_id": "550e8400-e29b-41d4-a716-446655440001",
                    "opponent_school_name": "Ohio State",
                    "result_type": "Decision",
                    "score": "8-3"
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 20
        }
        mock_get_matches.return_value = mock_matches_data
        
        # Act
        response = client.get("/api/v1/person/david-taylor/wrestler/matches")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["matches"]) == 1
        assert data["matches"][0]["wrestler_name"] == "David Taylor"
        assert data["matches"][0]["is_winner"] is True
        assert data["matches"][0]["opponent_name"] == "John Doe"
    
    @patch('src.routers.person.get_db')
    @patch('src.services.profile_service.PersonService.get_wrestler_matches')
    def test_get_wrestler_matches_with_filters(self, mock_get_matches, mock_get_db, client):
        """Test wrestler matches with year filter"""
        # Arrange
        mock_get_db.return_value = Mock()
        mock_matches_data = {
            "matches": [],
            "total": 0,
            "page": 1,
            "page_size": 10
        }
        mock_get_matches.return_value = mock_matches_data
        
        # Act
        response = client.get("/api/v1/person/david-taylor/wrestler/matches?year=2023&page=1&page_size=10")
        
        # Assert
        assert response.status_code == 200
        # Verify the service was called with correct parameters
        mock_get_matches.assert_called_once()
        call_args = mock_get_matches.call_args
        assert call_args[1]["year"] == 2023
        assert call_args[1]["page"] == 1
        assert call_args[1]["page_size"] == 10
