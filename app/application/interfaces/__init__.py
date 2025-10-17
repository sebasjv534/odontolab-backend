"""
Interfaces package for the odontology system.

This package contains abstract interfaces for repository patterns and service contracts,
enabling clean architecture and dependency inversion principles.
"""

from .user_repository import IUserRepository, IRoleRepository
from .clinical_repository import IPatientRepository, IClinicalInterventionRepository

__all__ = [
    "IUserRepository",
    "IRoleRepository", 
    "IPatientRepository",
    "IClinicalInterventionRepository"
]