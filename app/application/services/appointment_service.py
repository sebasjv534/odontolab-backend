"""
Appointment service for business logic.

This module provides appointment services including scheduling,
conflict detection, status management, and reminder creation.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date, time, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import Appointment, AppointmentReminder, Patient, User
from app.domain.models.user_model import UserRole
from app.domain.models.enums import AppointmentStatus, ReminderType
from app.domain.schemas.appointment_schemas import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentStatusUpdate,
    AppointmentResponse,
    AppointmentDetailResponse,
    AppointmentReminderCreate
)
from app.insfraestructure.repositories.appointment_repository import AppointmentRepository
from app.application.exceptions import (
    AppointmentNotFoundError,
    AppointmentConflictError,
    ValidationError,
    AuthorizationError,
    PatientNotFoundError,
    UserNotFoundError
)


class AppointmentService:
    """
    Service layer for appointment business logic.
    
    Handles appointment creation, updates, conflict detection,
    status transitions, and reminder management.
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize the appointment service with database session."""
        self.session = session
        self.repository = AppointmentRepository(session)
    
    async def create_appointment(
        self,
        appointment_data: AppointmentCreate,
        current_user: User
    ) -> AppointmentResponse:
        """
        Create a new appointment with validation.
        
        Args:
            appointment_data: Appointment creation data
            current_user: User creating the appointment
            
        Returns:
            Created appointment response
            
        Raises:
            PatientNotFoundError: If patient doesn't exist
            UserNotFoundError: If dentist doesn't exist
            AppointmentConflictError: If there's a scheduling conflict
            ValidationError: If validation fails
        """
        # Validate patient exists
        from app.insfraestructure.repositories.patient_repository import PatientRepository
        patient_repo = PatientRepository(self.session)
        patient = await patient_repo.get_by_id(appointment_data.patient_id)
        if not patient:
            raise PatientNotFoundError(f"Patient with ID {appointment_data.patient_id} not found")
        
        # Validate dentist exists and has DENTIST role
        from app.insfraestructure.repositories.user_repository import UserRepository
        user_repo = UserRepository(self.session)
        dentist = await user_repo.get_by_id(appointment_data.dentist_id)
        if not dentist:
            raise UserNotFoundError(f"Dentist with ID {appointment_data.dentist_id} not found")
        if dentist.role != UserRole.DENTIST and dentist.role != UserRole.ADMIN:
            raise ValidationError("Specified user is not a dentist")
        
        # Validate business hours (optional - can be configured)
        if not self._is_within_business_hours(appointment_data.scheduled_time):
            raise ValidationError(
                "Appointment must be scheduled during business hours (Monday-Friday 8:00-18:00, Saturday 8:00-13:00)"
            )
        
        # Create appointment
        appointment_dict = appointment_data.model_dump()
        appointment_dict['created_by'] = current_user.id
        appointment_dict['status'] = AppointmentStatus.SCHEDULED
        
        appointment = await self.repository.create(appointment_dict)
        
        # Create automatic reminders
        await self._create_automatic_reminders(appointment)
        
        return AppointmentResponse.model_validate(appointment)
    
    async def get_appointment(
        self,
        appointment_id: UUID,
        current_user: User,
        detailed: bool = False
    ) -> AppointmentResponse | AppointmentDetailResponse:
        """
        Get appointment by ID with authorization.
        
        Args:
            appointment_id: UUID of the appointment
            current_user: User requesting the appointment
            detailed: Whether to include detailed information
            
        Returns:
            Appointment response (detailed or basic)
            
        Raises:
            AppointmentNotFoundError: If appointment doesn't exist
            AuthorizationError: If user doesn't have access
        """
        appointment = await self.repository.get_by_id_or_raise(appointment_id, load_relations=True)
        
        # Authorization check
        self._check_appointment_access(appointment, current_user)
        
        if detailed:
            return self._build_detailed_response(appointment)
        
        return AppointmentResponse.model_validate(appointment)
    
    async def update_appointment(
        self,
        appointment_id: UUID,
        update_data: AppointmentUpdate,
        current_user: User
    ) -> AppointmentResponse:
        """
        Update appointment information.
        
        Args:
            appointment_id: UUID of the appointment to update
            update_data: Update data
            current_user: User performing the update
            
        Returns:
            Updated appointment response
            
        Raises:
            AppointmentNotFoundError: If appointment doesn't exist
            AuthorizationError: If user doesn't have permission
            ValidationError: If update is invalid
        """
        appointment = await self.repository.get_by_id_or_raise(appointment_id)
        
        # Authorization check
        self._check_appointment_modification_access(appointment, current_user)
        
        # Validate status transition if status is being updated
        if update_data.status and update_data.status != appointment.status:
            self._validate_status_transition(appointment, update_data.status)
        
        # Validate business hours if time is being updated
        if update_data.scheduled_time and not self._is_within_business_hours(update_data.scheduled_time):
            raise ValidationError("Appointment must be scheduled during business hours")
        
        # Update appointment
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_appointment = await self.repository.update(appointment_id, update_dict)
        
        return AppointmentResponse.model_validate(updated_appointment)
    
    async def update_appointment_status(
        self,
        appointment_id: UUID,
        status_update: AppointmentStatusUpdate,
        current_user: User
    ) -> AppointmentResponse:
        """
        Update appointment status with validation.
        
        Args:
            appointment_id: UUID of the appointment
            status_update: New status data
            current_user: User performing the update
            
        Returns:
            Updated appointment response
            
        Raises:
            AppointmentNotFoundError: If appointment doesn't exist
            ValidationError: If status transition is invalid
        """
        appointment = await self.repository.get_by_id_or_raise(appointment_id)
        
        # Authorization check
        self._check_appointment_modification_access(appointment, current_user)
        
        # Validate status transition
        self._validate_status_transition(appointment, status_update.status)
        
        # Update status
        update_dict = {
            'status': status_update.status
        }
        if status_update.notes:
            update_dict['notes'] = status_update.notes
        
        updated_appointment = await self.repository.update(appointment_id, update_dict)
        
        return AppointmentResponse.model_validate(updated_appointment)
    
    async def cancel_appointment(
        self,
        appointment_id: UUID,
        current_user: User,
        reason: Optional[str] = None
    ) -> AppointmentResponse:
        """
        Cancel an appointment.
        
        Args:
            appointment_id: UUID of the appointment
            current_user: User cancelling the appointment
            reason: Cancellation reason
            
        Returns:
            Updated appointment response
        """
        appointment = await self.repository.get_by_id_or_raise(appointment_id)
        
        # Authorization check
        self._check_appointment_modification_access(appointment, current_user)
        
        # Check if appointment can be cancelled
        if not appointment.can_be_cancelled():
            raise ValidationError(
                f"Cannot cancel appointment with status {appointment.status.value}"
            )
        
        # Cancel appointment
        update_dict = {
            'status': AppointmentStatus.CANCELLED
        }
        if reason:
            current_notes = appointment.notes or ""
            update_dict['notes'] = f"{current_notes}\n[CANCELLATION] {reason}".strip()
        
        updated_appointment = await self.repository.update(appointment_id, update_dict)
        
        return AppointmentResponse.model_validate(updated_appointment)
    
    async def list_appointments(
        self,
        current_user: User,
        patient_id: Optional[UUID] = None,
        dentist_id: Optional[UUID] = None,
        status: Optional[AppointmentStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        per_page: int = 50
    ) -> tuple[List[AppointmentDetailResponse], int]:
        """
        List appointments with filters and pagination.
        
        Args:
            current_user: User requesting the list
            patient_id: Filter by patient
            dentist_id: Filter by dentist
            status: Filter by status
            start_date: Filter by start date
            end_date: Filter by end date
            page: Page number (1-indexed)
            per_page: Items per page
            
        Returns:
            Tuple of (list of appointments, total count)
        """
        # Apply role-based filters
        if current_user.role == UserRole.DENTIST:
            dentist_id = current_user.id
        elif current_user.role == UserRole.RECEPTIONIST and not (dentist_id or patient_id):
            # Receptionist can see all, but we might want to limit the date range
            if not start_date:
                start_date = date.today()
            if not end_date:
                end_date = start_date + timedelta(days=30)
        
        # Calculate pagination
        skip = (page - 1) * per_page
        
        # Get appointments
        appointments, total = await self.repository.list_appointments(
            patient_id=patient_id,
            dentist_id=dentist_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=per_page,
            load_relations=True
        )
        
        # Build detailed responses
        detailed_responses = [self._build_detailed_response(apt) for apt in appointments]
        
        return detailed_responses, total
    
    async def check_availability(
        self,
        dentist_id: UUID,
        check_date: date,
        start_time: time = time(8, 0),
        end_time: time = time(18, 0),
        slot_duration: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Check dentist availability for a specific date.
        
        Args:
            dentist_id: UUID of the dentist
            check_date: Date to check
            start_time: Start of working hours
            end_time: End of working hours
            slot_duration: Duration of each slot in minutes
            
        Returns:
            List of time slots with availability
        """
        return await self.repository.check_availability(
            dentist_id=dentist_id,
            check_date=check_date,
            start_time=start_time,
            end_time=end_time,
            slot_duration=slot_duration
        )
    
    async def get_upcoming_appointments(
        self,
        current_user: User,
        days_ahead: int = 7
    ) -> List[AppointmentDetailResponse]:
        """
        Get upcoming appointments for current user.
        
        Args:
            current_user: Current logged-in user
            days_ahead: Number of days to look ahead
            
        Returns:
            List of upcoming appointments
        """
        dentist_id = current_user.id if current_user.role == UserRole.DENTIST else None
        
        appointments = await self.repository.get_upcoming_appointments(
            dentist_id=dentist_id,
            days_ahead=days_ahead
        )
        
        return [self._build_detailed_response(apt) for apt in appointments]
    
    async def _create_automatic_reminders(self, appointment: Appointment) -> None:
        """
        Create automatic reminders for an appointment.
        
        Creates:
        - Email reminder 24 hours before
        - SMS reminder 2 hours before (if configured)
        """
        # Email reminder 24 hours before
        email_reminder_time = appointment.scheduled_time - timedelta(hours=24)
        if email_reminder_time > datetime.now(appointment.scheduled_time.tzinfo):
            email_reminder = AppointmentReminder(
                appointment_id=appointment.id,
                reminder_type=ReminderType.EMAIL,
                scheduled_for=email_reminder_time
            )
            self.session.add(email_reminder)
        
        # SMS reminder 2 hours before (optional)
        sms_reminder_time = appointment.scheduled_time - timedelta(hours=2)
        if sms_reminder_time > datetime.now(appointment.scheduled_time.tzinfo):
            sms_reminder = AppointmentReminder(
                appointment_id=appointment.id,
                reminder_type=ReminderType.SMS,
                scheduled_for=sms_reminder_time
            )
            self.session.add(sms_reminder)
        
        await self.session.commit()
    
    def _check_appointment_access(self, appointment: Appointment, user: User) -> None:
        """Check if user has access to view appointment."""
        if user.role == UserRole.ADMIN or user.role == UserRole.RECEPTIONIST:
            return
        if user.role == UserRole.DENTIST and appointment.dentist_id == user.id:
            return
        raise AuthorizationError("You don't have permission to access this appointment")
    
    def _check_appointment_modification_access(self, appointment: Appointment, user: User) -> None:
        """Check if user has access to modify appointment."""
        if user.role == UserRole.ADMIN or user.role == UserRole.RECEPTIONIST:
            return
        if user.role == UserRole.DENTIST and appointment.dentist_id == user.id:
            return
        raise AuthorizationError("You don't have permission to modify this appointment")
    
    def _validate_status_transition(self, appointment: Appointment, new_status: AppointmentStatus) -> None:
        """
        Validate status transition according to business rules.
        
        Valid transitions:
        - SCHEDULED -> CONFIRMED, CANCELLED, NO_SHOW
        - CONFIRMED -> IN_PROGRESS, CANCELLED, NO_SHOW
        - IN_PROGRESS -> COMPLETED
        """
        current_status = appointment.status
        
        # Define valid transitions
        valid_transitions = {
            AppointmentStatus.SCHEDULED: [
                AppointmentStatus.CONFIRMED,
                AppointmentStatus.CANCELLED,
                AppointmentStatus.NO_SHOW
            ],
            AppointmentStatus.CONFIRMED: [
                AppointmentStatus.IN_PROGRESS,
                AppointmentStatus.CANCELLED,
                AppointmentStatus.NO_SHOW
            ],
            AppointmentStatus.IN_PROGRESS: [
                AppointmentStatus.COMPLETED
            ]
        }
        
        # Check if transition is valid
        allowed_statuses = valid_transitions.get(current_status, [])
        if new_status not in allowed_statuses:
            raise ValidationError(
                f"Invalid status transition from {current_status.value} to {new_status.value}"
            )
    
    def _is_within_business_hours(self, scheduled_time: datetime) -> bool:
        """
        Check if scheduled time is within business hours.
        
        Business hours:
        - Monday-Friday: 8:00-18:00
        - Saturday: 8:00-13:00
        - Sunday: Closed
        """
        weekday = scheduled_time.weekday()
        hour = scheduled_time.hour
        
        # Sunday (6) - Closed
        if weekday == 6:
            return False
        
        # Saturday (5) - 8:00-13:00
        if weekday == 5:
            return 8 <= hour < 13
        
        # Monday-Friday (0-4) - 8:00-18:00
        return 8 <= hour < 18
    
    def _build_detailed_response(self, appointment: Appointment) -> AppointmentDetailResponse:
        """Build detailed appointment response with related entity information."""
        response_data = AppointmentResponse.model_validate(appointment).model_dump()
        
        # Add related entity information
        if appointment.patient:
            response_data['patient_name'] = appointment.patient.full_name
            response_data['patient_phone'] = appointment.patient.phone
        
        if appointment.dentist:
            response_data['dentist_name'] = appointment.dentist.full_name
        
        return AppointmentDetailResponse(**response_data)
    
    async def get_appointment_stats(
        self,
        current_user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get appointment statistics for dashboard.
        
        Args:
            current_user: User requesting the statistics
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with appointment statistics
            
        Raises:
            AuthorizationError: If user doesn't have permission
        """
        # Only ADMIN and RECEPTIONIST can view stats
        if current_user.role not in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
            raise AuthorizationError("No tiene permiso para ver estadísticas")
        
        # Get all appointments in date range
        appointments, total = await self.repository.list_appointments(
            start_date=start_date,
            end_date=end_date,
            skip=0,
            limit=10000  # Get all for stats
        )
        
        # Calculate stats
        by_status = {}
        unique_patients = set()
        completed_count = 0
        no_show_count = 0
        upcoming_count = 0
        now = datetime.now()
        
        for apt in appointments:
            # Count by status
            status_key = apt.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1
            
            # Track unique patients
            unique_patients.add(apt.patient_id)
            
            # Count completed and no-show
            if apt.status == AppointmentStatus.COMPLETED:
                completed_count += 1
            elif apt.status == AppointmentStatus.NO_SHOW:
                no_show_count += 1
            
            # Count upcoming (future appointments that aren't cancelled/completed/no_show)
            if (apt.scheduled_time > now and 
                apt.status not in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]):
                upcoming_count += 1
        
        # Calculate rates
        total_finished = completed_count + no_show_count
        completion_rate = (completed_count / total_finished * 100) if total_finished > 0 else 0
        no_show_rate = (no_show_count / total_finished * 100) if total_finished > 0 else 0
        
        return {
            "total_appointments": total,
            "by_status": by_status,
            "upcoming_count": upcoming_count,
            "completion_rate": round(completion_rate, 2),
            "no_show_rate": round(no_show_rate, 2),
            "total_patients": len(unique_patients)
        }
    
    async def get_upcoming_appointments(
        self,
        dentist_id: UUID,
        limit: int,
        current_user: User
    ) -> List[Appointment]:
        """
        Get upcoming appointments for a specific dentist.
        
        Args:
            dentist_id: ID of the dentist
            limit: Maximum number of appointments to return
            current_user: User making the request
            
        Returns:
            List of upcoming appointments
            
        Raises:
            AuthorizationError: If user doesn't have permission
        """
        # Only dentists can see their own upcoming appointments
        if current_user.role == UserRole.DENTIST and current_user.id != dentist_id:
            raise AuthorizationError("Solo puede ver sus propias citas")
        
        return await self.repository.get_upcoming_appointments(
            dentist_id=dentist_id,
            limit=limit
        )


