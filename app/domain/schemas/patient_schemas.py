"""
Patient schemas for validation and serialization.

This module defines Pydantic schemas for Patient-related operations following
the API_SUMMARY specifications.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime


class PatientBase(BaseModel):
    """Base schema for patient data."""
    first_name: str = Field(..., min_length=1, max_length=100, description="Patient's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Patient's last name")
    email: EmailStr = Field(..., description="Patient's email address")
    phone: str = Field(..., min_length=7, max_length=20, description="Patient's phone number")
    date_of_birth: date = Field(..., description="Patient's birth date")
    address: Optional[str] = Field(None, description="Patient's address")
    emergency_contact_name: Optional[str] = Field(None, max_length=100, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, max_length=20, description="Emergency contact phone")
    medical_conditions: Optional[str] = Field(None, description="Pre-existing medical conditions")
    allergies: Optional[str] = Field(None, description="Known allergies")


class PatientCreate(PatientBase):
    """Schema for creating a new patient."""
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "María",
                "last_name": "García Rodríguez",
                "email": "maria.garcia@email.com",
                "phone": "3001234567",
                "date_of_birth": "1990-05-15",
                "address": "Calle 45 #23-12, Bogotá",
                "emergency_contact_name": "Pedro García",
                "emergency_contact_phone": "3009876543",
                "medical_conditions": "Hipertensión controlada",
                "allergies": "Penicilina"
            }
        }
    }


class PatientUpdate(BaseModel):
    """Schema for updating patient information."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Patient's first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Patient's last name")
    email: Optional[EmailStr] = Field(None, description="Patient's email address")
    phone: Optional[str] = Field(None, min_length=7, max_length=20, description="Patient's phone number")
    date_of_birth: Optional[date] = Field(None, description="Patient's birth date")
    address: Optional[str] = Field(None, description="Patient's address")
    emergency_contact_name: Optional[str] = Field(None, max_length=100, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, max_length=20, description="Emergency contact phone")
    medical_conditions: Optional[str] = Field(None, description="Pre-existing medical conditions")
    allergies: Optional[str] = Field(None, description="Known allergies")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "phone": "3001234567",
                "address": "Calle 45 #23-12, Bogotá",
                "medical_conditions": "Hipertensión controlada, Diabetes tipo 2"
            }
        }
    }


class PatientResponse(BaseModel):
    """Schema for patient response."""
    id: str = Field(..., description="Patient's unique identifier")
    first_name: str = Field(..., description="Patient's first name")
    last_name: str = Field(..., description="Patient's last name")
    email: str = Field(..., description="Patient's email address")
    phone: str = Field(..., description="Patient's phone number")
    date_of_birth: date = Field(..., description="Patient's birth date")
    address: Optional[str] = Field(None, description="Patient's address")
    emergency_contact_name: Optional[str] = Field(None, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, description="Emergency contact phone")
    medical_conditions: Optional[str] = Field(None, description="Pre-existing medical conditions")
    allergies: Optional[str] = Field(None, description="Known allergies")
    created_at: datetime = Field(..., description="Patient creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="User ID who created the patient")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "650e8400-e29b-41d4-a716-446655440001",
                "first_name": "María",
                "last_name": "García Rodríguez",
                "email": "maria.garcia@email.com",
                "phone": "3001234567",
                "date_of_birth": "1990-05-15",
                "address": "Calle 45 #23-12, Bogotá",
                "emergency_contact_name": "Pedro García",
                "emergency_contact_phone": "3009876543",
                "medical_conditions": "Hipertensión controlada",
                "allergies": "Penicilina",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z",
                "created_by": "550e8400-e29b-41d4-a716-446655440003"
            }
        }
    }


class PatientListResponse(BaseModel):
    """Schema for paginated patient list response."""
    success: bool = Field(True, description="Request success status")
    data: list[PatientResponse] = Field(..., description="List of patients")
    total: int = Field(..., description="Total number of patients")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "data": [
                    {
                        "id": "650e8400-e29b-41d4-a716-446655440001",
                        "first_name": "María",
                        "last_name": "García Rodríguez",
                        "email": "maria.garcia@email.com",
                        "phone": "3001234567",
                        "date_of_birth": "1990-05-15",
                        "address": "Calle 45 #23-12, Bogotá",
                        "emergency_contact_name": "Pedro García",
                        "emergency_contact_phone": "3009876543",
                        "medical_conditions": "Hipertensión controlada",
                        "allergies": "Penicilina",
                        "created_at": "2025-01-01T00:00:00Z",
                        "updated_at": "2025-01-01T00:00:00Z",
                        "created_by": "550e8400-e29b-41d4-a716-446655440003"
                    }
                ],
                "total": 3,
                "page": 1,
                "per_page": 10,
                "total_pages": 1
            }
        }
    }
