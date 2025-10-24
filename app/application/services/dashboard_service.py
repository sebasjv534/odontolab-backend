"""
Dashboard service for the OdontoLab system.

This module provides business logic for dashboard statistics.
"""

from uuid import UUID
from datetime import datetime, timedelta

from app.domain.models import User, UserRole
from app.domain.schemas.dashboard_schemas import (
    AdminDashboardStats,
    DentistDashboardStats,
    ReceptionistDashboardStats
)
from app.insfraestructure.repositories import (
    UserRepository,
    PatientRepository,
    MedicalRecordRepository,
    ContactRequestRepository
)
from app.application.exceptions import PermissionError


class DashboardService:
    """Service for dashboard statistics operations."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        patient_repository: PatientRepository,
        medical_record_repository: MedicalRecordRepository,
        contact_repository: ContactRequestRepository
    ):
        """Initialize the dashboard service."""
        self.user_repository = user_repository
        self.patient_repository = patient_repository
        self.medical_record_repository = medical_record_repository
        self.contact_repository = contact_repository
    
    async def get_admin_dashboard_stats(self) -> AdminDashboardStats:
        """Get dashboard statistics for administrators."""
        # Get user counts
        total_users = await self.user_repository.count_active_users()
        total_dentists = await self.user_repository.count_by_role(UserRole.DENTIST)
        total_receptionists = await self.user_repository.count_by_role(UserRole.RECEPTIONIST)
        
        # Get patient counts
        total_patients = await self.patient_repository.count()
        recent_patients = await self.patient_repository.count_recent(days=30)
        
        # Get medical record counts
        total_records = await self.medical_record_repository.count()
        recent_records = await self.medical_record_repository.count_recent(days=30)
        
        # Get contact request counts
        total_contacts = await self.contact_repository.count()
        pending_contacts = await self.contact_repository.count_by_status("pending")
        
        # Get upcoming appointments
        upcoming_appointments = await self.medical_record_repository.get_upcoming_appointments()
        upcoming_appointments_count = len(upcoming_appointments)
        
        return AdminDashboardStats(
            total_users=total_users,
            total_dentists=total_dentists,
            total_receptionists=total_receptionists,
            total_patients=total_patients,
            recent_patients=recent_patients,
            total_medical_records=total_records,
            recent_medical_records=recent_records,
            pending_contact_requests=pending_contacts,
            total_contact_requests=total_contacts,
            upcoming_appointments=upcoming_appointments_count
        )
    
    async def get_dentist_dashboard_stats(self, dentist_id: UUID) -> DentistDashboardStats:
        """Get dashboard statistics for dentists."""
        # Get patient count (unique patients treated)
        total_patients = await self.medical_record_repository.count_unique_patients_by_dentist(dentist_id)
        
        # Get medical record counts
        records, total_records = await self.medical_record_repository.get_by_dentist(
            dentist_id=dentist_id,
            skip=0,
            limit=1000000  # Get all to count
        )
        
        # Get recent records
        recent_records = await self.medical_record_repository.count_recent_by_dentist(
            dentist_id,
            days=30
        )
        
        # Get upcoming appointments for this dentist
        upcoming_appointments = await self.medical_record_repository.get_upcoming_appointments(
            dentist_id=dentist_id
        )
        upcoming_appointments_count = len(upcoming_appointments)
        
        # Calculate today's appointments
        today = datetime.now().date()
        today_appointments = sum(
            1 for appt in upcoming_appointments 
            if appt.next_appointment and appt.next_appointment.date() == today
        )
        
        return DentistDashboardStats(
            total_patients=total_patients,
            total_medical_records=total_records,
            recent_medical_records=recent_records,
            upcoming_appointments=upcoming_appointments_count,
            today_appointments=today_appointments
        )
    
    async def get_receptionist_dashboard_stats(
        self,
        receptionist_id: UUID
    ) -> ReceptionistDashboardStats:
        """Get dashboard statistics for receptionists."""
        # Get patient counts created by this receptionist
        total_patients = await self.patient_repository.count_by_creator(receptionist_id)
        recent_patients = await self.patient_repository.count_recent(days=30)
        
        # Get contact request counts (all, as they manage these)
        total_contacts = await self.contact_repository.count()
        pending_contacts = await self.contact_repository.count_by_status("pending")
        
        # Get upcoming appointments (all)
        upcoming_appointments = await self.medical_record_repository.get_upcoming_appointments()
        upcoming_appointments_count = len(upcoming_appointments)
        
        # Calculate today's appointments
        today = datetime.now().date()
        today_appointments = sum(
            1 for appt in upcoming_appointments 
            if appt.next_appointment and appt.next_appointment.date() == today
        )
        
        return ReceptionistDashboardStats(
            total_patients=total_patients,
            recent_patients=recent_patients,
            pending_contact_requests=pending_contacts,
            total_contact_requests=total_contacts,
            upcoming_appointments=upcoming_appointments_count,
            today_appointments=today_appointments
        )
    
    async def get_dashboard_stats_by_role(self, current_user: User):
        """Get dashboard statistics based on user role."""
        if current_user.role == UserRole.ADMIN:
            return await self.get_admin_dashboard_stats()
        elif current_user.role == UserRole.DENTIST:
            return await self.get_dentist_dashboard_stats(current_user.id)
        elif current_user.role == UserRole.RECEPTIONIST:
            return await self.get_receptionist_dashboard_stats(current_user.id)
        else:
            raise PermissionError("Invalid user role")
