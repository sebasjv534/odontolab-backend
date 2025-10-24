"""
Contact Request schemas for validation and serialization.

This module defines Pydantic schemas for ContactRequest-related operations following
the API_SUMMARY specifications. This is a PUBLIC endpoint (no authentication required).
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum


class ContactStatus(str, Enum):
    """Contact request status enumeration."""
    PENDING = "pending"
    CONTACTED = "contacted"
    RESOLVED = "resolved"


class ContactRequestCreate(BaseModel):
    """
    Schema for creating a new contact request (PUBLIC ENDPOINT).
    
    This is used by the public website contact form and does not require authentication.
    """
    nombre: str = Field(..., min_length=1, max_length=100, description="Full name")
    cedula: str = Field(..., min_length=1, max_length=20, description="ID document number")
    email: EmailStr = Field(..., description="Email address")
    telefono: str = Field(..., min_length=7, max_length=20, description="Phone number")
    motivo: str = Field(..., min_length=1, max_length=255, description="Reason for contact")
    servicio: Optional[str] = Field(None, description="Service of interest")
    aceptaPolitica: bool = Field(..., description="Acceptance of privacy policy (must be True)")
    
    @field_validator('aceptaPolitica')
    @classmethod
    def validate_acepta_politica(cls, v: bool) -> bool:
        """Validate that privacy policy is accepted."""
        if not v:
            raise ValueError('Must accept privacy policy to submit contact request')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre": "Roberto Sánchez",
                "cedula": "1234567890",
                "email": "roberto.sanchez@email.com",
                "telefono": "3001112233",
                "motivo": "Consulta por ortodoncia y blanqueamiento dental",
                "servicio": "Ortodoncia",
                "aceptaPolitica": True
            }
        }
    }


class ContactRequestResponse(BaseModel):
    """Schema for contact request response."""
    id: str = Field(..., description="Contact request's unique identifier")
    nombre: str = Field(..., description="Full name")
    cedula: str = Field(..., description="ID document number")
    email: str = Field(..., description="Email address")
    telefono: str = Field(..., description="Phone number")
    motivo: str = Field(..., description="Reason for contact")
    servicio: Optional[str] = Field(None, description="Service of interest")
    acepta_politica: bool = Field(..., description="Acceptance of privacy policy")
    status: str = Field(..., description="Current status of the request")
    created_at: datetime = Field(..., description="Submission timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "850e8400-e29b-41d4-a716-446655440001",
                "nombre": "Roberto Sánchez",
                "cedula": "1234567890",
                "email": "roberto.sanchez@email.com",
                "telefono": "3001112233",
                "motivo": "Consulta por ortodoncia y blanqueamiento dental",
                "servicio": "Ortodoncia",
                "acepta_politica": True,
                "status": "pending",
                "created_at": "2025-01-20T15:30:00Z"
            }
        }
    }


class ContactRequestUpdateStatus(BaseModel):
    """Schema for updating contact request status (ADMIN only)."""
    status: ContactStatus = Field(..., description="New status for the request")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "contacted"
            }
        }
    }


class ContactRequestListResponse(BaseModel):
    """Schema for paginated contact request list response."""
    success: bool = Field(True, description="Request success status")
    data: list[ContactRequestResponse] = Field(..., description="List of contact requests")
    total: int = Field(..., description="Total number of contact requests")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "data": [
                    {
                        "id": "850e8400-e29b-41d4-a716-446655440001",
                        "nombre": "Roberto Sánchez",
                        "cedula": "1234567890",
                        "email": "roberto.sanchez@email.com",
                        "telefono": "3001112233",
                        "motivo": "Consulta por ortodoncia",
                        "servicio": "Ortodoncia",
                        "acepta_politica": True,
                        "status": "pending",
                        "created_at": "2025-01-20T15:30:00Z"
                    }
                ],
                "total": 2,
                "page": 1,
                "per_page": 10,
                "total_pages": 1
            }
        }
    }
