"""
Authentication schemas for the odontology system.

This module defines Pydantic schemas for authentication and authorization,
including login requests, token responses, and user registration.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """
    Schema for user login requests.
    
    Attributes:
        email (EmailStr): User's email address
        password (str): User's password (plain text, will be hashed)
    """
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=128, description="User's password")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "dentist@odontolab.com",
                "password": "securepassword123"
            }
        }
    }


class TokenResponse(BaseModel):
    """
    Schema for JWT token responses.
    
    Attributes:
        access_token (str): JWT access token
        token_type (str): Type of token (always "bearer")
        expires_in (int): Token expiration time in seconds
        user_id (str): User's unique identifier
        role (str): User's role name
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user_id: str = Field(..., description="User's unique identifier")
    role: str = Field(..., description="User's role name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "role": "dentist"
            }
        }
    }


class TokenData(BaseModel):
    """
    Schema for token data validation.
    
    Attributes:
        user_id (Optional[str]): User's unique identifier from token
    """
    user_id: Optional[str] = None


class UserResponse(BaseModel):
    """
    Schema for user information responses.
    
    Attributes:
        id (str): User's unique identifier
        username (str): User's username
        email (str): User's email address
        first_name (str): User's first name
        last_name (str): User's last name
        phone (Optional[str]): User's phone number
        is_active (bool): Whether the user account is active
        role (str): User's role name
        created_at (datetime): Account creation timestamp
    """
    id: str = Field(..., description="User's unique identifier")
    username: str = Field(..., description="User's username")
    email: str = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    phone: Optional[str] = Field(None, description="User's phone number")
    is_active: bool = Field(..., description="Whether the user account is active")
    role: str = Field(..., description="User's role name")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "dentist_user",
                "email": "dentist@odontolab.com",
                "first_name": "Dr. John",
                "last_name": "Smith",
                "phone": "+1234567890",
                "is_active": True,
                "role": "dentist",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }
    }


class ChangePasswordRequest(BaseModel):
    """
    Schema for password change requests.
    
    Attributes:
        current_password (str): User's current password
        new_password (str): New password to set
    """
    current_password: str = Field(..., min_length=8, max_length=128, description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")

    model_config = {
        "json_schema_extra": {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newsecurepassword456"
            }
        }
    }