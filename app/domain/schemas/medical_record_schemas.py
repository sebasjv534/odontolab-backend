"""
Medical Record schemas for validation and serialization.

This module defines Pydantic schemas for MedicalRecord-related operations following
the API_SUMMARY specifications.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class MedicalRecordBase(BaseModel):
    """Base schema for medical record data."""
    patient_id: str = Field(..., description="Patient's unique identifier")
    visit_date: datetime = Field(..., description="Date and time of the visit")
    diagnosis: str = Field(..., min_length=1, description="Clinical diagnosis")
    treatment: str = Field(..., min_length=1, description="Treatment performed")
    notes: Optional[str] = Field(None, description="Additional clinical notes")
    teeth_chart: Optional[Dict[str, Any]] = Field(None, description="Digital odontogram in JSON format")
    next_appointment: Optional[datetime] = Field(None, description="Scheduled next appointment")


class MedicalRecordCreate(MedicalRecordBase):
    """Schema for creating a new medical record."""
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": "650e8400-e29b-41d4-a716-446655440001",
                "visit_date": "2025-01-15T10:00:00Z",
                "diagnosis": "Caries dental en segundo molar superior derecho",
                "treatment": "Restauración con resina compuesta. Se realizó limpieza profunda y aplicación de sellante.",
                "notes": "Paciente cooperativa. Se recomienda control en 6 meses.",
                "teeth_chart": {
                    "tooth_17": {
                        "status": "restored",
                        "notes": "Resina compuesta"
                    },
                    "general": "Higiene oral regular"
                },
                "next_appointment": "2025-07-15T10:00:00Z"
            }
        }
    }


class MedicalRecordUpdate(BaseModel):
    """Schema for updating medical record information."""
    visit_date: Optional[datetime] = Field(None, description="Date and time of the visit")
    diagnosis: Optional[str] = Field(None, min_length=1, description="Clinical diagnosis")
    treatment: Optional[str] = Field(None, min_length=1, description="Treatment performed")
    notes: Optional[str] = Field(None, description="Additional clinical notes")
    teeth_chart: Optional[Dict[str, Any]] = Field(None, description="Digital odontogram in JSON format")
    next_appointment: Optional[datetime] = Field(None, description="Scheduled next appointment")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "notes": "Paciente cooperativa. Se recomienda control en 6 meses. Actualizado por evolución favorable.",
                "next_appointment": "2025-08-15T10:00:00Z"
            }
        }
    }


class MedicalRecordResponse(BaseModel):
    """Schema for medical record response."""
    id: str = Field(..., description="Medical record's unique identifier")
    patient_id: str = Field(..., description="Patient's unique identifier")
    dentist_id: str = Field(..., description="Dentist's unique identifier")
    visit_date: datetime = Field(..., description="Date and time of the visit")
    diagnosis: str = Field(..., description="Clinical diagnosis")
    treatment: str = Field(..., description="Treatment performed")
    notes: Optional[str] = Field(None, description="Additional clinical notes")
    teeth_chart: Optional[Dict[str, Any]] = Field(None, description="Digital odontogram in JSON format")
    next_appointment: Optional[datetime] = Field(None, description="Scheduled next appointment")
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "750e8400-e29b-41d4-a716-446655440001",
                "patient_id": "650e8400-e29b-41d4-a716-446655440001",
                "dentist_id": "550e8400-e29b-41d4-a716-446655440002",
                "visit_date": "2025-01-15T10:00:00Z",
                "diagnosis": "Caries dental en segundo molar superior derecho",
                "treatment": "Restauración con resina compuesta. Se realizó limpieza profunda y aplicación de sellante.",
                "notes": "Paciente cooperativa. Se recomienda control en 6 meses.",
                "teeth_chart": {
                    "tooth_17": {
                        "status": "restored",
                        "notes": "Resina compuesta"
                    },
                    "general": "Higiene oral regular"
                },
                "next_appointment": "2025-07-15T10:00:00Z",
                "created_at": "2025-01-15T10:00:00Z",
                "updated_at": "2025-01-15T10:00:00Z"
            }
        }
    }


class MedicalRecordListResponse(BaseModel):
    """Schema for paginated medical record list response."""
    success: bool = Field(True, description="Request success status")
    data: list[MedicalRecordResponse] = Field(..., description="List of medical records")
    total: int = Field(..., description="Total number of medical records")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "data": [
                    {
                        "id": "750e8400-e29b-41d4-a716-446655440001",
                        "patient_id": "650e8400-e29b-41d4-a716-446655440001",
                        "dentist_id": "550e8400-e29b-41d4-a716-446655440002",
                        "visit_date": "2025-01-15T10:00:00Z",
                        "diagnosis": "Caries dental en segundo molar superior derecho",
                        "treatment": "Restauración con resina compuesta",
                        "notes": "Paciente cooperativa",
                        "teeth_chart": {"tooth_17": {"status": "restored"}},
                        "next_appointment": "2025-07-15T10:00:00Z",
                        "created_at": "2025-01-15T10:00:00Z",
                        "updated_at": "2025-01-15T10:00:00Z"
                    }
                ],
                "total": 3,
                "page": 1,
                "per_page": 10,
                "total_pages": 1
            }
        }
    }
