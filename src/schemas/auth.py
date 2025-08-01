"""
Authentication-related Pydantic models and schemas.

This module defines the data models used for authentication and user management
in the MatIQ API, including JWT token validation and user information.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    """Response model for authenticated user information."""
    
    user_id: str = Field(..., description="Unique user identifier from Supabase")
    email: EmailStr = Field(..., description="User's email address")
    authenticated: bool = Field(True, description="Whether the user is authenticated")
    additional_claims: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Additional claims from the JWT token"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "authenticated": True,
                "additional_claims": {
                    "role": "user",
                    "aud": "authenticated",
                    "exp": 1672531200
                }
            }
        }


class TokenInfo(BaseModel):
    """Information extracted from a JWT token."""
    
    user_id: str = Field(..., description="User ID from token subject")
    email: EmailStr = Field(..., description="User email from token")
    issued_at: Optional[int] = Field(None, description="Token issued at timestamp")
    expires_at: Optional[int] = Field(None, description="Token expiration timestamp")
    audience: Optional[str] = Field(None, description="Token audience")
    issuer: Optional[str] = Field(None, description="Token issuer")
    role: Optional[str] = Field(None, description="User role")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "issued_at": 1672444800,
                "expires_at": 1672531200,
                "audience": "authenticated",
                "issuer": "https://your-project.supabase.co/auth/v1",
                "role": "authenticated"
            }
        }


class AuthError(BaseModel):
    """Error response for authentication failures."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Additional error details"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "error": "invalid_token",
                "message": "The provided token is invalid or expired",
                "details": {
                    "token_status": "expired",
                    "expired_at": "2024-01-01T12:00:00Z"
                }
            }
        }


class PublicEndpointResponse(BaseModel):
    """Response model for public endpoints with optional authentication."""
    
    message: str = Field(..., description="Response message")
    authenticated: bool = Field(..., description="Whether request was authenticated")
    user_info: Optional[UserResponse] = Field(
        default=None, 
        description="User information if authenticated"
    )
    public_data: str = Field(..., description="Data available to all users")
    premium_data: Optional[str] = Field(
        default=None, 
        description="Data only available to authenticated users"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message": "Welcome to MatIQ API",
                "authenticated": True,
                "user_info": {
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "authenticated": True
                },
                "public_data": "Wrestling tournament data",
                "premium_data": "Advanced analytics and insights"
            }
        }


class ProtectedActionRequest(BaseModel):
    """Request model for protected actions."""
    
    action: str = Field(..., description="Action to perform")
    data: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Additional action data"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "action": "update_profile",
                "data": {
                    "preferences": {
                        "theme": "dark",
                        "notifications": True
                    }
                }
            }
        }


class ProtectedActionResponse(BaseModel):
    """Response model for protected actions."""
    
    message: str = Field(..., description="Action result message")
    performed_by: EmailStr = Field(..., description="Email of user who performed action")
    user_id: str = Field(..., description="ID of user who performed action")
    action_data: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Data that was processed"
    )
    timestamp: str = Field(..., description="Action timestamp")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message": "Profile updated successfully",
                "performed_by": "user@example.com",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "action_data": {
                    "preferences": {
                        "theme": "dark",
                        "notifications": True
                    }
                },
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }