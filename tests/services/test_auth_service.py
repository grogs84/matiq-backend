"""Tests for authentication service."""

import pytest
from unittest.mock import patch, MagicMock
import logging

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.services.auth_service import AuthService
from src.schemas.auth import LoginRequest, LoginResponse


class TestAuthService:
    """Test cases for authentication service."""
    
    def setup_method(self):
        """Set up test environment."""
        self.auth_service = AuthService()
    
    @pytest.mark.asyncio
    async def test_login_with_valid_credentials(self):
        """Test login with valid test credentials."""
        login_request = LoginRequest(
            email="test@example.com",
            password="testpassword"
        )
        
        response = await self.auth_service.login(login_request)
        
        assert isinstance(response, LoginResponse)
        assert response.success is True
        assert response.message == "Login successful"
        assert response.user_id == "mock-user-id-123"
        assert response.access_token == "mock-access-token-abc"
    
    @pytest.mark.asyncio
    async def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_request = LoginRequest(
            email="wrong@example.com",
            password="wrongpassword"
        )
        
        response = await self.auth_service.login(login_request)
        
        assert isinstance(response, LoginResponse)
        assert response.success is False
        assert response.message == "Invalid email or password"
        assert response.user_id is None
        assert response.access_token is None
    
    @pytest.mark.asyncio
    async def test_login_with_different_valid_email(self):
        """Test login with different email but wrong password."""
        login_request = LoginRequest(
            email="test@example.com",
            password="wrongpassword"
        )
        
        response = await self.auth_service.login(login_request)
        
        assert isinstance(response, LoginResponse)
        assert response.success is False
        assert response.message == "Invalid email or password"
        assert response.user_id is None
        assert response.access_token is None
    
    @pytest.mark.asyncio
    async def test_login_logging(self, caplog):
        """Test that login attempts are properly logged."""
        with caplog.at_level(logging.INFO):
            login_request = LoginRequest(
                email="test@example.com",
                password="testpassword"
            )
            
            await self.auth_service.login(login_request)
            
            # Check that appropriate log messages were created
            log_messages = [record.message for record in caplog.records]
            assert any("Attempting login for user: test@example.com" in msg for msg in log_messages)
            assert any("Login successful for user: test@example.com" in msg for msg in log_messages)
    
    @pytest.mark.asyncio
    async def test_failed_login_logging(self, caplog):
        """Test that failed login attempts are properly logged."""
        with caplog.at_level(logging.WARNING):
            login_request = LoginRequest(
                email="wrong@example.com",
                password="wrongpassword"
            )
            
            await self.auth_service.login(login_request)
            
            # Check that appropriate log messages were created
            log_messages = [record.message for record in caplog.records]
            assert any("Login failed for user: wrong@example.com - Invalid credentials" in msg for msg in log_messages)
    
    def test_auth_service_initialization(self):
        """Test that auth service initializes properly."""
        auth_service = AuthService()
        assert auth_service is not None
    
    @pytest.mark.asyncio
    async def test_login_response_schema_validation(self):
        """Test that login response follows the expected schema."""
        login_request = LoginRequest(
            email="test@example.com",
            password="testpassword"
        )
        
        response = await self.auth_service.login(login_request)
        
        # Validate response structure
        assert hasattr(response, 'success')
        assert hasattr(response, 'message')
        assert hasattr(response, 'user_id')
        assert hasattr(response, 'access_token')
        
        # Validate types
        assert isinstance(response.success, bool)
        assert isinstance(response.message, str)
        assert isinstance(response.user_id, str) or response.user_id is None
        assert isinstance(response.access_token, str) or response.access_token is None