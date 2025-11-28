"""
User model for the odontology system.

This module defines the User entity and related relationships for authentication
and authorization in the dental clinic management system.
"""

import uuid
import enum
from sqlalchemy import Column, String, DateTime, func, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class UserRole(str, enum.Enum):
    """
    Enum for user roles in the system.
    
    Values:
        ADMIN: Administrator with full system access
        DENTIST: Dental professional who creates medical records
        RECEPTIONIST: Front desk staff who manages patients
    """
    ADMIN = "admin"
    DENTIST = "dentist"
    RECEPTIONIST = "receptionist"


class User(Base):
    """
    User model representing system users.
    
    This model handles user authentication, profile information, and role assignment.
    Each user has a role that determines their permissions and access levels.
    
    Attributes:
        id (UUID): Unique identifier for the user
        email (str): User's email address (unique, used as username)
        hashed_password (str): Bcrypt hashed password
        first_name (str): User's first name
        last_name (str): User's last name
        role (UserRole): User's role (admin, dentist, receptionist)
        is_active (bool): Whether the user account is active
        created_at (datetime): Account creation timestamp
        updated_at (datetime): Last profile update timestamp
        
    Relationships:
        patients_created: One-to-many relationship with Patient (created_by)
        medical_records: One-to-many relationship with MedicalRecord (dentist_id)
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole, name="user_role"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    patients_created = relationship("Patient", back_populates="creator", foreign_keys="Patient.created_by")
    medical_records = relationship("MedicalRecord", back_populates="dentist", foreign_keys="MedicalRecord.dentist_id")
    appointments_as_dentist = relationship("Appointment", back_populates="dentist", 
                                          foreign_keys="Appointment.dentist_id")
    appointments_created = relationship("Appointment", back_populates="creator", 
                                       foreign_keys="Appointment.created_by")
    
    def __repr__(self) -> str:
        return f"<User(email='{self.email}', role='{self.role.value}')>"
    
    @property
    def full_name(self) -> str:
        """Returns the user's full name."""
        return f"{self.first_name} {self.last_name}"

    