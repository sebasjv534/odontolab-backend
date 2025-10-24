"""
Authentication schemas for the OdontoLab system.

This module defines Pydantic schemas for authentication following OAuth2 standards
and API_SUMMARY specifications.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    """
    OAuth2 token response schema.
    
    Attributes:
        access_token (str): JWT access token
        token_type (str): Token type (always "bearer")
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }
    }


class TokenData(BaseModel):
    """
    Schema for token data validation.
    
    Attributes:
        sub (str): Subject (user_id)
        email (str): User email
        role (str): User role
    """
    sub: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class LoginResponse(BaseModel):
    """
    Enhanced login response with user information.
    
    Attributes:
        access_token (str): JWT access token
        token_type (str): Token type (always "bearer")
        user (dict): User information
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: dict = Field(..., description="User information")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440001",
                    "email": "admin@odontolab.com",
                    "first_name": "Admin",
                    "last_name": "Sistema",
                    "role": "admin",
                    "is_active": True
                }
            }
        }
    }


class UserMeResponse(BaseModel):
    """
    Schema for /auth/me endpoint response.
    
    Returns current authenticated user information.
    """
    id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    role: str = Field(..., description="User's role")
    is_active: bool = Field(..., description="Whether the user is active")
    created_at: datetime = Field(..., description="User creation timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440001",
                "email": "admin@odontolab.com",
                "first_name": "Admin",
                "last_name": "Sistema",
                "role": "admin",
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z"
            }
        }
    }