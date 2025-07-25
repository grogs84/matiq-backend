import pytest
from fastapi.testclient import TestClient

class TestSearchRouter:
    
    def test_global_search_with_query(self, test_client, sample_data):
        """Test global search endpoint with query parameter."""
        response = test_client.get("/api/v1/search/?q=David")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "persons" in data
        assert "schools" in data
        assert "tournaments" in data
        assert "total_results" in data
        
        # Check persons results
        assert len(data["persons"]) == 1
        person = data["persons"][0]
        assert person["search_name"] == "David Taylor"
        assert person["person_id"] == "1"
        assert "Wrestler at Penn State" in person["metadata"]
        
        # Check total count
        assert data["total_results"] == 1  # Only David Taylor should match
    
    def test_global_search_with_school_filter(self, test_client, sample_data):
        """Test global search with school filter."""
        response = test_client.get("/api/v1/search/?q=Penn")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find Penn State in schools
        assert len(data["schools"]) == 1
        school = data["schools"][0]
        assert school["name"] == "Penn State"
        assert school["school_id"] == "1"
        
        # Might also find persons from Penn State
        assert data["total_results"] >= 1
    
    def test_global_search_empty_query(self, test_client, sample_data):
        """Test global search with empty query returns limited results."""
        response = test_client.get("/api/v1/search/?q=")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return some results but respect limits
        assert isinstance(data["persons"], list)
        assert isinstance(data["schools"], list)
        assert isinstance(data["tournaments"], list)
        assert len(data["persons"]) <= 5  # Default limit
        assert len(data["schools"]) <= 5
        assert len(data["tournaments"]) <= 5
    
    def test_global_search_no_query_parameter(self, test_client, sample_data):
        """Test global search without query parameter."""
        response = test_client.get("/api/v1/search/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return some results with default behavior
        assert isinstance(data["persons"], list)
        assert isinstance(data["schools"], list) 
        assert isinstance(data["tournaments"], list)
    
    def test_global_search_no_results(self, test_client, sample_data):
        """Test global search with query that matches nothing."""
        response = test_client.get("/api/v1/search/?q=NonExistentSearchTerm12345")
        
        assert response.status_code == 200
        data = response.json()
        
        # All result arrays should be empty
        assert len(data["persons"]) == 0
        assert len(data["schools"]) == 0
        assert len(data["tournaments"]) == 0
        assert data["total_results"] == 0
    
    def test_global_search_special_characters(self, test_client, sample_data):
        """Test global search handles special characters gracefully."""
        # Test with URL-encoded special characters
        response = test_client.get("/api/v1/search/?q=%26%40%23")  # &@#
        
        assert response.status_code == 200
        data = response.json()
        
        # Should not crash and return valid structure
        assert "persons" in data
        assert "schools" in data
        assert "tournaments" in data
        assert "total_results" in data
    
    def test_global_search_very_long_query(self, test_client, sample_data):
        """Test global search with very long query string."""
        long_query = "a" * 1000  # 1000 character query
        response = test_client.get(f"/api/v1/search/?q={long_query}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should handle gracefully and return empty results
        assert data["total_results"] == 0
    
    def test_search_response_schema(self, test_client, sample_data):
        """Test that search response matches expected schema."""
        response = test_client.get("/api/v1/search/?q=David")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate top-level schema
        required_keys = ["persons", "schools", "tournaments", "total_results"]
        for key in required_keys:
            assert key in data
        
        # Validate person result schema if present
        if data["persons"]:
            person = data["persons"][0]
            person_keys = ["search_name", "person_id", "metadata"]
            for key in person_keys:
                assert key in person
            assert isinstance(person["search_name"], str)
            assert isinstance(person["person_id"], str)
            assert isinstance(person["metadata"], str)
        
        # Validate school result schema if present
        if data["schools"]:
            school = data["schools"][0]
            school_keys = ["name", "school_id", "metadata"]
            for key in school_keys:
                assert key in school
        
        # Validate tournament result schema if present
        if data["tournaments"]:
            tournament = data["tournaments"][0]
            tournament_keys = ["name", "tournament_id", "metadata"]
            for key in tournament_keys:
                assert key in tournament
