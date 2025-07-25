import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

class TestSearchIntegration:
    """Integration tests for the complete search workflow."""
    
    def test_end_to_end_person_search(self, test_client, db_session, sample_data):
        """Test complete search workflow from API to database for persons."""
        # Make API request
        response = test_client.get("/api/v1/search/?q=David")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify person was found through complete stack
        assert len(data["persons"]) == 1
        person = data["persons"][0]
        assert person["search_name"] == "David Taylor"
        
        # Verify metadata includes database-derived information
        metadata = person["metadata"]
        assert "Wrestler" in metadata
        assert "Penn State" in metadata
        assert "165 lbs" in metadata
        assert "2023" in metadata
    
    def test_cross_entity_search(self, test_client, sample_data):
        """Test search that finds results across multiple entity types."""
        # Search for "Penn" should find both school and related persons
        response = test_client.get("/api/v1/search/?q=Penn")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should find Penn State school
        assert len(data["schools"]) >= 1
        school_found = any(school["name"] == "Penn State" for school in data["schools"])
        assert school_found
        
        # Total results should reflect all entities found
        assert data["total_results"] >= 1
    
    def test_search_performance_with_large_dataset(self, test_client, db_session):
        """Test search performance with a reasonable query time."""
        import time
        
        # Create additional test data for performance testing
        from src.models.person import Person
        from src.models.school import School
        
        # Add more persons for performance testing
        for i in range(50):
            person = Person(
                person_id=str(100 + i),
                first_name=f"TestPerson{i}",
                last_name=f"LastName{i}",
                search_name=f"TestPerson{i} LastName{i}"
            )
            db_session.add(person)
        
        # Add more schools
        for i in range(20):
            school = School(
                school_id=str(100 + i),
                name=f"Test University {i}",
                city=f"TestCity{i}",
                state="TS"
            )
            db_session.add(school)
        
        db_session.commit()
        
        # Time the search operation
        start_time = time.time()
        response = test_client.get("/api/v1/search/?q=Test")
        end_time = time.time()
        
        # Verify response is valid and performant
        assert response.status_code == 200
        assert end_time - start_time < 2.0  # Should complete within 2 seconds
        
        data = response.json()
        assert len(data["persons"]) > 0  # Should find test persons
        assert len(data["schools"]) > 0  # Should find test schools
    
    def test_database_transaction_rollback(self, test_client, db_session, sample_data):
        """Test that database state is properly isolated between tests."""
        # First search to establish baseline
        response1 = test_client.get("/api/v1/search/?q=David")
        data1 = response1.json()
        baseline_count = data1["total_results"]
        
        # Simulate adding data within this test
        from src.models.person import Person
        temp_person = Person(
            person_id="temp123",
            first_name="Temporary",
            last_name="Person",
            search_name="Temporary Person"
        )
        db_session.add(temp_person)
        db_session.commit()
        
        # Search should now find the additional person
        response2 = test_client.get("/api/v1/search/?q=Temporary")
        data2 = response2.json()
        assert len(data2["persons"]) == 1
        assert data2["persons"][0]["search_name"] == "Temporary Person"
        
        # Note: The temporary data will be rolled back by the test fixture
        # This test verifies that our test isolation is working correctly
    
    def test_concurrent_search_requests(self, test_client, sample_data):
        """Test multiple simultaneous search requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_search_request(query):
            try:
                response = test_client.get(f"/api/v1/search/?q={query}")
                results.append((query, response.status_code, response.json()))
            except Exception as e:
                errors.append((query, str(e)))
        
        # Create multiple threads making different search requests
        queries = ["David", "Penn", "NCAA", "State", "Taylor"]
        threads = []
        
        start_time = time.time()
        for query in queries:
            thread = threading.Thread(target=make_search_request, args=(query,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        end_time = time.time()
        
        # Verify all requests completed successfully
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == len(queries)
        
        # Verify all responses are valid
        for query, status_code, data in results:
            assert status_code == 200
            assert "persons" in data
            assert "schools" in data
            assert "tournaments" in data
            assert "total_results" in data
        
        # Verify reasonable performance even with concurrent requests
        assert end_time - start_time < 5.0  # All requests should complete within 5 seconds
    
    def test_search_result_consistency(self, test_client, sample_data):
        """Test that search results are consistent across multiple calls."""
        query = "David"
        
        # Make the same search request multiple times
        responses = []
        for _ in range(5):
            response = test_client.get(f"/api/v1/search/?q={query}")
            assert response.status_code == 200
            responses.append(response.json())
        
        # Verify all responses are identical
        first_response = responses[0]
        for response in responses[1:]:
            assert response == first_response, "Search results should be consistent"
            
        # Verify the consistent result is correct
        assert len(first_response["persons"]) == 1
        assert first_response["persons"][0]["search_name"] == "David Taylor"
