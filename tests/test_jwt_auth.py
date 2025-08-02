"""
Tests for JWT authentication functionality.

This module tests the Supabase JWT validation system including:
- Token validation and decoding
- User extraction from tokens
- Protected endpoint access
- Error handling for invalid tokens
"""

import pytest
import jwt
from datetime import datetime, timedelta
import httpx
from fastapi import FastAPI, Depends
from unittest.mock import patch, MagicMock

from src.core.auth import (
    decode_jwt,
    extract_user_from_jwt,
    get_current_user,
    get_optional_current_user,
    AuthenticatedUser
)
from src.core.config import settings
from src.main import app


class TestJWTDecoding:
    """Test JWT token decoding and validation."""
    
    def test_decode_valid_jwt(self):
        """Test decoding a valid JWT token."""
        # Create a valid token
        payload = {
            "sub": "user123",
            "email": "test@example.com",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        
        decoded = decode_jwt(token)
        
        assert decoded["sub"] == "user123"
        assert decoded["email"] == "test@example.com"
    
    def test_decode_expired_jwt(self):
        """Test that expired tokens are rejected."""
        # Create an expired token
        payload = {
            "sub": "user123",
            "email": "test@example.com", 
            "iat": datetime.utcnow() - timedelta(hours=2),
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        
        token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        
        with pytest.raises(Exception) as exc_info:
            decode_jwt(token)
        
        assert exc_info.value.status_code == 401
        assert "Token has expired" in exc_info.value.detail
    
    def test_decode_invalid_signature(self):
        """Test that tokens with invalid signatures are rejected."""
        # Create a token with wrong secret
        payload = {
            "sub": "user123",
            "email": "test@example.com",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        token = jwt.encode(payload, "wrong-secret", algorithm=settings.JWT_ALGORITHM)
        
        with pytest.raises(Exception) as exc_info:
            decode_jwt(token)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail
    
    def test_decode_malformed_jwt(self):
        """Test that malformed tokens are rejected."""
        malformed_token = "this.is.not.a.valid.jwt.token"
        
        with pytest.raises(Exception) as exc_info:
            decode_jwt(malformed_token)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail


class TestUserExtraction:
    """Test user information extraction from JWT payload."""
    
    def test_extract_user_valid_payload(self):
        """Test extracting user from valid JWT payload."""
        payload = {
            "sub": "user123",
            "email": "test@example.com",
            "role": "user",
            "iat": datetime.utcnow().timestamp()
        }
        
        user = extract_user_from_jwt(payload)
        
        assert user.user_id == "user123"
        assert user.email == "test@example.com"
        assert user.raw_claims["role"] == "user"
    
    def test_extract_user_missing_sub(self):
        """Test error when 'sub' claim is missing."""
        payload = {
            "email": "test@example.com",
            "iat": datetime.utcnow().timestamp()
        }
        
        with pytest.raises(Exception) as exc_info:
            extract_user_from_jwt(payload)
        
        assert exc_info.value.status_code == 401
        assert "missing user ID" in exc_info.value.detail
    
    def test_extract_user_missing_email(self):
        """Test error when 'email' claim is missing."""
        payload = {
            "sub": "user123",
            "iat": datetime.utcnow().timestamp()
        }
        
        with pytest.raises(Exception) as exc_info:
            extract_user_from_jwt(payload)
        
        assert exc_info.value.status_code == 401
        assert "missing email" in exc_info.value.detail


class TestAuthenticatedEndpoints:
    """Test authentication on protected endpoints."""
    
    def setup_method(self):
        """Set up test client."""
        # Use ASGI transport for testing FastAPI app
        self.transport = httpx.ASGITransport(app=app)
        self.client = httpx.AsyncClient(transport=self.transport, base_url="http://testserver")
        
        # Create a valid test token
        self.valid_payload = {
            "sub": "test-user-123",
            "email": "test@example.com",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        self.valid_token = jwt.encode(
            self.valid_payload, 
            settings.SUPABASE_JWT_SECRET, 
            algorithm=settings.JWT_ALGORITHM
        )
    
    def teardown_method(self):
        """Clean up after each test."""
        # httpx.AsyncClient should be properly closed
        pass
    
    async def test_protected_endpoint_with_valid_token(self):
        """Test accessing protected endpoint with valid token."""
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        response = await self.client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user-123"
        assert data["email"] == "test@example.com"
        assert data["authenticated"] is True
    
    async def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token."""
        response = await self.client.get("/api/v1/auth/me")
        
        # FastAPI returns 403 when no authorization header is provided
        assert response.status_code == 403
        assert "detail" in response.json()
    
    async def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        
        response = await self.client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]
    
    async def test_protected_endpoint_with_expired_token(self):
        """Test accessing protected endpoint with expired token."""
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
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = await self.client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()
    
    async def test_post_endpoint_protection(self):
        """Test that POST endpoints are properly protected."""
        # Test without authentication
        response = await self.client.post("/api/v1/auth/protected-action", json={"action": "test"})
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
        
        # Test with valid authentication
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = await self.client.post(
            "/api/v1/auth/protected-action", 
            headers=headers,
            json={"action": "test"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["performed_by"] == "test@example.com"
        assert data["action_data"]["action"] == "test"
    
    async def test_optional_auth_endpoint_without_token(self):
        """Test optional auth endpoint works without token."""
        response = await self.client.get("/api/v1/auth/public-with-optional-auth")
        
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["user_info"] is None
        assert "premium_data" not in data or data["premium_data"] is None
    
    async def test_optional_auth_endpoint_with_token(self):
        """Test optional auth endpoint provides extra data with token."""
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        response = await self.client.get("/api/v1/auth/public-with-optional-auth", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert "premium_data" in data
        assert data["user_info"]["email"] == "test@example.com"
    
    async def test_malformed_authorization_header(self):
        """Test handling of malformed Authorization headers."""
        headers = {"Authorization": "NotBearer token"}
        
        response = await self.client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 403  # FastAPI returns 403 for malformed auth
    
    async def test_empty_bearer_token(self):
        """Test handling of empty Bearer token."""
        headers = {"Authorization": "Bearer "}
        
        response = await self.client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 403  # FastAPI HTTPBearer rejects empty tokens as 403


class TestJWTConfiguration:
    """Test JWT configuration and environment variables."""
    
    def test_default_configuration(self):
        """Test that default JWT configuration is set."""
        assert hasattr(settings, 'SUPABASE_JWT_SECRET')
        assert hasattr(settings, 'JWT_ALGORITHM')
        assert settings.JWT_ALGORITHM == "HS256"
    
    @patch.dict('os.environ', {'SUPABASE_JWT_SECRET': 'test-secret-key'})
    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        # Note: This test would require reloading settings
        # In practice, environment variables should be set before app startup
        pass


class TestAuthenticatedUserClass:
    """Test the AuthenticatedUser data class."""
    
    def test_authenticated_user_creation(self):
        """Test creating AuthenticatedUser instance."""
        user = AuthenticatedUser(
            user_id="test123",
            email="test@example.com",
            role="admin",
            custom_claim="value"
        )
        
        assert user.user_id == "test123"
        assert user.email == "test@example.com"
        assert user.raw_claims["role"] == "admin"
        assert user.raw_claims["custom_claim"] == "value"