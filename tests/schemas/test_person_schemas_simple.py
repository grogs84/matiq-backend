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


class TestPersonSchemas:
    """Test cases for person-related schemas"""
    
    def test_person_base_valid(self):
        """Test PersonBase with valid data"""
        data = {
            "first_name": "David",
            "last_name": "Taylor"
        }
        person = PersonBase(**data)
        assert person.first_name == "David"
        assert person.last_name == "Taylor"
    
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
