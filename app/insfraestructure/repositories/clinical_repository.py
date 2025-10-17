"""
SQLAlchemy implementation of clinical repository interfaces.

This module provides the concrete implementation of clinical repositories
using SQLAlchemy for database operations with PostgreSQL.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, func

from app.domain.models.clinical_models import Patient, ClinicalIntervention
from app.application.interfaces.clinical_repository import IPatientRepository, IClinicalInterventionRepository
from app.application.exceptions import ValidationError, PatientAlreadyExistsError


class PatientRepository(IPatientRepository):
    """
    SQLAlchemy implementation of the patient repository interface.
    
    This repository handles all database operations related to patients.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the patient repository.
        
        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        self.session = session
    
    async def get_by_id(self, patient_id: UUID) -> Optional[Patient]:
        """
        Retrieve a patient by ID.
        
        Args:
            patient_id (UUID): The patient ID to search for
            
        Returns:
            Optional[Patient]: The patient if found, None otherwise
        """
        result = await self.session.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_patient_number(self, patient_number: str) -> Optional[Patient]:
        """
        Retrieve a patient by document number.
        
        Args:
            patient_number (str): The document number to search for
            
        Returns:
            Optional[Patient]: The patient if found, None otherwise
        """
        result = await self.session.execute(
            select(Patient).where(Patient.document_number == patient_number)
        )
        return result.scalar_one_or_none()
    
    async def create(self, patient: Patient) -> Patient:
        """
        Create a new patient.
        
        Args:
            patient (Patient): The patient entity to create
            
        Returns:
            Patient: The created patient with assigned ID
            
        Raises:
            PatientAlreadyExistsError: If patient with document already exists
        """
        try:
            self.session.add(patient)
            await self.session.commit()
            await self.session.refresh(patient)
            return patient
        except IntegrityError as e:
            await self.session.rollback()
            if "unique constraint" in str(e).lower():
                raise PatientAlreadyExistsError("Patient with this document number already exists")
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def update(self, patient: Patient) -> Patient:
        """
        Update an existing patient.
        
        Args:
            patient (Patient): The patient entity to update
            
        Returns:
            Patient: The updated patient
        """
        try:
            await self.session.merge(patient)
            await self.session.commit()
            await self.session.refresh(patient)
            return patient
        except IntegrityError as e:
            await self.session.rollback()
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def delete(self, patient_id: UUID) -> bool:
        """
        Delete a patient by ID.
        
        Args:
            patient_id (UUID): The ID of the patient to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        result = await self.session.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        patient = result.scalar_one_or_none()
        
        if patient:
            await self.session.delete(patient)
            await self.session.commit()
            return True
        return False
    
    async def list_patients(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """
        List patients with pagination.
        
        Args:
            skip (int): Number of patients to skip
            limit (int): Maximum number of patients to return
            
        Returns:
            List[Patient]: List of patients
        """
        result = await self.session.execute(
            select(Patient)
            .offset(skip)
            .limit(limit)
            .order_by(Patient.created_at.desc())
        )
        return result.scalars().all()
    
    async def search_patients(self, query: str) -> List[Patient]:
        """
        Search patients by name, email, or document number.
        
        Args:
            query (str): Search query
            
        Returns:
            List[Patient]: List of matching patients
        """
        search_term = f"%{query}%"
        result = await self.session.execute(
            select(Patient).where(
                or_(
                    Patient.first_name.ilike(search_term),
                    Patient.last_name.ilike(search_term),
                    Patient.document_number.ilike(search_term),
                    Patient.email.ilike(search_term),
                    func.concat(Patient.first_name, ' ', Patient.last_name).ilike(search_term)
                )
            ).order_by(Patient.created_at.desc())
        )
        return result.scalars().all()
    
    async def generate_patient_number(self) -> str:
        """
        Generate a unique patient number.
        
        Returns:
            str: Unique patient number
        """
        # Simple implementation - in production, you might want a more sophisticated approach
        result = await self.session.execute(
            select(func.count(Patient.id))
        )
        count = result.scalar()
        return f"P{count + 1:06d}"


class ClinicalInterventionRepository(IClinicalInterventionRepository):
    """
    SQLAlchemy implementation of the clinical intervention repository interface.
    
    This repository handles all database operations related to clinical interventions.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the clinical intervention repository.
        
        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        self.session = session
    
    async def get_by_id(self, intervention_id: UUID) -> Optional[Intervention]:
        """
        Retrieve a clinical intervention by ID.
        
        Args:
            intervention_id (UUID): The intervention ID to search for
            
        Returns:
            Optional[ClinicalIntervention]: The intervention if found, None otherwise
        """
        result = await self.session.execute(
            select(Intervention).where(Intervention.id == intervention_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, intervention: Intervention) -> Intervention:
        """
        Create a new clinical intervention.
        
        Args:
            intervention (ClinicalIntervention): The intervention entity to create
            
        Returns:
            ClinicalIntervention: The created intervention with assigned ID
        """
        try:
            self.session.add(intervention)
            await self.session.commit()
            await self.session.refresh(intervention)
            return intervention
        except IntegrityError as e:
            await self.session.rollback()
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def update(self, intervention: Intervention) -> Intervention:
        """
        Update an existing clinical intervention.
        
        Args:
            intervention (ClinicalIntervention): The intervention entity to update
            
        Returns:
            ClinicalIntervention: The updated intervention
        """
        try:
            await self.session.merge(intervention)
            await self.session.commit()
            await self.session.refresh(intervention)
            return intervention
        except IntegrityError as e:
            await self.session.rollback()
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def delete(self, intervention_id: UUID) -> bool:
        """
        Delete a clinical intervention by ID.
        
        Args:
            intervention_id (UUID): The ID of the intervention to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        result = await self.session.execute(
            select(Intervention).where(Intervention.id == intervention_id)
        )
        intervention = result.scalar_one_or_none()
        
        if intervention:
            await self.session.delete(intervention)
            await self.session.commit()
            return True
        return False
    
    async def get_by_patient_id(self, patient_id: UUID) -> List[Intervention]:
        """
        Get all interventions for a specific patient.
        
        Args:
            patient_id (UUID): The patient ID
            
        Returns:
            List[ClinicalIntervention]: List of interventions for the patient
        """
        # Note: This requires joining through clinical_records table
        result = await self.session.execute(
            select(Intervention)
            .join(ClinicalRecord)
            .where(ClinicalRecord.patient_id == patient_id)
            .order_by(Intervention.performed_at.desc())
        )
        return result.scalars().all()
    
    async def get_by_dentist_id(self, dentist_id: UUID) -> List[Intervention]:
        """
        Get all interventions performed by a specific dentist.
        
        Args:
            dentist_id (UUID): The dentist profile ID
            
        Returns:
            List[ClinicalIntervention]: List of interventions by the dentist
        """
        result = await self.session.execute(
            select(Intervention)
            .where(Intervention.dentist_id == dentist_id)
            .order_by(Intervention.performed_at.desc())
        )
        return result.scalars().all()
    
    async def list_interventions(self, skip: int = 0, limit: int = 100) -> List[Intervention]:
        """
        List interventions with pagination.
        
        Args:
            skip (int): Number of interventions to skip
            limit (int): Maximum number of interventions to return
            
        Returns:
            List[ClinicalIntervention]: List of interventions
        """
        result = await self.session.execute(
            select(Intervention)
            .offset(skip)
            .limit(limit)
            .order_by(Intervention.performed_at.desc())
        )
        return result.scalars().all()