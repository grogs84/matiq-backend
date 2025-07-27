import pytest
from datetime import date
from pydantic import ValidationError

from src.schemas.person import (
    PersonBase, 
    PersonResponse, 
    PersonSearchResult, 
    PersonProfileResponse, 
    RoleResponse
)
from src.schemas.person_wrestler import (
    WrestlerYearlyStats,
    WrestlerStatsResponse,
    WrestlerMatchResult,
    WrestlerMatchesResponse
)


class TestPersonSchemas:
    """Test cases for person-related schemas"""
    
    def test_person_base_valid(self):
        """Test PersonBase with valid data"""
        data = {
            "first_name": "David",
            "last_name": "Taylor",
            "search_name": "david taylor",
            "date_of_birth": "1990-12-05",
            "city_of_origin": "St. Paris",
            "state_of_origin": "OH"
        }
        person = PersonBase(**data)
        assert person.first_name == "David"
        assert person.last_name == "Taylor"
        assert person.search_name == "david taylor"
        assert person.date_of_birth == date(1990, 12, 5)
    
    def test_person_base_optional_fields(self):
        """Test PersonBase with only required fields"""
        data = {
            "first_name": "John",
            "last_name": "Doe"
        }
        person = PersonBase(**data)
        assert person.first_name == "John"
        assert person.last_name == "Doe"
        assert person.search_name is None
        assert person.date_of_birth is None
    
    def test_person_response_valid(self):
        """Test PersonResponse with valid data"""
        data = {
            "person_id": "550e8400-e29b-41d4-a716-446655440000",
            "slug": "david-taylor",
            "first_name": "David",
            "last_name": "Taylor"
        }
        person = PersonResponse(**data)
        assert person.person_id == "550e8400-e29b-41d4-a716-446655440000"
        assert person.slug == "david-taylor"
    
    def test_person_search_result_valid(self):
        """Test PersonSearchResult with valid data"""
        data = {
            "person_id": "550e8400-e29b-41d4-a716-446655440000",
            "slug": "david-taylor",
            "search_name": "david taylor",
            "primary_display": "David Taylor",
            "metadata": "Penn State Wrestling"
        }
        result = PersonSearchResult(**data)
        assert result.result_type == "person"  # Default value
        assert result.primary_display == "David Taylor"
    
    def test_role_response_valid(self):
        """Test RoleResponse with valid data"""
        data = {
            "role_id": "660e8400-e29b-41d4-a716-446655440001",
            "role_type": "wrestler"
        }
        role = RoleResponse(**data)
        assert role.role_id == "660e8400-e29b-41d4-a716-446655440001"
        assert role.role_type == "wrestler"
    
    def test_person_profile_response_valid(self):
        """Test PersonProfileResponse with valid data"""
        data = {
            "person_id": "550e8400-e29b-41d4-a716-446655440000",
            "slug": "david-taylor",
            "first_name": "David",
            "last_name": "Taylor",
            "search_name": "david taylor",
            "roles": [
                {
                    "role_id": "660e8400-e29b-41d4-a716-446655440001",
                    "role_type": "wrestler"
                }
            ]
        }
        profile = PersonProfileResponse(**data)
        assert profile.person_id == "550e8400-e29b-41d4-a716-446655440000"
        assert len(profile.roles) == 1
        assert profile.roles[0].role_type == "wrestler"
    
    def test_person_profile_response_empty_roles(self):
        """Test PersonProfileResponse with empty roles"""
        data = {
            "person_id": "550e8400-e29b-41d4-a716-446655440000",
            "slug": "john-doe",
            "first_name": "John",
            "last_name": "Doe",
            "search_name": "john doe"
        }
        profile = PersonProfileResponse(**data)
        assert len(profile.roles) == 0


class TestWrestlerSchemas:
    """Test cases for wrestler-related schemas"""
    
    def test_wrestler_yearly_stats_valid(self):
        """Test WrestlerYearlyStats with valid data"""
        data = {
            "year": 2023,
            "weight_class": 184,
            "wins": 15,
            "placement": 1
        }
        stats = WrestlerYearlyStats(**data)
        assert stats.year == 2023
        assert stats.weight_class == 184
        assert stats.wins == 15
        assert stats.placement == 1
    
    def test_wrestler_yearly_stats_no_placement(self):
        """Test WrestlerYearlyStats without placement"""
        data = {
            "year": 2023,
            "weight_class": 184,
            "wins": 15
        }
        stats = WrestlerYearlyStats(**data)
        assert stats.placement is None
    
    def test_wrestler_stats_response_valid(self):
        """Test WrestlerStatsResponse with valid data"""
        data = {
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
        response = WrestlerStatsResponse(**data)
        assert len(response.yearly_stats) == 2
        assert response.yearly_stats[0].year == 2023
        assert response.yearly_stats[1].year == 2022
    
    def test_wrestler_match_result_valid(self):
        """Test WrestlerMatchResult with valid data"""
        data = {
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
        match = WrestlerMatchResult(**data)
        assert match.wrestler_name == "David Taylor"
        assert match.is_winner is True
        assert match.opponent_name == "John Doe"
        assert match.score == "8-3"
    
    def test_wrestler_match_result_no_score(self):
        """Test WrestlerMatchResult without score"""
        data = {
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
            "result_type": "Pin"
        }
        match = WrestlerMatchResult(**data)
        assert match.score is None
    
    def test_wrestler_matches_response_valid(self):
        """Test WrestlerMatchesResponse with valid data"""
        data = {
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
        response = WrestlerMatchesResponse(**data)
        assert len(response.matches) == 1
        assert response.total == 1
        assert response.page == 1
        assert response.page_size == 20
    
    def test_wrestler_matches_response_empty(self):
        """Test WrestlerMatchesResponse with no matches"""
        data = {
            "matches": [],
            "total": 0,
            "page": 1,
            "page_size": 20
        }
        response = WrestlerMatchesResponse(**data)
        assert len(response.matches) == 0
        assert response.total == 0


class TestSchemaValidation:
    """Test schema validation edge cases"""
    
    def test_invalid_person_id_type(self):
        """Test validation fails for invalid person_id type"""
        with pytest.raises(ValidationError):
            PersonResponse(
                person_id=123,  # Should be string
                slug="test-slug",
                first_name="Test",
                last_name="User"
            )
    
    def test_invalid_date_format(self):
        """Test validation fails for invalid date format"""
        with pytest.raises(ValidationError):
            PersonBase(
                first_name="Test",
                last_name="User",
                date_of_birth="invalid-date"
            )
    
    def test_missing_required_fields(self):
        """Test validation fails for missing required fields"""
        with pytest.raises(ValidationError):
            WrestlerMatchResult(
                year=2023,
                # Missing required fields
                weight_class="184"
            )
