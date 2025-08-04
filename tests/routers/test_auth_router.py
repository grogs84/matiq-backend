"""Tests for authentication router."""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.main import app
from src.schemas.auth import LoginRequest, LoginResponse


class TestAuthRouter:
    """Test cases for authentication router endpoints."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_login_with_valid_credentials(self):
        """Test login endpoint with valid credentials."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Login successful"
        assert data["user_id"] == "mock-user-id-123"
        assert data["access_token"] == "mock-access-token-abc"
    
    def test_login_with_invalid_credentials(self):
        """Test login endpoint with invalid credentials."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["message"] == "Invalid email or password"
        assert data["user_id"] is None
        assert data["access_token"] is None
    
    def test_login_with_missing_email(self):
        """Test login endpoint with missing email field."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "password": "testpassword"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_with_missing_password(self):
        """Test login endpoint with missing password field."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_with_empty_payload(self):
        """Test login endpoint with empty payload."""
        response = self.client.post(
            "/api/v1/auth/login",
            json={}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_with_invalid_json(self):
        """Test login endpoint with invalid JSON."""
        response = self.client.post(
            "/api/v1/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('src.services.auth_service.auth_service.login')
    def test_login_service_exception(self, mock_login):
        """Test login endpoint when service raises an exception."""
        # Mock the service to raise an exception
        mock_login.side_effect = Exception("Service error")
        
        response = self.client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword"
            }
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]