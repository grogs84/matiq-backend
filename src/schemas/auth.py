"""Authentication related schemas."""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: str
    password: str


class LoginResponse(BaseModel):
    """Schema for user login response."""

    success: bool
    message: str
    user_id: str | None = None
    access_token: str | None = None
