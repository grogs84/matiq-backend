#!/usr/bin/env python3
"""
Example script demonstrating Supabase JWT authentication integration.

This script shows how to:
1. Create test JWT tokens for development
2. Test authentication endpoints
3. Handle authentication errors
4. Use both protected and public endpoints

For production use, replace the test token creation with real Supabase tokens
received from your frontend application.
"""

import jwt
import requests
from datetime import datetime, timedelta
from src.core.config import settings


def create_test_token(user_id: str = "test-user", email: str = "test@example.com", role: str = "user") -> str:
    """
    Create a test JWT token for development purposes.
    
    In production, tokens would be created by Supabase and passed from the frontend.
    """
    payload = {
        "sub": user_id,
        "email": email,
        "iat": datetime.now(),
        "exp": datetime.now() + timedelta(hours=1),
        "role": role,
        "aud": "authenticated"
    }
    
    return jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def test_public_endpoint(base_url: str = "http://localhost:8000"):
    """Test public endpoint without authentication."""
    print("=== Testing Public Endpoint (No Auth) ===")
    
    response = requests.get(f"{base_url}/api/v1/auth/public-with-optional-auth")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data['message']}")
        print(f"   Authenticated: {data['authenticated']}")
        print(f"   Public data: {data['public_data']}")
        print(f"   Premium data: {data.get('premium_data', 'None')}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    print()


def test_public_endpoint_with_auth(token: str, base_url: str = "http://localhost:8000"):
    """Test public endpoint with authentication."""
    print("=== Testing Public Endpoint (With Auth) ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{base_url}/api/v1/auth/public-with-optional-auth", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data['message']}")
        print(f"   Authenticated: {data['authenticated']}")
        print(f"   User: {data['user_info']['email']} (ID: {data['user_info']['user_id']})")
        print(f"   Premium data: {data.get('premium_data', 'None')}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    print()


def test_protected_endpoint(token: str, base_url: str = "http://localhost:8000"):
    """Test protected endpoint requiring authentication."""
    print("=== Testing Protected Endpoint (/me) ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: User authenticated")
        print(f"   User ID: {data['user_id']}")
        print(f"   Email: {data['email']}")
        print(f"   Additional claims: {data['additional_claims']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    print()


def test_token_info(token: str, base_url: str = "http://localhost:8000"):
    """Test token info endpoint."""
    print("=== Testing Token Info Endpoint ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{base_url}/api/v1/auth/token-info", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: Token info retrieved")
        print(f"   User ID: {data['user_id']}")
        print(f"   Email: {data['email']}")
        print(f"   Role: {data.get('role', 'None')}")
        print(f"   Issued at: {data.get('issued_at', 'None')}")
        print(f"   Expires at: {data.get('expires_at', 'None')}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    print()


def test_protected_action(token: str, base_url: str = "http://localhost:8000"):
    """Test protected POST action."""
    print("=== Testing Protected Action (POST) ===")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    action_data = {
        "action": "update_preferences",
        "data": {
            "theme": "dark",
            "notifications": True,
            "favorite_weight_class": "165 lbs"
        }
    }
    
    response = requests.post(f"{base_url}/api/v1/auth/protected-action", 
                           headers=headers, 
                           json=action_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data['message']}")
        print(f"   Performed by: {data['performed_by']}")
        print(f"   Action data: {data['action_data']}")
        print(f"   Timestamp: {data['timestamp']}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
    
    print()


def test_invalid_token(base_url: str = "http://localhost:8000"):
    """Test behavior with invalid token."""
    print("=== Testing Invalid Token ===")
    
    headers = {"Authorization": "Bearer invalid-token-123"}
    response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers)
    
    print(f"Expected error: {response.status_code} - {response.json()['detail']}")
    print()


def test_no_token(base_url: str = "http://localhost:8000"):
    """Test behavior with no token on protected endpoint."""
    print("=== Testing No Token on Protected Endpoint ===")
    
    response = requests.get(f"{base_url}/api/v1/auth/me")
    
    print(f"Expected error: {response.status_code} - {response.json()['detail']}")
    print()


def main():
    """Run all authentication tests."""
    print("🔐 MatIQ JWT Authentication Demo")
    print("=" * 50)
    print()
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not running. Start it with: python -m uvicorn src.main:app --reload")
            return
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Start it with: python -m uvicorn src.main:app --reload")
        return
    
    print("✅ Server is running")
    print()
    
    # Create test token
    token = create_test_token(
        user_id="demo-user-123",
        email="demo@matiq.com",
        role="coach"
    )
    
    print(f"🎫 Test Token: {token[:50]}...")
    print()
    
    # Run tests
    test_public_endpoint()
    test_public_endpoint_with_auth(token)
    test_protected_endpoint(token)
    test_token_info(token)
    test_protected_action(token)
    test_invalid_token()
    test_no_token()
    
    print("🎉 All tests completed!")
    print()
    print("💡 Next Steps:")
    print("   1. Replace test tokens with real Supabase tokens from your frontend")
    print("   2. Configure SUPABASE_URL and SUPABASE_JWT_SECRET environment variables")
    print("   3. For production, the system will automatically use RS256 validation")
    print("   4. Add role-based access control using the require_role dependencies")


if __name__ == "__main__":
    main()