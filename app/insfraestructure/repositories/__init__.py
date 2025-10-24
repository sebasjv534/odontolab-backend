"""
Repositories package for the OdontoLab system.

This package contains all repository implementations for data access layer.
"""

from .user_repository import UserRepository
from .patient_repository import PatientRepository
from .medical_record_repository import MedicalRecordRepository
from .contact_repository import ContactRequestRepository

__all__ = [
    "UserRepository",
    "PatientRepository",
    "MedicalRecordRepository",
    "ContactRequestRepository",
]