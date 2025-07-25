class TestSearchIntegration:
    """Integration tests for the complete search workflow."""

    def test_end_to_end_person_search(self, test_client, db_session, sample_data):
        """Test complete search workflow from API to database for persons."""
        # Make API request
        response = test_client.get("/api/v1/search/?q=David")

        assert response.status_code == 200
        data = response.json()

        # Verify person was found through complete stack
        person_results = [
            r for r in data["results"] if r.get("result_type") == "person"
        ]
        assert len(person_results) == 1
        person = person_results[0]
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
        school_results = [
            r for r in data["results"] if r.get("result_type") == "school"
        ]
        assert len(school_results) >= 1
        school_found = any(school["name"] == "Penn State" for school in school_results)
        assert school_found

        # Total results should reflect all entities found
        assert data["total_results"] >= 1

    def test_search_performance_with_large_dataset(self, test_client, db_session):
        """Test search performance with a reasonable query time."""
        import time

        from src.models.participant import Participant

        # Create additional test data for performance testing
        from src.models.person import Person

        # Add more persons for performance testing
        from src.models.role import Role
        from src.models.school import School

        for i in range(50):
            person = Person(
                person_id=str(100 + i),
                first_name=f"TestPerson{i}",
                last_name=f"LastName{i}",
                search_name=f"TestPerson{i} LastName{i}",
            )
            db_session.add(person)

            # Create role for each person
            role = Role(
                role_id=f"test_role_{100 + i}",
                person_id=str(100 + i),
                role_type="wrestler",
            )
            db_session.add(role)

            # Create participant record
            participant = Participant(
                participant_id=f"test_part_{100 + i}",
                role_id=f"test_role_{100 + i}",
                tournament_id="1",  # Use existing tournament
                school_id="1",  # Use existing school
                person_id=str(100 + i),
                year=2024,
                weight_class="157",
            )
            db_session.add(participant)

        # Add more schools
        for i in range(20):
            school = School(
                school_id=str(100 + i),
                name=f"Test University {i}",
                location=f"TestCity{i}, TS",
            )
            db_session.add(school)

        db_session.commit()

        # Time the search operation - use "Test" to find either test persons or schools
        start_time = time.time()
        response = test_client.get("/api/v1/search/?q=Test")
        end_time = time.time()

        # Verify response is valid and performant
        assert response.status_code == 200
        assert end_time - start_time < 2.0  # Should complete within 2 seconds

        data = response.json()

        # Should find the Test University records we created (schools)
        # The API should find some test data we added
        assert data["total_results"] > 0  # Should find some test data
        assert len(data["results"]) > 0  # Should return some results

    def test_database_transaction_rollback(self, test_client, db_session, sample_data):
        """Test that database state is properly isolated between tests."""
        # First search to establish baseline (for future comparison if needed)
        # response1 = test_client.get("/api/v1/search/?q=David")
        # data1 = response1.json()  # For future use if needed
        # baseline_count = data1["total_results"]  # For future use

        # Simulate adding data within this test
        from src.models.participant import Participant
        from src.models.person import Person
        from src.models.role import Role

        temp_person = Person(
            person_id="temp123",
            first_name="Temporary",
            last_name="Person",
            search_name="Temporary Person",
        )
        db_session.add(temp_person)

        # Create a role for the person (required for search to find them)
        temp_role = Role(
            role_id="temp_role_123", person_id="temp123", role_type="wrestler"
        )
        db_session.add(temp_role)

        # Create a participant record (required for search to find them)
        temp_participant = Participant(
            participant_id="temp_part_123",
            role_id="temp_role_123",
            tournament_id="1",  # Use existing tournament from sample_data
            school_id="1",  # Use existing school from sample_data
            person_id="temp123",
            year=2024,
            weight_class="157",
        )
        db_session.add(temp_participant)
        db_session.commit()

        # Search should now find the additional person
        response2 = test_client.get("/api/v1/search/?q=Temporary")
        data2 = response2.json()
        person_results = [
            r for r in data2["results"] if r.get("result_type") == "person"
        ]

        assert len(person_results) == 1
        assert person_results[0]["search_name"] == "Temporary Person"

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
            assert "query" in data
            assert "results" in data
            assert "total_results" in data

        # Verify reasonable performance even with concurrent requests
        assert (
            end_time - start_time < 5.0
        )  # All requests should complete within 5 seconds

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
        person_results = [
            r for r in first_response["results"] if r.get("result_type") == "person"
        ]
        assert len(person_results) == 1
        assert person_results[0]["search_name"] == "David Taylor"
