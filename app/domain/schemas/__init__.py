"""
Schemas package for the odontology system.

This package contains all Pydantic schemas for request/response validation
and serialization in the dental clinic management system.
"""

from .auth_schemas import (
    LoginRequest,
    TokenResponse,
    TokenData,
    UserResponse,
    ChangePasswordRequest
)
from .user_schemas import (
    AdminCreateUserRequest,
    UserUpdateRequest,
    UserDetailResponse,
    DentistProfileResponse,
    ReceptionistProfileResponse
)
from .clinical_schemas import (
    PatientCreateRequest,
    PatientUpdateRequest,
    PatientResponse,
    PatientWithInterventionsResponse,
    ClinicalInterventionCreateRequest,
    ClinicalInterventionUpdateRequest,
    ClinicalInterventionResponse
)

__all__ = [
    # Auth schemas
    "LoginRequest",
    "TokenResponse", 
    "TokenData",
    "UserResponse",
    "ChangePasswordRequest",
    # User schemas
    "AdminCreateUserRequest",
    "UserUpdateRequest",
    "UserDetailResponse",
    "DentistProfileResponse",
    "ReceptionistProfileResponse",
    # Clinical schemas
    "PatientCreateRequest",
    "PatientUpdateRequest",
    "PatientResponse",
    "PatientWithInterventionsResponse",
    "ClinicalInterventionCreateRequest",
    "ClinicalInterventionUpdateRequest",
    "ClinicalInterventionResponse"
]