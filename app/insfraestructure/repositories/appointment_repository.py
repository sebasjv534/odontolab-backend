"""
SQLAlchemy implementation of appointment repository.

This module provides the concrete implementation of appointment repository
using SQLAlchemy for database operations with PostgreSQL.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date, time, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, func, String

from app.domain.models import Appointment, AppointmentReminder, Patient, User
from app.domain.models.enums import AppointmentStatus, ReminderType
from app.application.exceptions import (
    AppointmentNotFoundError,
    AppointmentConflictError,
    ValidationError
)


class AppointmentRepository:
    """
    SQLAlchemy implementation of the appointment repository.
    
    This repository handles all database operations related to appointments
    including CRUD operations, conflict detection, and availability checks.
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize the appointment repository with database session."""
        self.session = session
    
    async def create(self, appointment_data: Dict[str, Any]) -> Appointment:
        """
        Create a new appointment.
        
        Args:
            appointment_data: Dictionary containing appointment data
            
        Returns:
            Created Appointment instance
            
        Raises:
            AppointmentConflictError: If there's a scheduling conflict
            ValidationError: If validation fails
        """
        # Check for conflicts before creating
        await self._check_conflicts(
            dentist_id=appointment_data['dentist_id'],
            scheduled_time=appointment_data['scheduled_time'],
            duration_minutes=appointment_data.get('duration_minutes', 30)
        )
        
        appointment = Appointment(**appointment_data)
        self.session.add(appointment)
        
        try:
            await self.session.commit()
            await self.session.refresh(appointment)
            return appointment
        except IntegrityError as e:
            await self.session.rollback()
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def get_by_id(self, appointment_id: UUID, load_relations: bool = False) -> Optional[Appointment]:
        """
        Retrieve an appointment by ID.
        
        Args:
            appointment_id: UUID of the appointment
            load_relations: Whether to eager load patient and dentist relationships
            
        Returns:
            Appointment instance if found, None otherwise
        """
        query = select(Appointment).where(Appointment.id == appointment_id)
        
        if load_relations:
            query = query.options(
                selectinload(Appointment.patient),
                selectinload(Appointment.dentist),
                selectinload(Appointment.creator),
                selectinload(Appointment.reminders)
            )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_id_or_raise(self, appointment_id: UUID, load_relations: bool = False) -> Appointment:
        """
        Retrieve an appointment by ID or raise exception.
        
        Raises:
            AppointmentNotFoundError: If appointment is not found
        """
        appointment = await self.get_by_id(appointment_id, load_relations)
        if not appointment:
            raise AppointmentNotFoundError(f"Appointment with ID {appointment_id} not found")
        return appointment
    
    async def update(self, appointment_id: UUID, update_data: Dict[str, Any]) -> Appointment:
        """
        Update an appointment.
        
        Args:
            appointment_id: UUID of the appointment to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated Appointment instance
            
        Raises:
            AppointmentNotFoundError: If appointment is not found
            AppointmentConflictError: If new time creates a conflict
        """
        appointment = await self.get_by_id_or_raise(appointment_id)
        
        # If updating schedule, check for conflicts
        if 'scheduled_time' in update_data or 'duration_minutes' in update_data:
            await self._check_conflicts(
                dentist_id=appointment.dentist_id,
                scheduled_time=update_data.get('scheduled_time', appointment.scheduled_time),
                duration_minutes=update_data.get('duration_minutes', appointment.duration_minutes),
                exclude_appointment_id=appointment_id
            )
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(appointment, key):
                setattr(appointment, key, value)
        
        appointment.updated_at = datetime.utcnow()
        
        try:
            await self.session.commit()
            await self.session.refresh(appointment)
            return appointment
        except IntegrityError as e:
            await self.session.rollback()
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def delete(self, appointment_id: UUID) -> bool:
        """
        Delete an appointment.
        
        Args:
            appointment_id: UUID of the appointment to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            AppointmentNotFoundError: If appointment is not found
        """
        appointment = await self.get_by_id_or_raise(appointment_id)
        await self.session.delete(appointment)
        await self.session.commit()
        return True
    
    async def list_appointments(
        self,
        patient_id: Optional[UUID] = None,
        dentist_id: Optional[UUID] = None,
        status: Optional[AppointmentStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
        load_relations: bool = True
    ) -> tuple[List[Appointment], int]:
        """
        List appointments with optional filters and pagination.
        
        Args:
            patient_id: Filter by patient
            dentist_id: Filter by dentist
            status: Filter by status
            start_date: Filter by start date (inclusive)
            end_date: Filter by end date (inclusive)
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            load_relations: Whether to eager load relationships
            
        Returns:
            Tuple of (list of appointments, total count)
        """
        # Build base query
        query = select(Appointment)
        count_query = select(func.count(Appointment.id))
        
        # Apply filters
        filters = []
        if patient_id:
            filters.append(Appointment.patient_id == patient_id)
        if dentist_id:
            filters.append(Appointment.dentist_id == dentist_id)
        if status:
            filters.append(Appointment.status == status)
        if start_date:
            filters.append(Appointment.scheduled_time >= datetime.combine(start_date, time.min))
        if end_date:
            filters.append(Appointment.scheduled_time <= datetime.combine(end_date, time.max))
        
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Get total count
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()
        
        # Apply ordering, pagination, and eager loading
        query = query.order_by(Appointment.scheduled_time.asc())
        query = query.offset(skip).limit(limit)
        
        if load_relations:
            query = query.options(
                selectinload(Appointment.patient),
                selectinload(Appointment.dentist),
                selectinload(Appointment.creator)
            )
        
        result = await self.session.execute(query)
        appointments = result.scalars().all()
        
        return list(appointments), total
    
    async def _check_conflicts(
        self,
        dentist_id: UUID,
        scheduled_time: datetime,
        duration_minutes: int,
        exclude_appointment_id: Optional[UUID] = None
    ) -> None:
        """
        Check for scheduling conflicts for a dentist.
        
        Args:
            dentist_id: UUID of the dentist
            scheduled_time: Proposed appointment time
            duration_minutes: Duration of the appointment
            exclude_appointment_id: Appointment ID to exclude from check (for updates)
            
        Raises:
            AppointmentConflictError: If there's a scheduling conflict
        """
        end_time = scheduled_time + timedelta(minutes=duration_minutes)
        
        # Query for overlapping appointments
        query = select(Appointment).where(
            and_(
                Appointment.dentist_id == dentist_id,
                Appointment.status.in_([
                    AppointmentStatus.SCHEDULED,
                    AppointmentStatus.CONFIRMED,
                    AppointmentStatus.IN_PROGRESS
                ]),
                or_(
                    # New appointment starts during existing appointment
                    and_(
                        Appointment.scheduled_time <= scheduled_time,
                        func.datetime(Appointment.scheduled_time, '+' + func.cast(Appointment.duration_minutes, String) + ' minutes') > scheduled_time
                    ),
                    # New appointment ends during existing appointment
                    and_(
                        Appointment.scheduled_time < end_time,
                        func.datetime(Appointment.scheduled_time, '+' + func.cast(Appointment.duration_minutes, String) + ' minutes') >= end_time
                    ),
                    # New appointment completely contains existing appointment
                    and_(
                        Appointment.scheduled_time >= scheduled_time,
                        func.datetime(Appointment.scheduled_time, '+' + func.cast(Appointment.duration_minutes, String) + ' minutes') <= end_time
                    )
                )
            )
        )
        
        if exclude_appointment_id:
            query = query.where(Appointment.id != exclude_appointment_id)
        
        result = await self.session.execute(query)
        conflicts = result.scalars().all()
        
        if conflicts:
            conflict = conflicts[0]
            raise AppointmentConflictError(
                f"Scheduling conflict detected. Dentist already has an appointment at "
                f"{conflict.scheduled_time.isoformat()}"
            )
    
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
            slot_duration: Duration of each time slot in minutes
            
        Returns:
            List of time slots with availability status
        """
        # Get all appointments for the dentist on the specified date
        start_datetime = datetime.combine(check_date, start_time)
        end_datetime = datetime.combine(check_date, end_time)
        
        query = select(Appointment).where(
            and_(
                Appointment.dentist_id == dentist_id,
                Appointment.scheduled_time >= start_datetime,
                Appointment.scheduled_time < end_datetime,
                Appointment.status.in_([
                    AppointmentStatus.SCHEDULED,
                    AppointmentStatus.CONFIRMED,
                    AppointmentStatus.IN_PROGRESS
                ])
            )
        ).order_by(Appointment.scheduled_time)
        
        result = await self.session.execute(query)
        existing_appointments = result.scalars().all()
        
        # Generate time slots
        slots = []
        current_time = start_datetime
        
        while current_time < end_datetime:
            slot_end = current_time + timedelta(minutes=slot_duration)
            if slot_end > end_datetime:
                break
            
            # Check if slot overlaps with any existing appointment
            is_available = True
            for apt in existing_appointments:
                apt_end = apt.end_time
                if not (slot_end <= apt.scheduled_time or current_time >= apt_end):
                    is_available = False
                    break
            
            slots.append({
                "start_time": current_time,
                "end_time": slot_end,
                "available": is_available
            })
            
            current_time = slot_end
        
        return slots
    
    async def get_upcoming_appointments(
        self,
        dentist_id: Optional[UUID] = None,
        patient_id: Optional[UUID] = None,
        days_ahead: int = 7,
        limit: int = 50
    ) -> List[Appointment]:
        """
        Get upcoming appointments for a dentist or patient.
        
        Args:
            dentist_id: Filter by dentist
            patient_id: Filter by patient
            days_ahead: Number of days to look ahead
            limit: Maximum number of appointments to return
            
        Returns:
            List of upcoming appointments
        """
        now = datetime.now()
        future_date = now + timedelta(days=days_ahead)
        
        query = select(Appointment).where(
            and_(
                Appointment.scheduled_time >= now,
                Appointment.scheduled_time <= future_date,
                Appointment.status.in_([
                    AppointmentStatus.SCHEDULED,
                    AppointmentStatus.CONFIRMED
                ])
            )
        )
        
        if dentist_id:
            query = query.where(Appointment.dentist_id == dentist_id)
        if patient_id:
            query = query.where(Appointment.patient_id == patient_id)
        
        query = query.order_by(Appointment.scheduled_time.asc()).limit(limit)
        query = query.options(
            selectinload(Appointment.patient),
            selectinload(Appointment.dentist)
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
