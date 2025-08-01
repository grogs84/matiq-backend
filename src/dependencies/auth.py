"""
Authentication dependencies for FastAPI route protection.

This module provides dependency injection functions for protecting routes
with Supabase JWT authentication. It re-exports the core authentication
functions and provides additional convenience dependencies.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.core.auth import (
    get_current_user as _get_current_user,
    get_optional_current_user as _get_optional_current_user,
    AuthenticatedUser,
    decode_jwt,
    extract_user_from_jwt
)
from src.schemas.auth import UserResponse, TokenInfo


# Re-export core authentication dependencies
get_current_user = _get_current_user
get_optional_current_user = _get_optional_current_user


def require_authenticated_user(
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> AuthenticatedUser:
    """
    Dependency that ensures a user is authenticated.
    
    This is an alias for get_current_user but with a more explicit name
    for routes that absolutely require authentication.
    
    Args:
        current_user: Injected authenticated user
        
    Returns:
        AuthenticatedUser instance
        
    Raises:
        HTTPException: 401 if user is not authenticated
    """
    return current_user


def get_current_user_info(
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> UserResponse:
    """
    Dependency that returns structured user information.
    
    Converts the AuthenticatedUser object into a UserResponse schema
    for consistent API responses.
    
    Args:
        current_user: Injected authenticated user
        
    Returns:
        UserResponse with structured user data
    """
    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        authenticated=True,
        additional_claims=current_user.raw_claims
    )


def get_token_info(
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> TokenInfo:
    """
    Dependency that extracts detailed token information.
    
    Provides structured access to JWT claims for routes that need
    detailed token information like expiration times, audience, etc.
    
    Args:
        current_user: Injected authenticated user
        
    Returns:
        TokenInfo with detailed token claims
    """
    claims = current_user.raw_claims
    
    return TokenInfo(
        user_id=current_user.user_id,
        email=current_user.email,
        issued_at=claims.get("iat"),
        expires_at=claims.get("exp"),
        audience=claims.get("aud"),
        issuer=claims.get("iss"),
        role=claims.get("role")
    )


def get_user_id(
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> str:
    """
    Dependency that returns only the user ID.
    
    Convenient for routes that only need the user ID for database
    queries or logging.
    
    Args:
        current_user: Injected authenticated user
        
    Returns:
        User ID string
    """
    return current_user.user_id


def get_user_email(
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> str:
    """
    Dependency that returns only the user email.
    
    Convenient for routes that only need the email for notifications
    or logging.
    
    Args:
        current_user: Injected authenticated user
        
    Returns:
        User email string
    """
    return current_user.email


def require_role(required_role: str):
    """
    Dependency factory for role-based access control.
    
    Creates a dependency that checks if the authenticated user has
    the required role. This prepares for future role-based authorization.
    
    Args:
        required_role: Role required to access the endpoint
        
    Returns:
        Dependency function that validates user role
        
    Example:
        @app.get("/admin/users")
        def admin_endpoint(
            user: AuthenticatedUser = Depends(require_role("admin"))
        ):
            return {"message": "Admin access granted"}
    """
    def role_dependency(
        current_user: AuthenticatedUser = Depends(get_current_user)
    ) -> AuthenticatedUser:
        user_role = current_user.raw_claims.get("role", "")
        
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return current_user
    
    return role_dependency


# Common role dependencies (for future use)
require_admin = require_role("admin")
require_coach = require_role("coach")
require_moderator = require_role("moderator")


def optional_user_info(
    current_user: Optional[AuthenticatedUser] = Depends(get_optional_current_user)
) -> Optional[UserResponse]:
    """
    Dependency that returns optional user information.
    
    Returns structured user information if authenticated, None otherwise.
    Useful for public endpoints that show different content for authenticated users.
    
    Args:
        current_user: Optionally injected authenticated user
        
    Returns:
        UserResponse if authenticated, None otherwise
    """
    if current_user:
        return UserResponse(
            user_id=current_user.user_id,
            email=current_user.email,
            authenticated=True,
            additional_claims=current_user.raw_claims
        )
    return None


# Security scheme for OpenAPI documentation
security_scheme = HTTPBearer()


def validate_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> str:
    """
    Dependency that validates and returns a raw Bearer token.
    
    This is a lower-level dependency for routes that need to access
    the raw token string for custom validation or processing.
    
    Args:
        credentials: Bearer token credentials
        
    Returns:
        Raw token string
        
    Raises:
        HTTPException: 401 if token is missing or invalid format
    """
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return credentials.credentials