# Supabase JWT Authentication Implementation

This document provides a comprehensive guide to the Supabase JWT authentication system implemented in the MatIQ backend.

## 🔐 Overview

The MatIQ API now includes a complete JWT authentication system that integrates with Supabase to secure endpoints and manage user access. The implementation supports both testing with HS256 tokens and production use with Supabase's RS256 tokens.

## 🏗️ Architecture

### Core Components

```
src/
├── core/
│   ├── auth.py              # JWT validation and user extraction
│   └── config.py            # Authentication configuration
├── dependencies/
│   └── auth.py              # FastAPI authentication dependencies
├── schemas/
│   └── auth.py              # Authentication Pydantic models
└── routers/
    └── auth.py              # Authentication demonstration endpoints
```

### Key Features

- ✅ **JWT Token Validation** - Validates Supabase JWT tokens
- ✅ **Dual Algorithm Support** - RS256 (production) and HS256 (testing)
- ✅ **Protected Routes** - Easy dependency injection for route protection
- ✅ **Optional Authentication** - Public routes with enhanced features for authenticated users
- ✅ **User Information Extraction** - Structured user data from JWT claims
- ✅ **Error Handling** - Comprehensive error responses for authentication failures
- ✅ **Role-Based Access Control** - Foundation for future role-based permissions

## 🚀 Quick Start

### 1. Environment Configuration

Set up your environment variables:

```bash
# Required for production Supabase integration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-supabase-jwt-secret

# Algorithm configuration (defaults to HS256 for testing)
JWT_ALGORITHM=HS256
```

### 2. Install Dependencies

All required dependencies are included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Start the Server

```bash
python -m uvicorn src.main:app --reload
```

### 4. Test Authentication

Run the demo script to test all authentication features:

```bash
python demo_auth.py
```

## 📚 API Endpoints

### Protected Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/me` | GET | Get current user information |
| `/api/v1/auth/token-info` | GET | Get detailed token information |
| `/api/v1/auth/profile` | GET | Get user profile (example) |
| `/api/v1/auth/protected-action` | POST | Perform authenticated action |

### Public Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/public-with-optional-auth` | GET | Public endpoint with optional auth benefits |

## 🔧 Usage Examples

### Protecting a Route

```python
from fastapi import APIRouter, Depends
from src.dependencies.auth import get_current_user, AuthenticatedUser

router = APIRouter()

@router.post("/tournaments")
def create_tournament(
    tournament_data: dict,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """Create a new tournament (requires authentication)."""
    return {
        "message": f"Tournament created by {current_user.email}",
        "creator_id": current_user.user_id,
        "tournament": tournament_data
    }
```

### Optional Authentication

```python
from src.dependencies.auth import optional_user_info, UserResponse

@router.get("/tournaments")
def list_tournaments(
    user_info: UserResponse = Depends(optional_user_info)
):
    """List tournaments (enhanced for authenticated users)."""
    tournaments = get_public_tournaments()
    
    if user_info:
        # Add personalized data for authenticated users
        tournaments.update({
            "personalized_recommendations": get_user_recommendations(user_info.user_id),
            "user_tournaments": get_user_tournaments(user_info.user_id)
        })
    
    return tournaments
```

### Role-Based Access Control

```python
from src.dependencies.auth import require_role

@router.delete("/tournaments/{tournament_id}")
def delete_tournament(
    tournament_id: str,
    admin_user: AuthenticatedUser = Depends(require_role("admin"))
):
    """Delete a tournament (admin only)."""
    return {"message": f"Tournament {tournament_id} deleted by admin {admin_user.email}"}
```

## 🧪 Testing

### Unit Tests

```bash
# Run authentication unit tests
pytest tests/test_jwt_auth.py::TestJWTDecoding -v

# Run all authentication tests
pytest tests/test_jwt_auth.py -v
```

### Manual Testing

1. **Start the server**: `python -m uvicorn src.main:app --reload`
2. **Run demo script**: `python demo_auth.py`
3. **Test with curl**:

```bash
# Create a test token
python -c "
import jwt
from datetime import datetime, timedelta
from src.core.config import settings

token = jwt.encode({
    'sub': 'user123',
    'email': 'user@example.com',
    'exp': datetime.utcnow() + timedelta(hours=1)
}, settings.SUPABASE_JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
print(token)
"

# Test protected endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/auth/me
```

## 🔄 How It Works

### Token Validation Flow

1. **Token Extraction**: Bearer token extracted from `Authorization` header
2. **Algorithm Detection**: System determines whether to use RS256 (Supabase) or HS256 (testing)
3. **Signature Validation**: JWT signature verified using appropriate key
4. **Claims Validation**: Standard claims (exp, iat) validated
5. **User Extraction**: User information extracted and structured
6. **Request Context**: User attached to request for downstream use

### Production vs Testing

- **Production**: Automatically fetches Supabase's public key for RS256 validation
- **Testing**: Uses configured secret for HS256 validation
- **Fallback**: Gracefully falls back to HS256 if Supabase public key unavailable

## 🛡️ Security Features

- **Signature Verification**: All tokens cryptographically verified
- **Expiration Checking**: Expired tokens automatically rejected
- **Error Handling**: Detailed logging with safe error responses
- **HTTPS Ready**: Designed for production HTTPS deployment
- **Role Support**: Foundation for role-based access control

## 🔮 Future Enhancements

The current implementation provides a solid foundation for:

- **Database User Integration**: Link JWT users to database user profiles
- **Advanced Role Management**: Hierarchical role systems
- **Token Refresh**: Automatic token renewal
- **Session Management**: Track user sessions and activity
- **Audit Logging**: Track authenticated actions

## 🐛 Troubleshooting

### Common Issues

1. **"Not authenticated" error**
   - Ensure `Authorization: Bearer TOKEN` header is included
   - Verify token is not expired

2. **"Invalid token" error**
   - Check JWT secret configuration
   - Verify token format and signature

3. **"email-validator not installed"**
   - Run: `pip install email-validator`

4. **Server not starting**
   - Check all dependencies: `pip install -r requirements.txt`
   - Verify environment variables are set

### Debug Mode

Enable debug logging to troubleshoot authentication issues:

```python
import logging
logging.getLogger("src.core.auth").setLevel(logging.DEBUG)
```

## 📖 API Documentation

With the server running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

The interactive documentation includes:
- Authentication requirements for each endpoint
- Request/response schemas
- Example requests with Bearer tokens
- Error response formats

---

This authentication system provides a robust foundation for securing the MatIQ API while maintaining flexibility for future enhancements and easy integration with frontend applications.