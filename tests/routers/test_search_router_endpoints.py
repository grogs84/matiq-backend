class TestSearchRouter:

    def test_global_search_with_query(self, test_client, sample_data):
        """Test global search endpoint with query parameter."""
        response = test_client.get("/api/v1/search/?q=David")

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "query" in data
        assert "results" in data
        assert "total_results" in data
        assert data["query"] == "David"

        # Check that we have results
        assert len(data["results"]) > 0
        assert data["total_results"] > 0

        # Check that David Taylor is in the results
        person_results = [
            r for r in data["results"] if r.get("result_type") == "person"
        ]
        assert len(person_results) == 1
        person = person_results[0]
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

        # Should find Penn State in schools or persons from Penn State
        school_results = [
            r for r in data["results"] if r.get("result_type") == "school"
        ]

        # Should find at least one result (either school or person from Penn State)
        assert data["total_results"] >= 1

        # If there are school results, check the first one
        if school_results:
            school = school_results[0]
            assert school["name"] == "Penn State"
            assert school["school_id"] == "1"

    def test_global_search_empty_query(self, test_client, sample_data):
        """Test global search with minimal query."""
        response = test_client.get("/api/v1/search/?q=a")  # Use minimal valid query

        assert response.status_code == 200
        data = response.json()

        # Should return some results but respect limits
        assert isinstance(data["results"], list)
        assert data["query"] == "a"
        assert len(data["results"]) <= 20  # Default limit

    def test_global_search_no_query_parameter(self, test_client, sample_data):
        """Test global search without query parameter returns validation error."""
        response = test_client.get("/api/v1/search/")

        # Should return 422 validation error since q parameter is required
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

    def test_global_search_no_results(self, test_client, sample_data):
        """Test global search with query that matches nothing."""
        response = test_client.get("/api/v1/search/?q=NonExistentSearchTerm12345")

        assert response.status_code == 200
        data = response.json()

        # All result arrays should be empty
        assert len(data["results"]) == 0
        assert data["total_results"] == 0

    def test_global_search_special_characters(self, test_client, sample_data):
        """Test global search handles special characters gracefully."""
        # Test with URL-encoded special characters
        response = test_client.get("/api/v1/search/?q=%26%40%23")  # &@#

        assert response.status_code == 200
        data = response.json()

        # Should not crash and return valid structure
        assert "query" in data
        assert "results" in data
        assert "total_results" in data
        assert data["query"] == "&@#"

    def test_global_search_very_long_query(self, test_client, sample_data):
        """Test global search with very long query string."""
        long_query = "a" * 200  # Query longer than max_length=100
        response = test_client.get(f"/api/v1/search/?q={long_query}")

        # Should return 422 validation error due to max_length constraint
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

    def test_search_response_schema(self, test_client, sample_data):
        """Test that search response matches expected schema."""
        response = test_client.get("/api/v1/search/?q=David")

        assert response.status_code == 200
        data = response.json()

        # Validate top-level schema
        required_keys = ["query", "results", "total_results"]
        for key in required_keys:
            assert key in data

        assert data["query"] == "David"
        assert isinstance(data["results"], list)
        assert isinstance(data["total_results"], int)

        # Validate result schema if present
        if data["results"]:
            result = data["results"][0]

            # All results should have these common fields
            common_keys = ["result_type"]
            for key in common_keys:
                assert key in result

            # Validate person result schema if it's a person
            if result.get("result_type") == "person":
                person_keys = ["search_name", "person_id", "metadata"]
                for key in person_keys:
                    assert key in result
                assert isinstance(result["search_name"], str)
                assert isinstance(result["person_id"], str)
                assert isinstance(result["metadata"], str)

            # Validate school result schema if it's a school
            elif result.get("result_type") == "school":
                school_keys = ["name", "school_id", "metadata"]
                for key in school_keys:
                    assert key in result

            # Validate tournament result schema if it's a tournament
            elif result.get("result_type") == "tournament":
                tournament_keys = ["name", "tournament_id", "metadata"]
                for key in tournament_keys:
                    assert key in result
