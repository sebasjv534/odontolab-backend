"""
Patient and clinical schemas for the odontology system.

This module defines Pydantic schemas for patient management and clinical interventions,
supporting the core dental clinic functionality.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from app.domain.models.clinical_models import Gender, InterventionType


class PatientCreateRequest(BaseModel):
    """
    Schema for creating new patient records.
    
    Used by receptionists to register new patients in the system.
    """
    first_name: str = Field(..., min_length=1, max_length=100, description="Patient's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Patient's last name")
    date_of_birth: date = Field(..., description="Patient's birth date")
    gender: Gender = Field(..., description="Patient's gender")
    phone: str = Field(..., min_length=10, max_length=20, description="Primary contact phone")
    email: Optional[EmailStr] = Field(None, description="Patient's email address")
    address: Optional[str] = Field(None, max_length=500, description="Residential address")
    emergency_contact_name: Optional[str] = Field(None, max_length=200, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, max_length=20, description="Emergency contact phone")
    medical_history: Optional[str] = Field(None, description="Relevant medical history")
    allergies: Optional[str] = Field(None, description="Known allergies and reactions")
    insurance_info: Optional[str] = Field(None, description="Insurance information")

    @validator('date_of_birth')
    def validate_birth_date(cls, v):
        if v > date.today():
            raise ValueError('Birth date cannot be in the future')
        if date.today().year - v.year > 150:
            raise ValueError('Invalid birth date - too old')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Maria",
                "last_name": "Garcia",
                "date_of_birth": "1985-05-15",
                "gender": "female",
                "phone": "+1234567890",
                "email": "maria.garcia@email.com",
                "address": "123 Main St, City, State 12345",
                "emergency_contact_name": "Juan Garcia",
                "emergency_contact_phone": "+1234567891",
                "medical_history": "Hypertension, controlled with medication",
                "allergies": "Penicillin",
                "insurance_info": "HealthPlan Plus - Policy #HP123456"
            }
        }
    }


class PatientUpdateRequest(BaseModel):
    """
    Schema for updating patient information.
    
    All fields are optional to allow partial updates.
    """
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    insurance_info: Optional[str] = None


class PatientResponse(BaseModel):
    """
    Schema for patient information responses.
    """
    id: str
    patient_number: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    phone: str
    email: Optional[str]
    address: Optional[str]
    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[str]
    medical_history: Optional[str]
    allergies: Optional[str]
    insurance_info: Optional[str]
    age: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class ClinicalInterventionCreateRequest(BaseModel):
    """
    Schema for creating clinical intervention records.
    
    Used by dentists to record treatments and procedures.
    """
    patient_id: str = Field(..., description="Patient's unique identifier")
    intervention_type: InterventionType = Field(..., description="Type of dental intervention")
    diagnosis: str = Field(..., min_length=10, description="Clinical diagnosis")
    treatment_description: str = Field(..., min_length=10, description="Detailed treatment description")
    notes: Optional[str] = Field(None, description="Additional clinical notes")
    cost: Optional[Decimal] = Field(None, ge=0, description="Cost of the intervention")
    intervention_date: datetime = Field(..., description="Date and time of intervention")
    follow_up_date: Optional[datetime] = Field(None, description="Scheduled follow-up date")

    @validator('follow_up_date')
    def validate_follow_up_date(cls, v, values):
        if v and values.get('intervention_date') and v <= values['intervention_date']:
            raise ValueError('Follow-up date must be after intervention date')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": "123e4567-e89b-12d3-a456-426614174000",
                "intervention_type": "filling",
                "diagnosis": "Dental caries on upper right molar",
                "treatment_description": "Removed decay and placed composite filling on tooth #3",
                "notes": "Patient tolerated procedure well. Advised to avoid hard foods for 24 hours.",
                "cost": 150.00,
                "intervention_date": "2024-01-15T14:30:00Z",
                "follow_up_date": "2024-01-29T14:30:00Z"
            }
        }
    }


class ClinicalInterventionUpdateRequest(BaseModel):
    """
    Schema for updating clinical intervention records.
    """
    diagnosis: Optional[str] = Field(None, min_length=10)
    treatment_description: Optional[str] = Field(None, min_length=10)
    notes: Optional[str] = None
    cost: Optional[Decimal] = Field(None, ge=0)
    follow_up_date: Optional[datetime] = None


class ClinicalInterventionResponse(BaseModel):
    """
    Schema for clinical intervention responses.
    """
    id: str
    patient_id: str
    dentist_id: str
    intervention_type: str
    diagnosis: str
    treatment_description: str
    notes: Optional[str]
    cost: Optional[Decimal]
    intervention_date: datetime
    follow_up_date: Optional[datetime]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class PatientWithInterventionsResponse(PatientResponse):
    """
    Schema for patient responses including clinical history.
    """
    clinical_interventions: List[ClinicalInterventionResponse] = []

    model_config = {
        "from_attributes": True
    }