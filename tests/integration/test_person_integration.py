import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from src.main import app


class TestPersonProfileIntegration:
    """Integration tests for person profile endpoints"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @patch('src.core.database.get_db')
    def test_person_profile_workflow(self, mock_get_db, client):
        """Test complete person profile workflow"""
        # Mock database session
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock person data
        mock_person = Mock()
        mock_person.person_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_person.slug = "david-taylor"
        mock_person.first_name = "David"
        mock_person.last_name = "Taylor"
        mock_person.search_name = "david taylor"
        mock_person.profile_image_url = None
        mock_person.date_of_birth = "1990-12-05"
        mock_person.city_of_origin = "St. Paris"
        mock_person.state_of_origin = "OH"
        
        # Mock role data
        mock_role = Mock()
        mock_role.role_id = "660e8400-e29b-41d4-a716-446655440001"
        mock_role.role_type = "wrestler"
        
        # Configure database mocks
        mock_db.query.return_value.filter.return_value.first.return_value = mock_person
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_role]
        
        # Test person profile endpoint
        response = client.get("/api/v1/person/david-taylor")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "person_id" in data
        assert "slug" in data
        assert "first_name" in data
        assert "last_name" in data
        assert "roles" in data
        
        # Verify data values
        assert data["slug"] == "david-taylor"
        assert data["first_name"] == "David"
        assert data["last_name"] == "Taylor"
        assert len(data["roles"]) == 1
        assert data["roles"][0]["role_type"] == "wrestler"
    
    @patch('src.core.database.get_db')
    def test_wrestler_stats_integration(self, mock_get_db, client):
        """Test wrestler stats endpoint integration"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock person role check
        mock_person_check = Mock()
        mock_person_check.person_id = "550e8400-e29b-41d4-a716-446655440000"
        
        # Mock stats data
        mock_stat = Mock()
        mock_stat.year = 2023
        mock_stat.weight_class = 184
        mock_stat.wins = 15
        mock_stat.placement = 1
        
        # Configure execute calls
        mock_db.execute.side_effect = [
            Mock(first=Mock(return_value=mock_person_check)),  # Person check
            Mock(fetchall=Mock(return_value=[mock_stat]))      # Stats query
        ]
        
        # Test stats endpoint
        response = client.get("/api/v1/person/david-taylor/wrestler/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "yearly_stats" in data
        assert len(data["yearly_stats"]) == 1
        
        # Verify stats data
        stats = data["yearly_stats"][0]
        assert stats["year"] == 2023
        assert stats["weight_class"] == 184
        assert stats["wins"] == 15
        assert stats["placement"] == 1
    
    @patch('src.core.database.get_db')
    def test_wrestler_matches_integration(self, mock_get_db, client):
        """Test wrestler matches endpoint integration"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock database responses
        mock_db.execute.side_effect = [
            Mock(scalar=Mock(return_value=True)),  # View exists
            Mock(first=Mock(return_value=Mock(person_id="test-id"))),  # Person check
            Mock(scalar=Mock(return_value=1)),  # Total count
            Mock(mappings=Mock(return_value=Mock(all=Mock(return_value=[
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
            ]))))
        ]
        
        # Test matches endpoint
        response = client.get("/api/v1/person/david-taylor/wrestler/matches")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "matches" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        
        # Verify pagination
        assert data["total"] == 1
        assert data["page"] == 1
        assert data["page_size"] == 20
        
        # Verify match data
        assert len(data["matches"]) == 1
        match = data["matches"][0]
        assert match["wrestler_name"] == "David Taylor"
        assert match["opponent_name"] == "John Doe"
        assert match["is_winner"] is True
        assert match["score"] == "8-3"
    
    @patch('src.core.database.get_db')
    def test_error_handling_integration(self, mock_get_db, client):
        """Test error handling across endpoints"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Test person not found
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        response = client.get("/api/v1/person/nonexistent-person")
        assert response.status_code == 404
        
        # Test wrestler stats for non-wrestler
        mock_db.execute.return_value.first.return_value = None
        
        response = client.get("/api/v1/person/coach-only-person/wrestler/stats")
        assert response.status_code == 404
        
        # Test matches when view doesn't exist
        mock_db.execute.return_value.scalar.return_value = False
        
        response = client.get("/api/v1/person/david-taylor/wrestler/matches")
        assert response.status_code == 200  # Should return empty results, not error
        data = response.json()
        assert data["matches"] == []
        assert data["total"] == 0


class TestPaginationIntegration:
    """Integration tests for pagination functionality"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @patch('src.core.database.get_db')
    def test_matches_pagination(self, mock_get_db, client):
        """Test matches endpoint pagination"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock responses for pagination test
        mock_db.execute.side_effect = [
            Mock(scalar=Mock(return_value=True)),  # View exists
            Mock(first=Mock(return_value=Mock(person_id="test-id"))),  # Person check
            Mock(scalar=Mock(return_value=50)),  # Total count
            Mock(mappings=Mock(return_value=Mock(all=Mock(return_value=[]))))  # Empty results
        ]
        
        # Test with custom pagination
        response = client.get("/api/v1/person/david-taylor/wrestler/matches?page=2&page_size=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 2
        assert data["page_size"] == 10
        assert data["total"] == 50
    
    @patch('src.core.database.get_db')
    def test_matches_filtering(self, mock_get_db, client):
        """Test matches endpoint filtering"""
        mock_db = Mock()
        mock_get_db.return_value = mock_db
        
        # Mock responses for filtering test
        mock_db.execute.side_effect = [
            Mock(scalar=Mock(return_value=True)),  # View exists
            Mock(first=Mock(return_value=Mock(person_id="test-id"))),  # Person check
            Mock(scalar=Mock(return_value=5)),  # Total count
            Mock(mappings=Mock(return_value=Mock(all=Mock(return_value=[]))))  # Empty results
        ]
        
        # Test with year filter
        response = client.get("/api/v1/person/david-taylor/wrestler/matches?year=2023")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify the service was called with year parameter
        assert data["total"] == 5
