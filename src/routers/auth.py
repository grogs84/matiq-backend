"""Authentication router for user login endpoint."""

import logging
from fastapi import APIRouter, HTTPException

from ..schemas.auth import LoginRequest, LoginResponse
from ..services.auth_service import auth_service


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest) -> LoginResponse:
    """
    User login endpoint for Supabase authentication.

    Validates user credentials via Supabase and returns authentication result.

    Args:
        login_request: User email and password

    Returns:
        LoginResponse with success status and optional user data

    Raises:
        HTTPException: For server errors
    """
    try:
        logger.info(f"Login attempt for email: {login_request.email}")

        response = await auth_service.login(login_request)

        if response.success:
            logger.info(f"Successful login for: {login_request.email}")
        else:
            logger.warning(f"Failed login attempt for: {login_request.email}")

        return response

    except Exception as e:
        logger.error(f"Login endpoint error for {login_request.email}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error during authentication"
        )
