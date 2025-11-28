"""
Appointment schemas for validation and serialization.

This module defines Pydantic schemas for Appointment-related operations
following RESTful API best practices.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date as date_type, time as time_type
from uuid import UUID
from app.domain.models.enums import AppointmentStatus, ReminderType


class AppointmentBase(BaseModel):
    """Base schema for appointment data."""
    patient_id: UUID = Field(..., description="Patient's unique identifier")
    dentist_id: UUID = Field(..., description="Dentist's unique identifier")
    scheduled_time: datetime = Field(..., description="Date and time of the appointment")
    duration_minutes: int = Field(30, ge=5, le=480, description="Duration in minutes (5-480)")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for the appointment")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes")
    
    @validator('scheduled_time')
    def validate_future_time(cls, v):
        """Ensure scheduled_time is in the future."""
        if v <= datetime.now(v.tzinfo):
            raise ValueError('Scheduled time must be in the future')
        return v
    
    @validator('duration_minutes')
    def validate_duration(cls, v):
        """Ensure duration is a multiple of 5 minutes."""
        if v % 5 != 0:
            raise ValueError('Duration must be a multiple of 5 minutes')
        return v


class AppointmentCreate(AppointmentBase):
    """Schema for creating a new appointment."""
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": "650e8400-e29b-41d4-a716-446655440001",
                "dentist_id": "550e8400-e29b-41d4-a716-446655440003",
                "scheduled_time": "2025-12-01T10:00:00-05:00",
                "duration_minutes": 30,
                "reason": "Limpieza dental de rutina",
                "notes": "Paciente prefiere anestesia local"
            }
        }
    }


class AppointmentUpdate(BaseModel):
    """Schema for updating appointment information."""
    scheduled_time: Optional[datetime] = Field(None, description="New date and time")
    duration_minutes: Optional[int] = Field(None, ge=5, le=480, description="New duration")
    reason: Optional[str] = Field(None, max_length=500, description="Updated reason")
    notes: Optional[str] = Field(None, max_length=2000, description="Updated notes")
    status: Optional[AppointmentStatus] = Field(None, description="Updated status")
    
    @validator('scheduled_time')
    def validate_future_time(cls, v):
        """Ensure new scheduled_time is in the future."""
        if v and v <= datetime.now(v.tzinfo):
            raise ValueError('Scheduled time must be in the future')
        return v
    
    @validator('duration_minutes')
    def validate_duration(cls, v):
        """Ensure duration is a multiple of 5 minutes."""
        if v and v % 5 != 0:
            raise ValueError('Duration must be a multiple of 5 minutes')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "scheduled_time": "2025-12-01T11:00:00-05:00",
                "duration_minutes": 45,
                "notes": "Paciente llegará 10 minutos antes"
            }
        }
    }


class AppointmentStatusUpdate(BaseModel):
    """Schema for updating only the appointment status."""
    status: AppointmentStatus = Field(..., description="New appointment status")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes for status change")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "confirmed",
                "notes": "Paciente confirmó asistencia por teléfono"
            }
        }
    }


class AppointmentResponse(BaseModel):
    """Schema for appointment response."""
    id: UUID = Field(..., description="Appointment's unique identifier")
    patient_id: UUID = Field(..., description="Patient's unique identifier")
    dentist_id: UUID = Field(..., description="Dentist's unique identifier")
    scheduled_time: datetime = Field(..., description="Date and time of the appointment")
    duration_minutes: int = Field(..., description="Duration in minutes")
    status: AppointmentStatus = Field(..., description="Current appointment status")
    reason: Optional[str] = Field(None, description="Reason for the appointment")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_by: Optional[UUID] = Field(None, description="User ID who created the appointment")
    created_at: datetime = Field(..., description="Appointment creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "750e8400-e29b-41d4-a716-446655440010",
                "patient_id": "650e8400-e29b-41d4-a716-446655440001",
                "dentist_id": "550e8400-e29b-41d4-a716-446655440003",
                "scheduled_time": "2025-12-01T10:00:00-05:00",
                "duration_minutes": 30,
                "status": "scheduled",
                "reason": "Limpieza dental de rutina",
                "notes": "Paciente prefiere anestesia local",
                "created_by": "550e8400-e29b-41d4-a716-446655440004",
                "created_at": "2025-11-27T09:00:00-05:00",
                "updated_at": "2025-11-27T09:00:00-05:00"
            }
        }
    }


class AppointmentDetailResponse(AppointmentResponse):
    """
    Extended appointment response with related entity details.
    Includes patient and dentist information for UI display.
    """
    patient_name: Optional[str] = Field(None, description="Patient's full name")
    patient_phone: Optional[str] = Field(None, description="Patient's phone number")
    dentist_name: Optional[str] = Field(None, description="Dentist's full name")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "750e8400-e29b-41d4-a716-446655440010",
                "patient_id": "650e8400-e29b-41d4-a716-446655440001",
                "patient_name": "María García Rodríguez",
                "patient_phone": "3001234567",
                "dentist_id": "550e8400-e29b-41d4-a716-446655440003",
                "dentist_name": "Dr. Carlos Méndez",
                "scheduled_time": "2025-12-01T10:00:00-05:00",
                "duration_minutes": 30,
                "status": "scheduled",
                "reason": "Limpieza dental de rutina",
                "notes": "Paciente prefiere anestesia local",
                "created_by": "550e8400-e29b-41d4-a716-446655440004",
                "created_at": "2025-11-27T09:00:00-05:00",
                "updated_at": "2025-11-27T09:00:00-05:00"
            }
        }
    }


class AppointmentListResponse(BaseModel):
    """Schema for paginated appointment list response."""
    success: bool = Field(True, description="Request success status")
    data: List[AppointmentDetailResponse] = Field(..., description="List of appointments")
    total: int = Field(..., description="Total number of appointments")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class AppointmentReminderCreate(BaseModel):
    """Schema for creating appointment reminders."""
    appointment_id: UUID = Field(..., description="Appointment's unique identifier")
    reminder_type: ReminderType = Field(..., description="Type of reminder (email, SMS, WhatsApp)")
    scheduled_for: datetime = Field(..., description="When to send the reminder")
    
    @validator('scheduled_for')
    def validate_reminder_time(cls, v):
        """Ensure reminder is scheduled for the future."""
        if v <= datetime.now(v.tzinfo):
            raise ValueError('Reminder time must be in the future')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "appointment_id": "750e8400-e29b-41d4-a716-446655440010",
                "reminder_type": "email",
                "scheduled_for": "2025-11-30T10:00:00-05:00"
            }
        }
    }


class AppointmentReminderResponse(BaseModel):
    """Schema for appointment reminder response."""
    id: UUID = Field(..., description="Reminder's unique identifier")
    appointment_id: UUID = Field(..., description="Appointment's unique identifier")
    reminder_type: ReminderType = Field(..., description="Type of reminder")
    scheduled_for: datetime = Field(..., description="When to send the reminder")
    sent: bool = Field(..., description="Whether the reminder has been sent")
    sent_at: Optional[datetime] = Field(None, description="When the reminder was sent")
    created_at: datetime = Field(..., description="Reminder creation timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "850e8400-e29b-41d4-a716-446655440020",
                "appointment_id": "750e8400-e29b-41d4-a716-446655440010",
                "reminder_type": "email",
                "scheduled_for": "2025-11-30T10:00:00-05:00",
                "sent": False,
                "sent_at": None,
                "created_at": "2025-11-27T09:00:00-05:00"
            }
        }
    }


class AppointmentConflictCheck(BaseModel):
    """Schema for checking appointment conflicts."""
    dentist_id: UUID = Field(..., description="Dentist's unique identifier")
    scheduled_time: datetime = Field(..., description="Proposed appointment time")
    duration_minutes: int = Field(30, ge=5, le=480, description="Duration in minutes")
    exclude_appointment_id: Optional[UUID] = Field(None, description="Appointment ID to exclude from conflict check")


class AppointmentAvailability(BaseModel):
    """Schema for checking dentist availability."""
    dentist_id: UUID = Field(..., description="Dentist's unique identifier")
    date: date_type = Field(..., description="Date to check availability")
    start_hour: Optional[time_type] = Field(time_type(8, 0), description="Start of working hours")
    end_hour: Optional[time_type] = Field(time_type(18, 0), description="End of working hours")
    slot_duration: int = Field(30, ge=15, le=120, description="Time slot duration in minutes")


class TimeSlot(BaseModel):
    """Schema for available time slots."""
    start_time: datetime = Field(..., description="Slot start time")
    end_time: datetime = Field(..., description="Slot end time")
    available: bool = Field(..., description="Whether the slot is available")


class AvailabilityResponse(BaseModel):
    """Schema for availability response."""
    dentist_id: UUID = Field(..., description="Dentist's unique identifier")
    date: date_type = Field(..., description="Date checked")
    slots: List[TimeSlot] = Field(..., description="List of time slots")
    total_slots: int = Field(..., description="Total number of slots")
    available_slots: int = Field(..., description="Number of available slots")


class AppointmentStats(BaseModel):
    """Schema for appointment statistics."""
    total_appointments: int = Field(..., description="Total number of appointments")
    by_status: dict = Field(..., description="Appointments grouped by status")
    upcoming_count: int = Field(..., description="Number of upcoming appointments")
    completion_rate: float = Field(..., description="Percentage of completed appointments")
    no_show_rate: float = Field(..., description="Percentage of no-show appointments")
    total_patients: int = Field(..., description="Total unique patients with appointments")

