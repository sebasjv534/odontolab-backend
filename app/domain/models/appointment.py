"""
Appointment models for the OdontoLab system.

This module defines the Appointment and AppointmentReminder entities
for managing dental clinic appointments and automated reminders.
"""

import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from app.domain.models.enums import AppointmentStatus, ReminderType


class Appointment(Base):
    """
    Appointment model for managing dental clinic appointments.
    
    This model handles appointment scheduling, tracking, and conflict detection.
    Supports the complete appointment lifecycle from scheduling to completion.
    
    Attributes:
        id (UUID): Unique identifier for the appointment
        patient_id (UUID): Foreign key to the patient
        dentist_id (UUID): Foreign key to the dentist (User with DENTIST role)
        scheduled_time (datetime): Date and time of the appointment
        duration_minutes (int): Duration in minutes (default: 30)
        status (AppointmentStatus): Current appointment status
        reason (str): Reason for the appointment (optional)
        notes (str): Additional notes about the appointment (optional)
        created_by (UUID): Foreign key to user who created the appointment
        created_at (datetime): Appointment creation timestamp
        updated_at (datetime): Last update timestamp
        
    Relationships:
        patient: Many-to-one relationship with Patient
        dentist: Many-to-one relationship with User (dentist)
        creator: Many-to-one relationship with User (who created it)
        reminders: One-to-many relationship with AppointmentReminder
        
    Business Rules:
        - scheduled_time must be in the future
        - No overlapping appointments for the same dentist
        - Status transitions must follow defined workflow
        - Duration must be positive and reasonable (5-480 minutes)
    """
    __tablename__ = "appointments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), 
                       nullable=False, index=True)
    dentist_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), 
                       nullable=False, index=True)
    scheduled_time = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False, default=30)
    status = Column(SQLAEnum(AppointmentStatus), nullable=False, 
                   default=AppointmentStatus.SCHEDULED, index=True)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default="now()")
    updated_at = Column(DateTime(timezone=True), server_default="now()", onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments", foreign_keys=[patient_id])
    dentist = relationship("User", back_populates="appointments_as_dentist", foreign_keys=[dentist_id])
    creator = relationship("User", back_populates="appointments_created", foreign_keys=[created_by])
    reminders = relationship("AppointmentReminder", back_populates="appointment", 
                           cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Appointment(id='{self.id}', patient_id='{self.patient_id}', scheduled_time='{self.scheduled_time}')>"
    
    @property
    def end_time(self) -> datetime:
        """Calculates and returns the appointment end time."""
        return self.scheduled_time + timedelta(minutes=self.duration_minutes)
    
    @property
    def is_past(self) -> bool:
        """Returns True if the appointment is in the past."""
        return self.scheduled_time < datetime.now(self.scheduled_time.tzinfo)
    
    @property
    def is_today(self) -> bool:
        """Returns True if the appointment is scheduled for today."""
        now = datetime.now(self.scheduled_time.tzinfo)
        return self.scheduled_time.date() == now.date()
    
    def can_be_cancelled(self) -> bool:
        """
        Returns True if the appointment can be cancelled.
        
        Business rules:
        - Cannot cancel completed appointments
        - Cannot cancel already cancelled appointments
        - Cannot cancel no-show appointments
        """
        return self.status not in [
            AppointmentStatus.COMPLETED,
            AppointmentStatus.CANCELLED,
            AppointmentStatus.NO_SHOW
        ]
    
    def can_be_confirmed(self) -> bool:
        """Returns True if the appointment can be confirmed."""
        return self.status == AppointmentStatus.SCHEDULED
    
    def can_start(self) -> bool:
        """Returns True if the appointment can be started (moved to IN_PROGRESS)."""
        return self.status in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]
    
    def can_complete(self) -> bool:
        """Returns True if the appointment can be completed."""
        return self.status == AppointmentStatus.IN_PROGRESS


class AppointmentReminder(Base):
    """
    Appointment reminder model for automated notifications.
    
    This model manages automated reminders sent to patients before their appointments.
    Supports multiple notification channels (email, SMS, WhatsApp).
    
    Attributes:
        id (UUID): Unique identifier for the reminder
        appointment_id (UUID): Foreign key to the appointment
        reminder_type (ReminderType): Type of reminder (email, SMS, WhatsApp)
        scheduled_for (datetime): When to send the reminder
        sent (bool): Whether the reminder has been sent
        sent_at (datetime): When the reminder was actually sent (optional)
        created_at (datetime): Reminder creation timestamp
        
    Relationships:
        appointment: Many-to-one relationship with Appointment
        
    Business Rules:
        - scheduled_for should be before appointment.scheduled_time
        - Once sent=True, cannot be resent
        - Typical configuration: 24h before (email), 2h before (SMS)
    """
    __tablename__ = "appointment_reminders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id", ondelete="CASCADE"), 
                           nullable=False, index=True)
    reminder_type = Column(SQLAEnum(ReminderType), nullable=False)
    scheduled_for = Column(DateTime(timezone=True), nullable=False, index=True)
    sent = Column(Boolean, nullable=False, default=False, index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default="now()")
    
    # Relationships
    appointment = relationship("Appointment", back_populates="reminders")
    
    def __repr__(self) -> str:
        return f"<AppointmentReminder(id='{self.id}', type='{self.reminder_type}', sent={self.sent})>"
    
    @property
    def is_due(self) -> bool:
        """Returns True if the reminder should be sent now."""
        if self.sent:
            return False
        now = datetime.now(self.scheduled_for.tzinfo)
        return self.scheduled_for <= now
    
    def mark_as_sent(self):
        """Marks the reminder as sent with current timestamp."""
        self.sent = True
        self.sent_at = datetime.utcnow()
