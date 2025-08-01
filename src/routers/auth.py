"""
Authentication and protected routes for demonstrating JWT validation.

This module contains endpoints that demonstrate the JWT authentication system
and provide examples of protected routes using the new schemas and dependencies.
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Dict, Any

from src.core.auth import get_current_user, get_optional_current_user, AuthenticatedUser
from src.dependencies.auth import (
    get_current_user_info, 
    get_token_info, 
    optional_user_info,
    require_authenticated_user
)
from src.schemas.auth import (
    UserResponse, 
    TokenInfo, 
    PublicEndpointResponse,
    ProtectedActionRequest,
    ProtectedActionResponse
)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)


@router.get("/me", response_model=UserResponse)
def get_current_user_info_endpoint(
    user_info: UserResponse = Depends(get_current_user_info)
) -> UserResponse:
    """
    Get information about the currently authenticated user.

    This is a protected endpoint that requires a valid JWT token.
    Returns structured user information extracted from the JWT.
    """
    return user_info


@router.get("/token-info", response_model=TokenInfo)
def get_token_info_endpoint(
    token_info: TokenInfo = Depends(get_token_info)
) -> TokenInfo:
    """
    Get detailed information about the current JWT token.
    
    This protected endpoint returns comprehensive token information
    including expiration times, issuer, audience, and other claims.
    """
    return token_info


@router.get("/profile")
def get_user_profile(
    current_user: AuthenticatedUser = Depends(require_authenticated_user)
) -> Dict[str, Any]:
    """
    Get user profile information (protected endpoint example).

    This demonstrates a data-modifying endpoint that would require authentication.
    In a real application, this would fetch user-specific data from the database.
    """
    return {
        "message": f"Welcome to your profile, {current_user.email}!",
        "user_id": current_user.user_id,
        "email": current_user.email,
        "profile_data": {
            "created_at": "2024-01-01T00:00:00Z",  # Mock data
            "last_login": datetime.now().isoformat() + "Z",
            "preferences": {
                "theme": "dark",
                "notifications": True
            },
            "statistics": {
                "tournaments_participated": 12,
                "matches_recorded": 48,
                "favorite_weight_class": "157 lbs"
            }
        }
    }


@router.post("/protected-action", response_model=ProtectedActionResponse)
def perform_protected_action(
    action_request: ProtectedActionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> ProtectedActionResponse:
    """
    Example of a POST endpoint that requires authentication.

    This demonstrates how data-modifying operations would be protected.
    In a real application, this would perform actual business logic.
    """
    return ProtectedActionResponse(
        message="Protected action completed successfully",
        performed_by=current_user.email,
        user_id=current_user.user_id,
        action_data=action_request.dict(),
        timestamp=datetime.now().isoformat() + "Z"
    )


@router.get("/public-with-optional-auth", response_model=PublicEndpointResponse)
def public_endpoint_with_optional_auth(
    user_info: UserResponse = Depends(optional_user_info)
) -> PublicEndpointResponse:
    """
    Example of a public endpoint that behaves differently for authenticated users.

    This endpoint is accessible to everyone but provides additional
    information if the user is authenticated.
    """
    base_data = {
        "message": "Welcome to MatIQ Wrestling Analytics",
        "public_data": "Tournament schedules, public wrestler rankings, and match results"
    }

    if user_info:
        return PublicEndpointResponse(
            **base_data,
            authenticated=True,
            user_info=user_info,
            premium_data="Detailed analytics, coaching insights, and personalized recommendations"
        )
    else:
        return PublicEndpointResponse(
            **base_data,
            authenticated=False,
            user_info=None,
            premium_data=None
        )
