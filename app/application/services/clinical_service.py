"""
Clinical service for the odontology system.

This module provides clinical services including patient management,
clinical records, and intervention management for dental operations.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.domain.models.clinical_models import Patient, ClinicalRecord, Intervention
from app.domain.schemas.clinical_schemas import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    ClinicalRecordCreate,
    ClinicalRecordUpdate,
    ClinicalRecordResponse,
    InterventionCreate,
    InterventionUpdate,
    InterventionResponse
)
from app.application.interfaces.clinical_repository import IPatientRepository, IClinicalInterventionRepository
from app.application.exceptions import (
    PatientNotFoundError,
    PatientAlreadyExistsError,
    ClinicalRecordNotFoundError,
    InterventionNotFoundError,
    ValidationError
)


class PatientService:
    """
    Patient management service for handling patient operations.
    
    This service manages patient registration, updates, and retrieval
    for the dental clinic system.
    """
    
    def __init__(self, patient_repository: IPatientRepository):
        """
        Initialize the patient service.
        
        Args:
            patient_repository (IPatientRepository): Patient repository implementation
        """
        self.patient_repository = patient_repository
    
    async def create_patient(self, patient_data: PatientCreate, registered_by_id: UUID) -> PatientResponse:
        """
        Create a new patient record.
        
        Args:
            patient_data (PatientCreate): Patient creation data
            registered_by_id (UUID): ID of the receptionist registering the patient
            
        Returns:
            PatientResponse: Created patient details
            
        Raises:
            PatientAlreadyExistsError: If patient with document already exists
            ValidationError: If patient data is invalid
        """
        # Check if patient already exists by document number
        existing_patient = await self.patient_repository.get_by_patient_number(patient_data.document_number)
        if existing_patient:
            raise PatientAlreadyExistsError(f"Patient with document {patient_data.document_number} already exists")
        
        try:
            # Create patient entity
            patient = Patient(
                first_name=patient_data.first_name,
                last_name=patient_data.last_name,
                document_type=patient_data.document_type,
                document_number=patient_data.document_number,
                email=patient_data.email,
                phone=patient_data.phone,
                emergency_contact_name=patient_data.emergency_contact_name,
                emergency_contact_phone=patient_data.emergency_contact_phone,
                date_of_birth=patient_data.date_of_birth,
                gender=patient_data.gender.value,
                blood_type=patient_data.blood_type.value if patient_data.blood_type else None,
                address=patient_data.address,
                city=patient_data.city,
                insurance_provider=patient_data.insurance_provider,
                insurance_number=patient_data.insurance_number,
                allergies=patient_data.allergies,
                medical_conditions=patient_data.medical_conditions,
                medications=patient_data.medications,
                registered_by_id=registered_by_id
            )
            
            created_patient = await self.patient_repository.create(patient)
            
            return PatientResponse(
                id=created_patient.id,
                first_name=created_patient.first_name,
                last_name=created_patient.last_name,
                document_type=created_patient.document_type,
                document_number=created_patient.document_number,
                email=created_patient.email,
                phone=created_patient.phone,
                emergency_contact_name=created_patient.emergency_contact_name,
                emergency_contact_phone=created_patient.emergency_contact_phone,
                date_of_birth=created_patient.date_of_birth,
                gender=created_patient.gender,
                blood_type=created_patient.blood_type,
                address=created_patient.address,
                city=created_patient.city,
                insurance_provider=created_patient.insurance_provider,
                insurance_number=created_patient.insurance_number,
                allergies=created_patient.allergies,
                medical_conditions=created_patient.medical_conditions,
                medications=created_patient.medications,
                age=created_patient.age,
                created_at=created_patient.created_at,
                updated_at=created_patient.updated_at
            )
            
        except IntegrityError as e:
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def get_patient_by_id(self, patient_id: UUID) -> Optional[PatientResponse]:
        """
        Get a patient by their ID.
        
        Args:
            patient_id (UUID): Patient's unique identifier
            
        Returns:
            Optional[PatientResponse]: Patient details if found, None otherwise
        """
        patient = await self.patient_repository.get_by_id(patient_id)
        if not patient:
            return None
        
        return PatientResponse(
            id=patient.id,
            first_name=patient.first_name,
            last_name=patient.last_name,
            document_type=patient.document_type,
            document_number=patient.document_number,
            email=patient.email,
            phone=patient.phone,
            emergency_contact_name=patient.emergency_contact_name,
            emergency_contact_phone=patient.emergency_contact_phone,
            date_of_birth=patient.date_of_birth,
            gender=patient.gender,
            blood_type=patient.blood_type,
            address=patient.address,
            city=patient.city,
            insurance_provider=patient.insurance_provider,
            insurance_number=patient.insurance_number,
            allergies=patient.allergies,
            medical_conditions=patient.medical_conditions,
            medications=patient.medications,
            age=patient.age,
            created_at=patient.created_at,
            updated_at=patient.updated_at
        )
    
    async def get_patient_by_document(self, document_number: str) -> Optional[PatientResponse]:
        """
        Get a patient by their document number.
        
        Args:
            document_number (str): Patient's document number
            
        Returns:
            Optional[PatientResponse]: Patient details if found, None otherwise
        """
        patient = await self.patient_repository.get_by_patient_number(document_number)
        if not patient:
            return None
        
        return await self.get_patient_by_id(patient.id)
    
    async def update_patient(self, patient_id: UUID, patient_data: PatientUpdate) -> Optional[PatientResponse]:
        """
        Update patient information.
        
        Args:
            patient_id (UUID): Patient's unique identifier
            patient_data (PatientUpdate): Updated patient data
            
        Returns:
            Optional[PatientResponse]: Updated patient details if found, None otherwise
            
        Raises:
            PatientNotFoundError: If patient doesn't exist
        """
        patient = await self.patient_repository.get_by_id(patient_id)
        if not patient:
            raise PatientNotFoundError("Patient not found")
        
        # Update patient fields
        update_fields = patient_data.dict(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(patient, field, value)
        
        updated_patient = await self.patient_repository.update(patient)
        return await self.get_patient_by_id(patient_id)
    
    async def list_patients(self, skip: int = 0, limit: int = 100) -> List[PatientResponse]:
        """
        List all patients with pagination.
        
        Args:
            skip (int): Number of patients to skip
            limit (int): Maximum number of patients to return
            
        Returns:
            List[PatientResponse]: List of patients
        """
        patients = await self.patient_repository.list_patients(skip=skip, limit=limit)
        patient_responses = []
        
        for patient in patients:
            patient_response = await self.get_patient_by_id(patient.id)
            if patient_response:
                patient_responses.append(patient_response)
        
        return patient_responses
    
    async def search_patients(self, search_term: str) -> List[PatientResponse]:
        """
        Search patients by name, document number, or other criteria.
        
        Args:
            search_term (str): Search term to match against patient data
            
        Returns:
            List[PatientResponse]: List of matching patients
        """
        patients = await self.patient_repository.search_patients(search_term)
        patient_responses = []
        
        for patient in patients:
            patient_response = await self.get_patient_by_id(patient.id)
            if patient_response:
                patient_responses.append(patient_response)
        
        return patient_responses
    
    async def delete_patient(self, patient_id: UUID) -> bool:
        """
        Delete a patient record.
        
        Args:
            patient_id (UUID): Patient's unique identifier
            
        Returns:
            bool: True if patient was deleted, False if not found
        """
        return await self.patient_repository.delete(patient_id)


class ClinicalService:
    """
    Clinical service for handling clinical records and interventions.
    
    This service manages clinical records, interventions, and medical
    history for dental patients.
    """
    
    def __init__(
        self,
        patient_repository: IPatientRepository,
        clinical_intervention_repository: IClinicalInterventionRepository
    ):
        """
        Initialize the clinical service.
        
        Args:
            patient_repository (IPatientRepository): Patient repository implementation
            clinical_intervention_repository (IClinicalInterventionRepository): Clinical intervention repository
        """
        self.patient_repository = patient_repository
        self.clinical_intervention_repository = clinical_intervention_repository
    
    async def create_intervention(
        self,
        intervention_data: InterventionCreate,
        dentist_id: UUID
    ) -> InterventionResponse:
        """
        Create a new clinical intervention.
        
        Args:
            intervention_data (InterventionCreate): Intervention creation data
            dentist_id (UUID): ID of the dentist performing the intervention
            
        Returns:
            InterventionResponse: Created intervention details
            
        Raises:
            PatientNotFoundError: If patient doesn't exist
            ValidationError: If intervention data is invalid
        """
        # Verify patient exists
        patient = await self.patient_repository.get_by_id(intervention_data.patient_id)
        if not patient:
            raise PatientNotFoundError("Patient not found")
        
        try:
            # Create intervention entity
            intervention = Intervention(
                clinical_record_id=intervention_data.clinical_record_id,
                dentist_id=dentist_id,
                intervention_type=intervention_data.intervention_type.value,
                tooth_number=intervention_data.tooth_number,
                procedure_description=intervention_data.procedure_description,
                materials_used=intervention_data.materials_used,
                duration_minutes=intervention_data.duration_minutes,
                cost=intervention_data.cost,
                notes=intervention_data.notes,
                performed_at=intervention_data.performed_at
            )
            
            created_intervention = await self.clinical_intervention_repository.create(intervention)
            
            return InterventionResponse(
                id=created_intervention.id,
                clinical_record_id=created_intervention.clinical_record_id,
                dentist_id=created_intervention.dentist_id,
                intervention_type=created_intervention.intervention_type,
                tooth_number=created_intervention.tooth_number,
                procedure_description=created_intervention.procedure_description,
                materials_used=created_intervention.materials_used,
                duration_minutes=created_intervention.duration_minutes,
                cost=created_intervention.cost,
                notes=created_intervention.notes,
                performed_at=created_intervention.performed_at,
                created_at=created_intervention.created_at,
                updated_at=created_intervention.updated_at
            )
            
        except IntegrityError as e:
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def get_intervention_by_id(self, intervention_id: UUID) -> Optional[InterventionResponse]:
        """
        Get an intervention by its ID.
        
        Args:
            intervention_id (UUID): Intervention's unique identifier
            
        Returns:
            Optional[InterventionResponse]: Intervention details if found, None otherwise
        """
        intervention = await self.clinical_intervention_repository.get_by_id(intervention_id)
        if not intervention:
            return None
        
        return InterventionResponse(
            id=intervention.id,
            clinical_record_id=intervention.clinical_record_id,
            dentist_id=intervention.dentist_id,
            intervention_type=intervention.intervention_type,
            tooth_number=intervention.tooth_number,
            procedure_description=intervention.procedure_description,
            materials_used=intervention.materials_used,
            duration_minutes=intervention.duration_minutes,
            cost=intervention.cost,
            notes=intervention.notes,
            performed_at=intervention.performed_at,
            created_at=intervention.created_at,
            updated_at=intervention.updated_at
        )
    
    async def get_patient_interventions(self, patient_id: UUID) -> List[InterventionResponse]:
        """
        Get all interventions for a specific patient.
        
        Args:
            patient_id (UUID): Patient's unique identifier
            
        Returns:
            List[InterventionResponse]: List of patient's interventions
        """
        interventions = await self.clinical_intervention_repository.get_by_patient_id(patient_id)
        intervention_responses = []
        
        for intervention in interventions:
            intervention_response = await self.get_intervention_by_id(intervention.id)
            if intervention_response:
                intervention_responses.append(intervention_response)
        
        return intervention_responses
    
    async def get_dentist_interventions(self, dentist_id: UUID) -> List[InterventionResponse]:
        """
        Get all interventions performed by a specific dentist.
        
        Args:
            dentist_id (UUID): Dentist's unique identifier
            
        Returns:
            List[InterventionResponse]: List of dentist's interventions
        """
        interventions = await self.clinical_intervention_repository.get_by_dentist_id(dentist_id)
        intervention_responses = []
        
        for intervention in interventions:
            intervention_response = await self.get_intervention_by_id(intervention.id)
            if intervention_response:
                intervention_responses.append(intervention_response)
        
        return intervention_responses
    
    async def update_intervention(
        self,
        intervention_id: UUID,
        intervention_data: InterventionUpdate
    ) -> Optional[InterventionResponse]:
        """
        Update an existing intervention.
        
        Args:
            intervention_id (UUID): Intervention's unique identifier
            intervention_data (InterventionUpdate): Updated intervention data
            
        Returns:
            Optional[InterventionResponse]: Updated intervention details if found, None otherwise
            
        Raises:
            InterventionNotFoundError: If intervention doesn't exist
        """
        intervention = await self.clinical_intervention_repository.get_by_id(intervention_id)
        if not intervention:
            raise InterventionNotFoundError("Intervention not found")
        
        # Update intervention fields
        update_fields = intervention_data.dict(exclude_unset=True)
        for field, value in update_fields.items():
            if hasattr(intervention, field):
                setattr(intervention, field, value)
        
        updated_intervention = await self.clinical_intervention_repository.update(intervention)
        return await self.get_intervention_by_id(intervention_id)
    
    async def delete_intervention(self, intervention_id: UUID) -> bool:
        """
        Delete an intervention record.
        
        Args:
            intervention_id (UUID): Intervention's unique identifier
            
        Returns:
            bool: True if intervention was deleted, False if not found
        """
        return await self.clinical_intervention_repository.delete(intervention_id)