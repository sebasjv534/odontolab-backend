"""
User schemas for validation and serialization.

This module defines Pydantic schemas for User-related operations following
the API_SUMMARY specifications.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    DENTIST = "dentist"
    RECEPTIONIST = "receptionist"


class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr = Field(..., description="User's email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="User's last name")
    role: UserRole = Field(..., description="User's role in the system")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=128, description="User's password")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "dentist@odontolab.com",
                "first_name": "Juan Carlos",
                "last_name": "Pérez García",
                "role": "dentist",
                "password": "secure123"
            }
        }
    }


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = Field(None, description="User's email address")
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's last name")
    role: Optional[UserRole] = Field(None, description="User's role in the system")
    is_active: Optional[bool] = Field(None, description="Whether the user is active")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Juan Carlos",
                "last_name": "Pérez Gómez",
                "is_active": True
            }
        }
    }


class UserUpdatePassword(BaseModel):
    """Schema for updating user password."""
    password: str = Field(..., min_length=8, max_length=128, description="New password")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserDeactivate(BaseModel):
    """Schema for deactivating a user."""
    is_active: bool = Field(False, description="Set to False to deactivate")


class UserResponse(BaseModel):
    """Schema for user response."""
    id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    role: str = Field(..., description="User's role")
    is_active: bool = Field(..., description="Whether the user is active")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
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
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            }
        }
    }


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""
    success: bool = Field(True, description="Request success status")
    data: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "data": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440001",
                        "email": "admin@odontolab.com",
                        "first_name": "Admin",
                        "last_name": "Sistema",
                        "role": "admin",
                        "is_active": True,
                        "created_at": "2025-01-01T00:00:00Z",
                        "updated_at": "2025-01-01T00:00:00Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "per_page": 10,
                "total_pages": 1
            }
        }
    }