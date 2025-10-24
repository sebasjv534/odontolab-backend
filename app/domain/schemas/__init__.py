"""
Schemas package for the OdontoLab system.

This package contains all Pydantic schemas for request validation and response serialization.
"""

from .auth_schemas import Token, TokenData, LoginResponse, UserMeResponse
from .user_schemas import (
    UserRole, UserBase, UserCreate, UserUpdate, UserUpdatePassword,
    UserDeactivate, UserResponse, UserListResponse
)
from .patient_schemas import (
    PatientBase, PatientCreate, PatientUpdate,
    PatientResponse, PatientListResponse
)
from .medical_record_schemas import (
    MedicalRecordBase, MedicalRecordCreate, MedicalRecordUpdate,
    MedicalRecordResponse, MedicalRecordListResponse
)
from .contact_schemas import (
    ContactStatus, ContactRequestCreate, ContactRequestResponse,
    ContactRequestUpdateStatus, ContactRequestListResponse
)
from .dashboard_schemas import (
    AdminDashboardStats, DentistDashboardStats, ReceptionistDashboardStats,
    RecentActivityItem, DashboardStatsResponse, RecentActivityResponse
)

__all__ = [
    # Auth schemas
    "Token",
    "TokenData",
    "LoginResponse",
    "UserMeResponse",
    
    # User schemas
    "UserRole",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserUpdatePassword",
    "UserDeactivate",
    "UserResponse",
    "UserListResponse",
    
    # Patient schemas
    "PatientBase",
    "PatientCreate",
    "PatientUpdate",
    "PatientResponse",
    "PatientListResponse",
    
    # Medical Record schemas
    "MedicalRecordBase",
    "MedicalRecordCreate",
    "MedicalRecordUpdate",
    "MedicalRecordResponse",
    "MedicalRecordListResponse",
    
    # Contact schemas
    "ContactStatus",
    "ContactRequestCreate",
    "ContactRequestResponse",
    "ContactRequestUpdateStatus",
    "ContactRequestListResponse",
    
    # Dashboard schemas
    "AdminDashboardStats",
    "DentistDashboardStats",
    "ReceptionistDashboardStats",
    "RecentActivityItem",
    "DashboardStatsResponse",
    "RecentActivityResponse",
]