"""
Patient service for the OdontoLab system.

This module provides business logic for patient management operations.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime

from app.domain.models import Patient, User, UserRole
from app.domain.schemas.patient_schemas import PatientCreate, PatientUpdate
from app.insfraestructure.repositories import PatientRepository
from app.application.exceptions import NotFoundError, ValidationError, PermissionError


class PatientService:
    """Service for patient management operations."""
    
    def __init__(self, patient_repository: PatientRepository):
        """Initialize the patient service."""
        self.patient_repository = patient_repository
    
    async def create_patient(self, patient_data: PatientCreate, current_user: User) -> Patient:
        """Create a new patient."""
        patient_dict = patient_data.model_dump()
        patient_dict['created_by'] = current_user.id
        patient = await self.patient_repository.create(patient_dict)
        return patient
    
    async def get_patient_by_id(self, patient_id: UUID, current_user: User) -> Patient:
        """Get patient by ID."""
        patient = await self.patient_repository.get_by_id(patient_id)
        if not patient:
            raise NotFoundError("Patient not found")
        
        # Receptionists can only view patients they created
        if current_user.role == UserRole.RECEPTIONIST and patient.created_by != current_user.id:
            raise PermissionError("You don't have permission to view this patient")
        
        return patient
    
    async def get_all_patients(
        self,
        page: int = 1,
        per_page: int = 10,
        current_user: User = None
    ) -> tuple[list[Patient], int]:
        """Get all patients with pagination."""
        skip = (page - 1) * per_page
        
        # Receptionists can only see patients they created
        if current_user and current_user.role == UserRole.RECEPTIONIST:
            patients, total = await self.patient_repository.get_by_creator(
                creator_id=current_user.id,
                skip=skip,
                limit=per_page
            )
        else:
            patients, total = await self.patient_repository.get_all(
                skip=skip,
                limit=per_page
            )
        
        return patients, total
    
    async def search_patients(
        self,
        search_term: str,
        page: int = 1,
        per_page: int = 10,
        current_user: User = None
    ) -> tuple[list[Patient], int]:
        """Search patients by name, email, or phone."""
        skip = (page - 1) * per_page
        
        # If receptionist, limit search to their patients
        creator_id = current_user.id if current_user and current_user.role == UserRole.RECEPTIONIST else None
        
        patients, total = await self.patient_repository.search(
            search_term=search_term,
            skip=skip,
            limit=per_page,
            creator_id=creator_id
        )
        return patients, total
    
    async def update_patient(
        self,
        patient_id: UUID,
        patient_data: PatientUpdate,
        current_user: User
    ) -> Patient:
        """Update patient information."""
        # Check if patient exists
        patient = await self.patient_repository.get_by_id(patient_id)
        if not patient:
            raise NotFoundError("Patient not found")
        
        # Receptionists can only update patients they created
        if current_user.role == UserRole.RECEPTIONIST and patient.created_by != current_user.id:
            raise PermissionError("You don't have permission to update this patient")
        
        # Update patient
        patient_dict = patient_data.model_dump(exclude_unset=True)
        updated_patient = await self.patient_repository.update(patient_id, patient_dict)
        return updated_patient
    
    async def delete_patient(self, patient_id: UUID, current_user: User) -> bool:
        """Delete a patient (Admin only)."""
        if current_user.role != UserRole.ADMIN:
            raise PermissionError("Only administrators can delete patients")
        
        success = await self.patient_repository.delete(patient_id)
        if not success:
            raise NotFoundError("Patient not found")
        return success
    
    async def count_recent_patients(self, days: int = 30) -> int:
        """Count patients created in the last N days."""
        return await self.patient_repository.count_recent(days)
    
    async def count_patients_by_creator(self, creator_id: UUID) -> int:
        """Count patients created by a specific user."""
        return await self.patient_repository.count_by_creator(creator_id)
