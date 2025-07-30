# JWT Authentication with Supabase

This document describes the JWT authentication system implemented for the MatIQ backend API.

## Overview

The authentication system integrates with Supabase to validate JWT tokens and protect API endpoints. It provides:

- JWT token validation using Supabase secrets
- User information extraction from tokens
- Protected route enforcement
- Optional authentication for public endpoints

## Configuration

### Environment Variables

The following environment variables configure the JWT authentication:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret

# JWT Algorithm (default: HS256)
JWT_ALGORITHM=HS256
```

### Required Dependencies

Add these to your `requirements.txt`:

```
PyJWT==2.8.0
cryptography==41.0.7
```

## Usage

### Protecting Routes

To protect a route, add the `get_current_user` dependency:

```python
from fastapi import APIRouter, Depends
from src.core.auth import get_current_user, AuthenticatedUser

router = APIRouter()

@router.post("/protected-endpoint")
def protected_action(
    data: dict,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """This endpoint requires authentication."""
    return {
        "message": f"Hello {current_user.email}!",
        "user_id": current_user.user_id,
        "data": data
    }
```

### Optional Authentication

For endpoints that behave differently for authenticated users:

```python
from src.core.auth import get_optional_current_user

@router.get("/public-endpoint")
def public_with_optional_auth(
    current_user: AuthenticatedUser = Depends(get_optional_current_user)
):
    """This endpoint works for both authenticated and anonymous users."""
    if current_user:
        return {"message": f"Welcome back, {current_user.email}!"}
    else:
        return {"message": "Welcome, guest!"}
```

### AuthenticatedUser Object

The `AuthenticatedUser` object contains:

- `user_id`: The user's unique identifier (from JWT 'sub' claim)
- `email`: The user's email address
- `raw_claims`: Dictionary of all JWT claims

```python
def my_endpoint(current_user: AuthenticatedUser = Depends(get_current_user)):
    user_id = current_user.user_id
    email = current_user.email
    role = current_user.raw_claims.get("role")
```

## Authentication Flow

1. **Token Extraction**: The system extracts Bearer tokens from the `Authorization` header
2. **Token Validation**: JWT signature and expiration are validated using the Supabase secret
3. **User Extraction**: User information is extracted from the validated token
4. **Request Context**: User information is attached to the request for downstream use

## API Endpoints

The system includes demonstration endpoints:

### Protected Endpoints

- `GET /api/v1/auth/me` - Get current user information
- `GET /api/v1/auth/profile` - Get user profile (example)
- `POST /api/v1/auth/protected-action` - Perform authenticated action

### Public Endpoints

- `GET /api/v1/auth/public-with-optional-auth` - Public endpoint with optional auth

## Error Responses

The system returns appropriate HTTP status codes:

- `403 Forbidden`: No authorization header provided
- `401 Unauthorized`: Invalid, expired, or malformed token

Example error response:
```json
{
  "detail": "Token has expired"
}
```

## Testing

### Unit Tests

Run the JWT authentication tests:

```bash
pytest tests/test_jwt_auth.py -v
```

### Integration Tests

Run integration tests:

```bash
pytest tests/integration/test_jwt_auth_integration.py -v
```

### Creating Test Tokens

For testing, create valid JWT tokens:

```python
import jwt
from datetime import datetime, timedelta
from src.core.config import settings

payload = {
    "sub": "test-user-123",
    "email": "test@example.com",
    "iat": datetime.utcnow(),
    "exp": datetime.utcnow() + timedelta(hours=1)
}

token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
```

## Security Considerations

1. **Secret Management**: Keep `SUPABASE_JWT_SECRET` secure and never commit it to version control
2. **Token Expiration**: Tokens are validated for expiration automatically
3. **HTTPS Only**: Always use HTTPS in production to protect tokens in transit
4. **Error Handling**: Detailed error messages are logged but not exposed to clients

## Implementation Details

### Core Components

- `src/core/auth.py`: Main authentication module
- `src/core/config.py`: Configuration settings
- `src/routers/auth.py`: Example protected endpoints

### Key Functions

- `decode_jwt()`: Validates and decodes JWT tokens
- `extract_user_from_jwt()`: Extracts user info from token payload
- `get_current_user()`: FastAPI dependency for required authentication
- `get_optional_current_user()`: FastAPI dependency for optional authentication

### Token Requirements

JWT tokens must include:
- `sub`: User ID (required)
- `email`: User email (required)
- `exp`: Expiration timestamp (required)
- `iat`: Issued at timestamp (required)

Additional claims can be included and will be available in `raw_claims`.