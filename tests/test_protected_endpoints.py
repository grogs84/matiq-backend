"""
Tests for protected endpoints and role-based access control.

This module tests the newly implemented protected endpoints for person and school
management, ensuring proper authentication and authorization is enforced.
"""

import pytest
import httpx
import jwt
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

from src.core.config import settings
from src.main import app


class TestProtectedPersonEndpoints:
    """Test protected person management endpoints."""
    
    def setup_method(self):
        """Set up test client and authentication tokens."""
        self.transport = httpx.ASGITransport(app=app)
        self.client = httpx.AsyncClient(transport=self.transport, base_url="http://testserver")
        
        # Create valid test tokens
        self.user_payload = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "role": "user",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        self.user_token = jwt.encode(
            self.user_payload, 
            settings.SUPABASE_JWT_SECRET, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        self.admin_payload = {
            "sub": "admin-user-456",
            "email": "admin@example.com",
            "role": "admin",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        self.admin_token = jwt.encode(
            self.admin_payload, 
            settings.SUPABASE_JWT_SECRET, 
            algorithm=settings.JWT_ALGORITHM
        )
    
    async def test_create_person_requires_authentication(self):
        """Test that creating a person requires authentication."""
        person_data = {
            "first_name": "John",
            "last_name": "Doe",
            "city_of_origin": "New York",
            "state_of_origin": "NY"
        }
        
        # Test without authentication
        response = await self.client.post("/api/v1/person/", json=person_data)
        assert response.status_code == 403
    
    async def test_create_person_with_authentication(self):
        """Test creating a person with valid authentication."""
        person_data = {
            "first_name": "John",
            "last_name": "Doe",
            "city_of_origin": "New York",
            "state_of_origin": "NY"
        }
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        response = await self.client.post("/api/v1/person/", json=person_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert "person_id" in data
        assert "slug" in data
    
    async def test_update_person_requires_authentication(self):
        """Test that updating a person requires authentication."""
        update_data = {
            "first_name": "Jane"
        }
        
        # Test without authentication
        response = await self.client.put("/api/v1/person/john-doe", json=update_data)
        assert response.status_code == 403
    
    async def test_update_person_with_authentication(self):
        """Test updating a person with valid authentication."""
        # First create a person
        person_data = {
            "first_name": "John",
            "last_name": "Doe",
            "city_of_origin": "New York",
            "state_of_origin": "NY"
        }
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        create_response = await self.client.post("/api/v1/person/", json=person_data, headers=headers)
        assert create_response.status_code == 201
        
        created_person = create_response.json()
        slug = created_person["slug"]
        
        # Then update the person
        update_data = {
            "first_name": "Jane"
        }
        
        response = await self.client.put(f"/api/v1/person/{slug}", json=update_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Doe"  # Should remain unchanged
    
    async def test_assign_role_requires_authentication(self):
        """Test that assigning a role requires authentication."""
        role_data = {
            "person_id": "test-person-id",
            "role_type": "wrestler"
        }
        
        # Test without authentication
        response = await self.client.post("/api/v1/person/john-doe/roles", json=role_data)
        assert response.status_code == 403
    
    async def test_assign_role_with_authentication(self):
        """Test assigning a role with valid authentication."""
        # First create a person
        person_data = {
            "first_name": "John",
            "last_name": "Wrestler",
            "city_of_origin": "Chicago",
            "state_of_origin": "IL"
        }
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        create_response = await self.client.post("/api/v1/person/", json=person_data, headers=headers)
        assert create_response.status_code == 201
        
        created_person = create_response.json()
        slug = created_person["slug"]
        person_id = created_person["person_id"]
        
        # Then assign a role
        role_data = {
            "person_id": person_id,
            "role_type": "wrestler"
        }
        
        response = await self.client.post(f"/api/v1/person/{slug}/roles", json=role_data, headers=headers)
        assert response.status_code == 201
        
        data = response.json()
        assert "message" in data
        assert data["role_type"] == "wrestler"
        assert data["assigned_by"] == "test@example.com"
    
    async def test_remove_role_requires_authentication(self):
        """Test that removing a role requires authentication."""
        # Test without authentication
        response = await self.client.delete("/api/v1/person/john-doe/roles/wrestler")
        assert response.status_code == 403
    
    async def test_invalid_token_rejected(self):
        """Test that invalid tokens are rejected."""
        person_data = {
            "first_name": "John",
            "last_name": "Doe"
        }
        
        headers = {"Authorization": "Bearer invalid-token"}
        response = await self.client.post("/api/v1/person/", json=person_data, headers=headers)
        assert response.status_code == 401
    
    async def test_expired_token_rejected(self):
        """Test that expired tokens are rejected."""
        expired_payload = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "iat": datetime.utcnow() - timedelta(hours=2),
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        expired_token = jwt.encode(
            expired_payload, 
            settings.SUPABASE_JWT_SECRET, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        person_data = {
            "first_name": "John",
            "last_name": "Doe"
        }
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await self.client.post("/api/v1/person/", json=person_data, headers=headers)
        assert response.status_code == 401


class TestProtectedSchoolEndpoints:
    """Test protected school management endpoints."""
    
    def setup_method(self):
        """Set up test client and authentication tokens."""
        self.transport = httpx.ASGITransport(app=app)
        self.client = httpx.AsyncClient(transport=self.transport, base_url="http://testserver")
        
        # Create valid test token
        self.user_payload = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "role": "user",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        self.user_token = jwt.encode(
            self.user_payload, 
            settings.SUPABASE_JWT_SECRET, 
            algorithm=settings.JWT_ALGORITHM
        )
    
    async def test_create_school_requires_authentication(self):
        """Test that creating a school requires authentication."""
        school_data = {
            "name": "Test University",
            "location": "Test City, TS",
            "mascot": "Tigers",
            "school_type": "University"
        }
        
        # Test without authentication
        response = await self.client.post("/api/v1/school/", json=school_data)
        assert response.status_code == 403
    
    async def test_create_school_with_authentication(self):
        """Test creating a school with valid authentication."""
        school_data = {
            "name": "Test University",
            "location": "Test City, TS",
            "mascot": "Tigers",
            "school_type": "University"
        }
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        response = await self.client.post("/api/v1/school/", json=school_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test University"
        assert data["location"] == "Test City, TS"
        assert "school_id" in data
        assert "slug" in data
    
    async def test_update_school_requires_authentication(self):
        """Test that updating a school requires authentication."""
        update_data = {
            "mascot": "Bears"
        }
        
        # Test without authentication
        response = await self.client.put("/api/v1/school/test-university", json=update_data)
        assert response.status_code == 403
    
    async def test_update_school_with_authentication(self):
        """Test updating a school with valid authentication."""
        # First create a school
        school_data = {
            "name": "Test University",
            "location": "Test City, TS",
            "mascot": "Tigers",
            "school_type": "University"
        }
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        create_response = await self.client.post("/api/v1/school/", json=school_data, headers=headers)
        assert create_response.status_code == 201
        
        created_school = create_response.json()
        slug = created_school["slug"]
        
        # Then update the school
        update_data = {
            "mascot": "Bears"
        }
        
        response = await self.client.put(f"/api/v1/school/{slug}", json=update_data, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["mascot"] == "Bears"
        assert data["name"] == "Test University"  # Should remain unchanged
    
    async def test_delete_school_requires_authentication(self):
        """Test that deleting a school requires authentication."""
        # Test without authentication
        response = await self.client.delete("/api/v1/school/test-university")
        assert response.status_code == 403
    
    async def test_delete_school_with_authentication(self):
        """Test deleting a school with valid authentication."""
        # First create a school
        school_data = {
            "name": "Test University to Delete",
            "location": "Test City, TS",
            "mascot": "Eagles",
            "school_type": "University"
        }
        
        headers = {"Authorization": f"Bearer {self.user_token}"}
        create_response = await self.client.post("/api/v1/school/", json=school_data, headers=headers)
        assert create_response.status_code == 201
        
        created_school = create_response.json()
        slug = created_school["slug"]
        
        # Then delete the school
        response = await self.client.delete(f"/api/v1/school/{slug}", headers=headers)
        assert response.status_code == 204
        
        # Verify the school is deleted by trying to get it
        get_response = await self.client.get(f"/api/v1/school/{slug}")
        assert get_response.status_code == 404


class TestRoleBasedAccessControl:
    """Test role-based access control features."""
    
    def setup_method(self):
        """Set up test client and role-based tokens."""
        self.transport = httpx.ASGITransport(app=app)
        self.client = httpx.AsyncClient(transport=self.transport, base_url="http://testserver")
        
        # Create tokens for different roles
        self.user_payload = {
            "sub": "user-123",
            "email": "user@example.com",
            "role": "user",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        self.user_token = jwt.encode(
            self.user_payload, 
            settings.SUPABASE_JWT_SECRET, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        self.admin_payload = {
            "sub": "admin-456",
            "email": "admin@example.com",
            "role": "admin",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        self.admin_token = jwt.encode(
            self.admin_payload, 
            settings.SUPABASE_JWT_SECRET, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        self.coach_payload = {
            "sub": "coach-789",
            "email": "coach@example.com",
            "role": "coach",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        self.coach_token = jwt.encode(
            self.coach_payload, 
            settings.SUPABASE_JWT_SECRET, 
            algorithm=settings.JWT_ALGORITHM
        )
    
    async def test_different_roles_can_access_protected_endpoints(self):
        """Test that different roles can access basic protected endpoints."""
        person_data = {
            "first_name": "Test",
            "last_name": "Person",
            "city_of_origin": "Test City",
            "state_of_origin": "TS"
        }
        
        # Test user role
        user_headers = {"Authorization": f"Bearer {self.user_token}"}
        user_response = await self.client.post("/api/v1/person/", json=person_data, headers=user_headers)
        assert user_response.status_code == 201
        
        # Test admin role
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        admin_response = await self.client.post("/api/v1/person/", json=person_data, headers=admin_headers)
        assert admin_response.status_code == 201
        
        # Test coach role
        coach_headers = {"Authorization": f"Bearer {self.coach_token}"}
        coach_response = await self.client.post("/api/v1/person/", json=person_data, headers=coach_headers)
        assert coach_response.status_code == 201
    
    async def test_enhanced_role_types_in_person_roles(self):
        """Test that enhanced role types can be assigned."""
        # First create a person
        person_data = {
            "first_name": "Admin",
            "last_name": "User",
            "city_of_origin": "Admin City",
            "state_of_origin": "AC"
        }
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        create_response = await self.client.post("/api/v1/person/", json=person_data, headers=headers)
        assert create_response.status_code == 201
        
        created_person = create_response.json()
        slug = created_person["slug"]
        person_id = created_person["person_id"]
        
        # Test assigning different role types
        role_types = ["admin", "moderator", "editor", "coach", "wrestler"]
        
        for role_type in role_types:
            role_data = {
                "person_id": person_id,
                "role_type": role_type
            }
            
            response = await self.client.post(f"/api/v1/person/{slug}/roles", json=role_data, headers=headers)
            assert response.status_code == 201
            
            data = response.json()
            assert data["role_type"] == role_type