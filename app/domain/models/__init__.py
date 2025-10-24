"""
Domain models for the OdontoLab system.

This module exports all domain models for the application following the
odontolab_database.sql schema.
"""

from .user_model import User, UserRole
from .patient import Patient
from .medical_record import MedicalRecord
from .contact_request import ContactRequest, ContactStatus

__all__ = [
    "User",
    "UserRole",
    "Patient",
    "MedicalRecord",
    "ContactRequest",
    "ContactStatus",
]