"""
Appointments API endpoints.
Handles all appointment-related HTTP requests.
"""
from typing import List, Optional
from uuid import UUID
from datetime import date as date_type, datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.presentation.api.dependencies import get_current_user
from app.domain.models.user_model import User
from app.domain.schemas.appointment_schemas import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentStatusUpdate,
    AppointmentResponse,
    AppointmentDetailResponse,
    AppointmentListResponse,
    AppointmentConflictCheck,
    AppointmentAvailability,
    AvailabilityResponse,
    AppointmentStats
)
from app.domain.models.enums import AppointmentStatus
from app.application.services.appointment_service import AppointmentService

router = APIRouter(prefix="/appointments", tags=["appointments"])


def get_appointment_service(db: AsyncSession = Depends(get_db)) -> AppointmentService:
    """Dependency to get appointment service instance."""
    return AppointmentService(db)


@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new appointment",
    description="Create a new appointment. Requires ADMIN, RECEPTIONIST, or DENTIST role."
)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service)
) -> AppointmentResponse:
    """
    Create a new appointment with the following validations:
    - Check dentist availability
    - Validate time conflicts
    - Verify business hours
    - Check role permissions
    """
    appointment = await service.create_appointment(
        appointment_data=appointment_data,
        creator_id=current_user.id,
        current_user=current_user
    )
    return AppointmentResponse.model_validate(appointment)


@router.get(
    "/",
    response_model=AppointmentListResponse,
    summary="List appointments",
    description="List appointments with optional filters. Results depend on user role."
)
async def list_appointments(
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    dentist_id: Optional[UUID] = Query(None, description="Filter by dentist ID"),
    status: Optional[AppointmentStatus] = Query(None, description="Filter by appointment status"),
    start_date: Optional[date_type] = Query(None, description="Filter appointments from this date"),
    end_date: Optional[date_type] = Query(None, description="Filter appointments until this date"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service)
) -> AppointmentListResponse:
    """
    List appointments with role-based filtering:
    - ADMIN/RECEPTIONIST: Can see all appointments
    - DENTIST: Can only see their own appointments
    - Other roles: Access denied
    """
    appointments, total = await service.list_appointments(
        current_user=current_user,
        patient_id=patient_id,
        dentist_id=dentist_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return AppointmentListResponse(
        appointments=[AppointmentResponse.model_validate(apt) for apt in appointments],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentDetailResponse,
    summary="Get appointment details",
    description="Get detailed information about a specific appointment."
)
async def get_appointment(
    appointment_id: UUID,
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service)
) -> AppointmentDetailResponse:
    """Get detailed information about an appointment including patient and dentist details."""
    appointment = await service.get_appointment(
        appointment_id=appointment_id,
        current_user=current_user
    )
    return AppointmentDetailResponse.model_validate(appointment)


@router.put(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    summary="Update appointment",
    description="Update appointment details. Requires ADMIN, RECEPTIONIST, or assigned DENTIST role."
)
async def update_appointment(
    appointment_id: UUID,
    appointment_data: AppointmentUpdate,
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service)
) -> AppointmentResponse:
    """
    Update appointment details including:
    - Date and time
    - Duration
    - Reason
    - Notes
    
    Validates time conflicts and dentist availability.
    """
    appointment = await service.update_appointment(
        appointment_id=appointment_id,
        appointment_data=appointment_data,
        current_user=current_user
    )
    return AppointmentResponse.model_validate(appointment)


@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentResponse,
    summary="Update appointment status",
    description="Update the status of an appointment (scheduled, confirmed, in_progress, completed, cancelled, no_show)."
)
async def update_appointment_status(
    appointment_id: UUID,
    status_data: AppointmentStatusUpdate,
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service)
) -> AppointmentResponse:
    """
    Update appointment status with validation:
    - scheduled → confirmed, cancelled, no_show
    - confirmed → in_progress, cancelled, no_show
    - in_progress → completed, cancelled
    - completed, cancelled, no_show: No further transitions allowed
    """
    appointment = await service.update_appointment_status(
        appointment_id=appointment_id,
        new_status=status_data.status,
        notes=status_data.notes,
        current_user=current_user
    )
    return AppointmentResponse.model_validate(appointment)


@router.delete(
    "/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel appointment",
    description="Cancel an appointment. Requires ADMIN, RECEPTIONIST, or assigned DENTIST role."
)
async def cancel_appointment(
    appointment_id: UUID,
    reason: Optional[str] = Query(None, description="Reason for cancellation"),
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service)
):
    """
    Cancel an appointment. This updates the status to 'cancelled' rather than deleting the record.
    """
    await service.cancel_appointment(
        appointment_id=appointment_id,
        reason=reason,
        current_user=current_user
    )
    return None


@router.post(
    "/check-conflict",
    response_model=dict,
    summary="Check appointment conflict",
    description="Check if there's a time conflict for a proposed appointment."
)
async def check_conflict(
    conflict_check: AppointmentConflictCheck,
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service)
) -> dict:
    """
    Check if the proposed appointment time conflicts with existing appointments.
    Returns conflict status and details if conflict exists.
    """
    has_conflict, conflicting_appointment = await service.repository.check_conflicts(
        dentist_id=conflict_check.dentist_id,
        appointment_datetime=conflict_check.appointment_datetime,
        duration_minutes=conflict_check.duration_minutes,
        exclude_appointment_id=conflict_check.exclude_appointment_id
    )
    
    return {
        "has_conflict": has_conflict,
        "conflicting_appointment": (
            AppointmentResponse.model_validate(conflicting_appointment) 
            if conflicting_appointment else None
        )
    }


@router.post(
    "/availability",
    response_model=AvailabilityResponse,
    summary="Check dentist availability",
    description="Get available time slots for a dentist on a specific date."
)
async def check_availability(
    availability_request: AppointmentAvailability,
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service)
) -> AvailabilityResponse:
    """
    Get available time slots for a dentist on a specific date.
    Takes into account existing appointments and business hours.
    """
    return await service.check_availability(
        dentist_id=availability_request.dentist_id,
        date=availability_request.date,
        slot_duration=availability_request.slot_duration,
        start_hour=availability_request.start_hour,
        end_hour=availability_request.end_hour
    )


@router.get(
    "/stats/dashboard",
    response_model=AppointmentStats,
    summary="Get appointment statistics",
    description="Get appointment statistics for dashboard. Requires ADMIN or RECEPTIONIST role."
)
async def get_appointment_stats(
    start_date: Optional[date_type] = Query(None, description="Start date for statistics"),
    end_date: Optional[date_type] = Query(None, description="End date for statistics"),
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service)
) -> AppointmentStats:
    """
    Get appointment statistics including:
    - Total appointments
    - Appointments by status
    - Upcoming appointments
    - Completion rate
    - No-show rate
    """
    return await service.get_appointment_stats(
        current_user=current_user,
        start_date=start_date,
        end_date=end_date
    )


@router.get(
    "/upcoming/me",
    response_model=List[AppointmentResponse],
    summary="Get my upcoming appointments",
    description="Get upcoming appointments for the current dentist."
)
async def get_my_upcoming_appointments(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of appointments to return"),
    current_user: User = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service)
) -> List[AppointmentResponse]:
    """
    Get upcoming appointments for the current dentist.
    Only available for users with DENTIST role.
    """
    appointments = await service.get_upcoming_appointments(
        dentist_id=current_user.id,
        limit=limit,
        current_user=current_user
    )
    return [AppointmentResponse.model_validate(apt) for apt in appointments]
