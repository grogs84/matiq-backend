"""Authentication service for Supabase integration."""

import logging

from ..schemas.auth import LoginRequest, LoginResponse


logger = logging.getLogger(__name__)


class AuthService:
    """Service for handling user authentication via Supabase."""

    def __init__(self):
        """Initialize the auth service with Supabase client."""
        try:
            # For now, we'll implement a basic mock until Supabase is properly installed
            # In production, this would be:
            # from supabase import create_client, Client
            # self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

            logger.info("Auth service initialized (mock mode for demonstration)")
        except Exception as e:
            logger.error(f"Failed to initialize auth service: {str(e)}")
            raise

    async def login(self, login_request: LoginRequest) -> LoginResponse:
        """
        Authenticate user with email and password via Supabase.

        Args:
            login_request: User login credentials

        Returns:
            LoginResponse with authentication result
        """
        try:
            logger.info(f"Attempting login for user: {login_request.email}")

            # Mock authentication logic for demonstration
            # In production, this would integrate with Supabase:
            # response = self.supabase.auth.sign_in_with_password({
            #     "email": login_request.email,
            #     "password": login_request.password
            # })

            # For demonstration, accept test credentials
            if (
                login_request.email == "test@example.com"
                and login_request.password == "testpassword"
            ):
                logger.info(f"Login successful for user: {login_request.email}")
                return LoginResponse(
                    success=True,
                    message="Login successful",
                    user_id="mock-user-id-123",
                    access_token="mock-access-token-abc",
                )
            else:
                logger.warning(
                    f"Login failed for user: {login_request.email} - Invalid credentials"
                )
                return LoginResponse(success=False, message="Invalid email or password")

        except Exception as e:
            logger.error(f"Login error for user {login_request.email}: {str(e)}")
            return LoginResponse(success=False, message="Authentication service error")


# Singleton instance
auth_service = AuthService()
