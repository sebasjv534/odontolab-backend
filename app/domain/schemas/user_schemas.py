"""
User management schemas for the odontology system.

This module defines Pydantic schemas for user registration and profile management
across different roles (administrator, dentist, receptionist).
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime, date
from app.domain.models.role_model import RoleType


class UserCreateBase(BaseModel):
    """
    Base schema for user creation.
    
    Contains common fields for all user types.
    """
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=128, description="User's password")
    first_name: str = Field(..., min_length=1, max_length=100, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="User's last name")
    phone: Optional[str] = Field(None, max_length=20, description="User's phone number")


class AdminCreateUserRequest(UserCreateBase):
    """
    Schema for administrator creating new users.
    
    Includes role assignment and role-specific profile data.
    """
    role: RoleType = Field(..., description="User's role in the system")
    
    # Dentist-specific fields (optional, used when role is DENTIST)
    license_number: Optional[str] = Field(None, max_length=50, description="Professional license number")
    specialization: Optional[str] = Field(None, max_length=100, description="Dental specialization")
    years_experience: Optional[int] = Field(None, ge=0, le=50, description="Years of experience")
    education: Optional[str] = Field(None, description="Educational background")
    certifications: Optional[str] = Field(None, description="Professional certifications")
    
    # Receptionist-specific fields (optional, used when role is RECEPTIONIST)
    employee_id: Optional[str] = Field(None, max_length=20, description="Employee identification")
    department: Optional[str] = Field(None, max_length=100, description="Department assignment")
    shift_schedule: Optional[str] = Field(None, max_length=100, description="Work shift schedule")
    emergency_contact: Optional[str] = Field(None, max_length=200, description="Emergency contact info")
    hire_date: Optional[date] = Field(None, description="Date of employment")

    @validator('license_number')
    def validate_license_number(cls, v, values):
        if values.get('role') == RoleType.DENTIST and not v:
            raise ValueError('License number is required for dentist role')
        return v

    @validator('employee_id')
    def validate_employee_id(cls, v, values):
        if values.get('role') == RoleType.RECEPTIONIST and not v:
            raise ValueError('Employee ID is required for receptionist role')
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Create Dentist",
                    "value": {
                        "username": "dr_smith",
                        "email": "dr.smith@odontolab.com",
                        "password": "securepassword123",
                        "first_name": "John",
                        "last_name": "Smith",
                        "phone": "+1234567890",
                        "role": "dentist",
                        "license_number": "DEN123456",
                        "specialization": "Orthodontics",
                        "years_experience": 10,
                        "education": "DDS from University Medical School",
                        "certifications": "Board Certified Orthodontist"
                    }
                },
                {
                    "title": "Create Receptionist", 
                    "value": {
                        "username": "receptionist_jane",
                        "email": "jane@odontolab.com",
                        "password": "securepassword123",
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "phone": "+1234567891",
                        "role": "receptionist",
                        "employee_id": "EMP001",
                        "department": "Front Desk",
                        "shift_schedule": "Monday-Friday 8AM-5PM",
                        "emergency_contact": "John Doe - +1234567892",
                        "hire_date": "2024-01-15"
                    }
                }
            ]
        }
    }


class UserUpdateRequest(BaseModel):
    """
    Schema for updating user information.
    
    All fields are optional to allow partial updates.
    """
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "John",
                "last_name": "Smith",
                "phone": "+1234567890",
                "email": "john.smith@odontolab.com"
            }
        }
    }


class DentistProfileResponse(BaseModel):
    """
    Schema for dentist profile responses.
    """
    id: str
    license_number: str
    specialization: Optional[str]
    years_experience: Optional[int]
    education: Optional[str]
    certifications: Optional[str]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class ReceptionistProfileResponse(BaseModel):
    """
    Schema for receptionist profile responses.
    """
    id: str
    employee_id: str
    department: Optional[str]
    shift_schedule: Optional[str]
    emergency_contact: Optional[str]
    hire_date: Optional[date]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserDetailResponse(BaseModel):
    """
    Schema for detailed user information responses.
    
    Includes role-specific profile information.
    """
    id: str
    username: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    is_active: bool
    role: str
    created_at: datetime
    dentist_profile: Optional[DentistProfileResponse] = None
    receptionist_profile: Optional[ReceptionistProfileResponse] = None

    model_config = {
        "from_attributes": True
    }