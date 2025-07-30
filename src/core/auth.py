"""
JWT Authentication module for Supabase integration.

This module provides JWT validation functionality for authenticating requests
using Supabase-issued tokens.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Security scheme for extracting Bearer tokens
security = HTTPBearer()


class AuthenticatedUser:
    """Container for authenticated user information extracted from JWT."""

    def __init__(self, user_id: str, email: str, **kwargs):
        self.user_id = user_id
        self.email = email
        self.raw_claims = kwargs


def decode_jwt(token: str) -> Dict[str, Any]:
    """
    Decode and validate a Supabase JWT token.

    Args:
        token: The JWT token string to decode

    Returns:
        Dict containing the decoded claims

    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    try:
        # Decode the JWT using the Supabase JWT secret
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            # Validate standard claims
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": False,  # Supabase doesn't always set audience
                "verify_iss": False,  # Supabase doesn't always set issuer
            }
        )

        logger.debug(f"Successfully decoded JWT for user: {payload.get('sub')}")
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error decoding JWT: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def extract_user_from_jwt(payload: Dict[str, Any]) -> AuthenticatedUser:
    """
    Extract user information from decoded JWT payload.

    Args:
        payload: Decoded JWT claims

    Returns:
        AuthenticatedUser instance with user information

    Raises:
        HTTPException: If required claims are missing
    """
    user_id = payload.get("sub")
    email = payload.get("email")

    if not user_id:
        logger.error("JWT payload missing 'sub' claim (user ID)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not email:
        logger.error("JWT payload missing 'email' claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing email",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthenticatedUser(
        user_id=user_id,
        email=email,
        **{k: v for k, v in payload.items() if k not in ("sub", "email")}
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AuthenticatedUser:
    """
    FastAPI dependency to extract and validate the current authenticated user.

    This dependency:
    1. Extracts the Bearer token from the Authorization header
    2. Validates the JWT signature and expiration
    3. Extracts user information from the token
    4. Returns an AuthenticatedUser instance

    Args:
        credentials: Automatically injected HTTPAuthorizationCredentials

    Returns:
        AuthenticatedUser instance containing user info

    Raises:
        HTTPException: If token is missing, invalid, or expired (401)
    """
    token = credentials.credentials

    if not token:
        logger.warning("Authorization header present but token is empty")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode and validate the JWT
    payload = decode_jwt(token)

    # Extract user information
    user = extract_user_from_jwt(payload)

    logger.info(f"Successfully authenticated user: {user.user_id} ({user.email})")
    return user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[AuthenticatedUser]:
    """
    FastAPI dependency for optional authentication.

    This dependency works like get_current_user but returns None instead of
    raising an exception if no valid token is provided. Useful for endpoints
    that have different behavior for authenticated vs anonymous users.

    Args:
        credentials: Optionally injected HTTPAuthorizationCredentials

    Returns:
        AuthenticatedUser instance if valid token provided, None otherwise

    Raises:
        HTTPException: Only if token is provided but invalid (401)
    """
    if not credentials or not credentials.credentials:
        return None

    try:
        return get_current_user(credentials)
    except HTTPException:
        # Re-raise the exception since a token was provided but invalid
        raise
