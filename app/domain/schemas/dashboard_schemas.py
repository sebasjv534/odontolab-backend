"""
Dashboard schemas for validation and serialization.

This module defines Pydantic schemas for Dashboard statistics following
the API_SUMMARY specifications. Statistics vary by user role.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class AdminDashboardStats(BaseModel):
    """
    Dashboard statistics for Admin role.
    
    Includes comprehensive system-wide statistics.
    """
    total_patients: int = Field(..., description="Total number of patients in the system")
    total_users: int = Field(..., description="Total number of active users")
    total_staff: int = Field(..., description="Total staff members (dentists + receptionists)")
    total_dentists: int = Field(..., description="Total number of dentists")
    total_receptionists: int = Field(..., description="Total number of receptionists")
    total_medical_records: int = Field(..., description="Total number of medical records")
    recent_patients: int = Field(..., description="Patients registered in the last 30 days")
    recent_records: int = Field(..., description="Medical records created in the last 30 days")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total_patients": 150,
                "total_users": 25,
                "total_staff": 24,
                "total_dentists": 15,
                "total_receptionists": 9,
                "total_medical_records": 450,
                "recent_patients": 12,
                "recent_records": 35
            }
        }
    }


class DentistDashboardStats(BaseModel):
    """
    Dashboard statistics for Dentist role.
    
    Includes personal statistics and patient counts.
    """
    total_patients: int = Field(..., description="Total patients with medical records from this dentist")
    total_medical_records: int = Field(..., description="Total medical records created by this dentist")
    recent_records: int = Field(..., description="Medical records created in the last 30 days")
    upcoming_appointments: int = Field(..., description="Number of upcoming appointments scheduled")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total_patients": 45,
                "total_medical_records": 120,
                "recent_records": 8,
                "upcoming_appointments": 5
            }
        }
    }


class ReceptionistDashboardStats(BaseModel):
    """
    Dashboard statistics for Receptionist role.
    
    Includes patient management statistics.
    """
    total_patients: int = Field(..., description="Total patients in the system")
    patients_registered_by_me: int = Field(..., description="Patients registered by this receptionist")
    recent_patients: int = Field(..., description="Patients registered in the last 30 days")
    total_medical_records: int = Field(..., description="Total medical records in the system")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total_patients": 150,
                "patients_registered_by_me": 45,
                "recent_patients": 12,
                "total_medical_records": 450
            }
        }
    }


class RecentActivityItem(BaseModel):
    """Schema for a recent activity item."""
    id: str = Field(..., description="Activity ID")
    type: str = Field(..., description="Activity type (patient_created, medical_record_created, etc.)")
    description: str = Field(..., description="Activity description")
    timestamp: datetime = Field(..., description="Activity timestamp")
    user_name: Optional[str] = Field(None, description="Name of user who performed the activity")
    patient_name: Optional[str] = Field(None, description="Name of patient involved (if applicable)")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "activity-001",
                "type": "medical_record_created",
                "description": "Nueva historia clínica creada para María García",
                "timestamp": "2025-01-20T10:30:00Z",
                "user_name": "Dr. Juan Pérez",
                "patient_name": "María García"
            }
        }
    }


class DashboardStatsResponse(BaseModel):
    """
    Generic dashboard stats response.
    
    The stats field will contain role-specific statistics.
    """
    success: bool = Field(True, description="Request success status")
    role: str = Field(..., description="User's role")
    stats: Dict[str, Any] = Field(..., description="Role-specific statistics")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "role": "admin",
                "stats": {
                    "total_patients": 150,
                    "total_users": 25,
                    "total_staff": 24,
                    "total_dentists": 15,
                    "total_receptionists": 9,
                    "total_medical_records": 450,
                    "recent_patients": 12,
                    "recent_records": 35
                }
            }
        }
    }


class RecentActivityResponse(BaseModel):
    """Schema for recent activity response."""
    success: bool = Field(True, description="Request success status")
    data: List[RecentActivityItem] = Field(..., description="List of recent activities")
    total: int = Field(..., description="Total number of activities")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "data": [
                    {
                        "id": "activity-001",
                        "type": "medical_record_created",
                        "description": "Nueva historia clínica creada para María García",
                        "timestamp": "2025-01-20T10:30:00Z",
                        "user_name": "Dr. Juan Pérez",
                        "patient_name": "María García"
                    },
                    {
                        "id": "activity-002",
                        "type": "patient_created",
                        "description": "Nuevo paciente registrado: Carlos López",
                        "timestamp": "2025-01-20T09:15:00Z",
                        "user_name": "Ana Martínez",
                        "patient_name": "Carlos López"
                    }
                ],
                "total": 2
            }
        }
    }
