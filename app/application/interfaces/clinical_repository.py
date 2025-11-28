"""
Clinical repository interfaces for the odontology system.

This module defines abstract interfaces for patient and clinical intervention
data access operations, following the repository pattern.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

# TODO: These models will be implemented in future phases (MVP Phase 2-4)
# from app.domain.models.clinical_models import Patient, ClinicalIntervention
from app.domain.models import Patient


class IPatientRepository(ABC):
    """
    Abstract interface for patient data access operations.
    """

    @abstractmethod
    async def get_by_id(self, patient_id: UUID) -> Optional[Patient]:
        """
        Retrieve a patient by ID.
        
        Args:
            patient_id (UUID): The patient ID to search for
            
        Returns:
            Optional[Patient]: The patient if found, None otherwise
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_patient_number(self, patient_number: str) -> Optional[Patient]:
        """
        Retrieve a patient by patient number.
        
        Args:
            patient_number (str): The patient number to search for
            
        Returns:
            Optional[Patient]: The patient if found, None otherwise
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, patient: Patient) -> Patient:
        """
        Create a new patient.
        
        Args:
            patient (Patient): The patient entity to create
            
        Returns:
            Patient: The created patient with assigned ID
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, patient: Patient) -> Patient:
        """
        Update an existing patient.
        
        Args:
            patient (Patient): The patient entity to update
            
        Returns:
            Patient: The updated patient
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, patient_id: UUID) -> bool:
        """
        Delete a patient by ID.
        
        Args:
            patient_id (UUID): The ID of the patient to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        raise NotImplementedError

    @abstractmethod
    async def list_patients(self, skip: int = 0, limit: int = 100) -> List[Patient]:
        """
        List patients with pagination.
        
        Args:
            skip (int): Number of patients to skip
            limit (int): Maximum number of patients to return
            
        Returns:
            List[Patient]: List of patients
        """
        raise NotImplementedError

    @abstractmethod
    async def search_patients(self, query: str) -> List[Patient]:
        """
        Search patients by name, email, or patient number.
        
        Args:
            query (str): Search query
            
        Returns:
            List[Patient]: List of matching patients
        """
        raise NotImplementedError

    @abstractmethod
    async def generate_patient_number(self) -> str:
        """
        Generate a unique patient number.
        
        Returns:
            str: Unique patient number
        """
        raise NotImplementedError


class IClinicalInterventionRepository(ABC):
    """
    Abstract interface for clinical intervention data access operations.
    """

    @abstractmethod
    async def get_by_id(self, intervention_id: UUID) -> Optional[ClinicalIntervention]:
        """
        Retrieve a clinical intervention by ID.
        
        Args:
            intervention_id (UUID): The intervention ID to search for
            
        Returns:
            Optional[ClinicalIntervention]: The intervention if found, None otherwise
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, intervention: ClinicalIntervention) -> ClinicalIntervention:
        """
        Create a new clinical intervention.
        
        Args:
            intervention (ClinicalIntervention): The intervention entity to create
            
        Returns:
            ClinicalIntervention: The created intervention with assigned ID
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, intervention: ClinicalIntervention) -> ClinicalIntervention:
        """
        Update an existing clinical intervention.
        
        Args:
            intervention (ClinicalIntervention): The intervention entity to update
            
        Returns:
            ClinicalIntervention: The updated intervention
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, intervention_id: UUID) -> bool:
        """
        Delete a clinical intervention by ID.
        
        Args:
            intervention_id (UUID): The ID of the intervention to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_patient_id(self, patient_id: UUID) -> List[ClinicalIntervention]:
        """
        Get all interventions for a specific patient.
        
        Args:
            patient_id (UUID): The patient ID
            
        Returns:
            List[ClinicalIntervention]: List of interventions for the patient
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_dentist_id(self, dentist_id: UUID) -> List[ClinicalIntervention]:
        """
        Get all interventions performed by a specific dentist.
        
        Args:
            dentist_id (UUID): The dentist profile ID
            
        Returns:
            List[ClinicalIntervention]: List of interventions by the dentist
        """
        raise NotImplementedError

    @abstractmethod
    async def list_interventions(self, skip: int = 0, limit: int = 100) -> List[ClinicalIntervention]:
        """
        List interventions with pagination.
        
        Args:
            skip (int): Number of interventions to skip
            limit (int): Maximum number of interventions to return
            
        Returns:
            List[ClinicalIntervention]: List of interventions
        """
        raise NotImplementedError