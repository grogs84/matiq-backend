"""
Integration tests for JWT authentication system.

These tests verify the JWT authentication works correctly in
the context of the full application.
"""

import pytest
import jwt
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from src.main import app
from src.core.config import settings


class TestJWTAuthIntegration:
    """Integration tests for JWT authentication."""
    
    def setup_method(self):
        """Set up test client and test tokens."""
        self.client = TestClient(app)
        
        # Valid token for testing
        self.valid_payload = {
            "sub": "integration-test-user",
            "email": "integration@test.com",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1),
            "role": "user"
        }
        self.valid_token = jwt.encode(
            self.valid_payload,
            settings.SUPABASE_JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )
    
    def test_full_authentication_flow(self):
        """Test complete authentication flow from token to user data."""
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        
        # Test /me endpoint
        response = self.client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == "integration-test-user"
        assert data["email"] == "integration@test.com"
        assert data["authenticated"] is True
        assert data["additional_claims"]["role"] == "user"
    
    def test_protected_route_security(self):
        """Test that protected routes properly enforce authentication."""
        # Test without token
        response = self.client.get("/api/v1/auth/profile")
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
        
        # Test with token
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.get("/api/v1/auth/profile", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "Welcome to your profile" in data["message"]
        assert data["email"] == "integration@test.com"
    
    def test_data_modifying_endpoint_protection(self):
        """Test that data-modifying endpoints require authentication."""
        action_data = {"action": "create_resource", "resource_id": "test123"}
        
        # Test POST without authentication
        response = self.client.post("/api/v1/auth/protected-action", json=action_data)
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
        
        # Test POST with authentication
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.post(
            "/api/v1/auth/protected-action",
            headers=headers,
            json=action_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["performed_by"] == "integration@test.com"
        assert data["action_data"]["action"] == "create_resource"
    
    def test_public_endpoint_remains_accessible(self):
        """Test that public endpoints remain accessible without auth."""
        # Existing search endpoint should still work (or fail due to DB, not auth)
        try:
            response = self.client.get("/api/v1/search/?q=test")
            # The endpoint may fail due to database connection issues, but it should not fail due to auth
            # Valid status codes: 200 (success), 500 (DB error), 422 (validation error)
            # Should NOT be 401 or 403 (auth errors)
            assert response.status_code not in [401, 403]
        except Exception as e:
            # If there's a database connection error during the test, that's expected
            # The important thing is that it's not an authentication error
            assert "connection" in str(e).lower() or "operational" in str(e).lower()
    
    def test_optional_auth_behavioral_difference(self):
        """Test that optional auth endpoints behave differently with/without auth."""
        # Without auth
        response = self.client.get("/api/v1/auth/public-with-optional-auth")
        assert response.status_code == 200
        data_public = response.json()
        
        # With auth
        headers = {"Authorization": f"Bearer {self.valid_token}"}
        response = self.client.get("/api/v1/auth/public-with-optional-auth", headers=headers)
        assert response.status_code == 200
        data_auth = response.json()
        
        # Verify different behavior
        assert data_public["authenticated"] is False
        assert data_auth["authenticated"] is True
        assert "premium_data" not in data_public
        assert "premium_data" in data_auth
    
    def test_error_responses_format(self):
        """Test that authentication errors return proper format."""
        # Test with invalid token
        headers = {"Authorization": "Bearer invalid-token"}
        response = self.client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert response.headers.get("WWW-Authenticate") == "Bearer"
    
    def test_token_with_missing_claims(self):
        """Test behavior with tokens missing required claims."""
        # Token missing email
        payload_no_email = {
            "sub": "user123",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token_no_email = jwt.encode(
            payload_no_email,
            settings.SUPABASE_JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )
        
        headers = {"Authorization": f"Bearer {token_no_email}"}
        response = self.client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "missing email" in response.json()["detail"]