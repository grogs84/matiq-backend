"""
Authentication and protected routes for demonstrating JWT validation.

This module contains endpoints that demonstrate the JWT authentication system
and provide examples of protected routes.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any

from src.core.auth import get_current_user, get_optional_current_user, AuthenticatedUser

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)


@router.get("/me")
def get_current_user_info(
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get information about the currently authenticated user.

    This is a protected endpoint that requires a valid JWT token.
    Returns user information extracted from the JWT.
    """
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "authenticated": True,
        "additional_claims": current_user.raw_claims
    }


@router.get("/profile")
def get_user_profile(
    current_user: AuthenticatedUser = Depends(get_current_user)
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
            "last_login": "2024-12-30T12:00:00Z",  # Mock data
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        }
    }


@router.post("/protected-action")
def perform_protected_action(
    action_data: Dict[str, Any],
    current_user: AuthenticatedUser = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Example of a POST endpoint that requires authentication.

    This demonstrates how data-modifying operations would be protected.
    In a real application, this would perform actual business logic.
    """
    return {
        "message": "Protected action completed successfully",
        "performed_by": current_user.email,
        "user_id": current_user.user_id,
        "action_data": action_data,
        "timestamp": "2024-12-30T12:00:00Z"  # Mock timestamp
    }


@router.get("/public-with-optional-auth")
def public_endpoint_with_optional_auth(
    current_user: AuthenticatedUser = Depends(get_optional_current_user)
) -> Dict[str, Any]:
    """
    Example of a public endpoint that behaves differently for authenticated users.

    This endpoint is accessible to everyone but provides additional
    information if the user is authenticated.
    """
    base_response = {
        "message": "This is a public endpoint",
        "public_data": "Available to everyone",
        "timestamp": "2024-12-30T12:00:00Z"
    }

    if current_user:
        base_response.update({
            "authenticated": True,
            "user_specific_message": f"Hello {current_user.email}!",
            "premium_data": "This data is only shown to authenticated users"
        })
    else:
        base_response.update({
            "authenticated": False,
            "guest_message": "Sign up to see more content!"
        })

    return base_response
