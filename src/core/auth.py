"""
JWT Authentication module for Supabase integration.

This module provides JWT validation functionality for authenticating requests
using Supabase-issued tokens. It supports both HS256 (for testing) and RS256 
(for production Supabase tokens) JWT validation.
"""

from typing import Optional, Dict, Any
import requests
import jwt
import logging
from functools import lru_cache
from cryptography.hazmat.primitives import serialization
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

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


@lru_cache(maxsize=1)
def get_supabase_public_key() -> Optional[str]:
    """
    Fetch Supabase's public key for JWT validation.
    
    This function fetches the public key from Supabase's JWKS endpoint
    for RS256 JWT validation. The result is cached to avoid repeated requests.
    
    Returns:
        Public key as PEM string, or None if fetch fails
    """
    if not settings.SUPABASE_URL or settings.SUPABASE_URL == "https://your-supabase-url.supabase.co":
        logger.debug("Supabase URL not configured, skipping public key fetch")
        return None
    
    try:
        jwks_url = f"{settings.SUPABASE_URL}/auth/v1/jwks"
        logger.debug(f"Fetching JWKS from: {jwks_url}")
        
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        
        jwks = response.json()
        
        # Get the first key (Supabase typically has one key)
        if "keys" not in jwks or not jwks["keys"]:
            logger.warning("No keys found in JWKS response")
            return None
            
        key_data = jwks["keys"][0]
        
        # Convert JWK to PEM format for cryptography library
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key_data)
        
        # Serialize to PEM format
        pem_key = public_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        logger.debug("Successfully fetched and converted Supabase public key")
        return pem_key.decode('utf-8')
        
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch Supabase JWKS: {e}")
        return None
    except Exception as e:
        logger.error(f"Error processing Supabase public key: {e}")
        return None


def get_jwt_validation_key():
    """
    Get the appropriate key for JWT validation.
    
    Returns RS256 public key for production or HS256 secret for testing.
    
    Returns:
        Tuple of (key, algorithm) for JWT validation
    """
    # First try to get Supabase public key for RS256
    public_key = get_supabase_public_key()
    if public_key:
        return public_key, "RS256"
    
    # Fall back to HS256 with secret (for testing)
    logger.debug("Using HS256 fallback for JWT validation")
    return settings.SUPABASE_JWT_SECRET, settings.JWT_ALGORITHM


def decode_jwt(token: str) -> Dict[str, Any]:
    """
    Decode and validate a Supabase JWT token.

    Supports both RS256 (production Supabase) and HS256 (testing) validation.

    Args:
        token: The JWT token string to decode

    Returns:
        Dict containing the decoded claims

    Raises:
        HTTPException: If token is invalid, expired, or malformed
    """
    try:
        # Get the appropriate validation key and algorithm
        validation_key, algorithm = get_jwt_validation_key()
        
        logger.debug(f"Validating JWT with algorithm: {algorithm}")
        
        # Decode the JWT using the determined key and algorithm
        payload = jwt.decode(
            token,
            validation_key,
            algorithms=[algorithm],
            # Validate standard claims
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": False,  # Supabase doesn't always set audience consistently
                "verify_iss": False,  # Supabase issuer varies by setup
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
