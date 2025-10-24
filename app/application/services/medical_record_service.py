"""
Medical Record service for the OdontoLab system.

This module provides business logic for medical record management operations.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime

from app.domain.models import MedicalRecord, User, UserRole
from app.domain.schemas.medical_record_schemas import MedicalRecordCreate, MedicalRecordUpdate
from app.insfraestructure.repositories import MedicalRecordRepository, PatientRepository
from app.application.exceptions import NotFoundError, ValidationError, PermissionError


class MedicalRecordService:
    """Service for medical record management operations."""
    
    def __init__(
        self,
        medical_record_repository: MedicalRecordRepository,
        patient_repository: PatientRepository
    ):
        """Initialize the medical record service."""
        self.medical_record_repository = medical_record_repository
        self.patient_repository = patient_repository
    
    async def create_medical_record(
        self,
        record_data: MedicalRecordCreate,
        current_user: User
    ) -> MedicalRecord:
        """Create a new medical record (Dentist only)."""
        if current_user.role != UserRole.DENTIST:
            raise PermissionError("Only dentists can create medical records")
        
        # Verify patient exists
        patient = await self.patient_repository.get_by_id(record_data.patient_id)
        if not patient:
            raise NotFoundError("Patient not found")
        
        # Create medical record
        record_dict = record_data.model_dump()
        record_dict['dentist_id'] = current_user.id
        record = await self.medical_record_repository.create(record_dict)
        return record
    
    async def get_medical_record_by_id(
        self,
        record_id: UUID,
        current_user: User
    ) -> MedicalRecord:
        """Get medical record by ID."""
        record = await self.medical_record_repository.get_by_id(record_id)
        if not record:
            raise NotFoundError("Medical record not found")
        
        # Dentists can only view their own records (unless admin)
        if (current_user.role == UserRole.DENTIST and 
            record.dentist_id != current_user.id and
            current_user.role != UserRole.ADMIN):
            raise PermissionError("You don't have permission to view this medical record")
        
        return record
    
    async def get_all_medical_records(
        self,
        page: int = 1,
        per_page: int = 10,
        current_user: User = None
    ) -> tuple[list[MedicalRecord], int]:
        """Get all medical records with pagination."""
        skip = (page - 1) * per_page
        
        # Dentists can only see their own records
        if current_user and current_user.role == UserRole.DENTIST:
            records, total = await self.medical_record_repository.get_by_dentist(
                dentist_id=current_user.id,
                skip=skip,
                limit=per_page
            )
        else:
            records, total = await self.medical_record_repository.get_all(
                skip=skip,
                limit=per_page
            )
        
        return records, total
    
    async def get_records_by_patient(
        self,
        patient_id: UUID,
        current_user: User
    ) -> list[MedicalRecord]:
        """Get all medical records for a specific patient."""
        # Verify patient exists
        patient = await self.patient_repository.get_by_id(patient_id)
        if not patient:
            raise NotFoundError("Patient not found")
        
        # Receptionists can only view records for patients they created
        if current_user.role == UserRole.RECEPTIONIST and patient.created_by != current_user.id:
            raise PermissionError("You don't have permission to view this patient's records")
        
        records = await self.medical_record_repository.get_by_patient(patient_id)
        return records
    
    async def update_medical_record(
        self,
        record_id: UUID,
        record_data: MedicalRecordUpdate,
        current_user: User
    ) -> MedicalRecord:
        """Update medical record (Only by the dentist who created it or admin)."""
        # Check if record exists
        record = await self.medical_record_repository.get_by_id(record_id)
        if not record:
            raise NotFoundError("Medical record not found")
        
        # Only the dentist who created it or admin can update
        if (current_user.role == UserRole.DENTIST and 
            record.dentist_id != current_user.id):
            raise PermissionError("You can only update your own medical records")
        
        if current_user.role == UserRole.RECEPTIONIST:
            raise PermissionError("Receptionists cannot update medical records")
        
        # Update record
        record_dict = record_data.model_dump(exclude_unset=True)
        updated_record = await self.medical_record_repository.update(record_id, record_dict)
        return updated_record
    
    async def delete_medical_record(
        self,
        record_id: UUID,
        current_user: User
    ) -> bool:
        """Delete a medical record (Admin only)."""
        if current_user.role != UserRole.ADMIN:
            raise PermissionError("Only administrators can delete medical records")
        
        success = await self.medical_record_repository.delete(record_id)
        if not success:
            raise NotFoundError("Medical record not found")
        return success
    
    async def get_upcoming_appointments(
        self,
        dentist_id: Optional[UUID] = None
    ) -> list[MedicalRecord]:
        """Get upcoming appointments."""
        return await self.medical_record_repository.get_upcoming_appointments(dentist_id)
    
    async def count_unique_patients_by_dentist(self, dentist_id: UUID) -> int:
        """Count unique patients treated by a dentist."""
        return await self.medical_record_repository.count_unique_patients_by_dentist(dentist_id)
    
    async def count_recent_records_by_dentist(
        self,
        dentist_id: UUID,
        days: int = 30
    ) -> int:
        """Count recent medical records by a dentist."""
        return await self.medical_record_repository.count_recent_by_dentist(dentist_id, days)
