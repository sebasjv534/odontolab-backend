"""
Profile models for different user roles in the dental clinic management system.

This module defines profile models for administrators, dentists, and receptionists,
each with specific fields relevant to their role in the dental clinic.
"""

import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Text, Integer, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class AdministratorProfile(Base):
    """
    Administrator profile model.
    
    Contains specific information for system administrators
    who manage users and system configurations.
    
    Attributes:
        id (UUID): Unique identifier for the profile
        user_id (UUID): Foreign key to the associated user
        department (str): Department or area of responsibility
        permissions_level (str): Level of administrative permissions
        created_at (datetime): Timestamp of profile creation
        updated_at (datetime): Timestamp of last update
    """
    __tablename__ = "administrator_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    department = Column(String(100), nullable=True)
    permissions_level = Column(String(50), default="full")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="administrator_profile")
    
    def __repr__(self) -> str:
        return f"<AdministratorProfile(user_id='{self.user_id}', department='{self.department}')>"


class DentistProfile(Base):
    """
    Dentist profile model with professional information.
    
    This model stores specific information for users with the dentist role,
    including professional credentials and specializations.
    
    Attributes:
        id (UUID): Unique identifier for the profile
        user_id (UUID): Foreign key reference to the User
        license_number (str): Professional license number
        specialization (str): Dental specialization area
        years_experience (int): Years of professional experience
        education (str): Educational background
        certifications (str): Professional certifications
        created_at (datetime): Profile creation timestamp
        updated_at (datetime): Last profile update timestamp
        
    Relationships:
        user: One-to-one relationship with User model
        clinical_interventions: One-to-many relationship with ClinicalIntervention
    """
    __tablename__ = "dentist_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    license_number = Column(String(50), unique=True, nullable=False)
    specialization = Column(String(100), nullable=True)
    years_experience = Column(Integer, nullable=True)
    education = Column(Text, nullable=True)
    certifications = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="dentist_profile")
    clinical_interventions = relationship("ClinicalIntervention", back_populates="dentist")
    interventions = relationship("Intervention", back_populates="dentist")
    
    def __repr__(self) -> str:
        return f"<DentistProfile(license_number='{self.license_number}')>"


class ReceptionistProfile(Base):
    """
    Receptionist profile model with administrative information.
    
    This model stores specific information for users with the receptionist role,
    including administrative skills and department assignments.
    
    Attributes:
        id (UUID): Unique identifier for the profile
        user_id (UUID): Foreign key reference to the User
        employee_id (str): Internal employee identification
        department (str): Assigned department or area
        shift_schedule (str): Work shift information
        emergency_contact (str): Emergency contact information
        hire_date (datetime): Date of employment
        created_at (datetime): Profile creation timestamp
        updated_at (datetime): Last profile update timestamp
        
    Relationships:
        user: One-to-one relationship with User model
        registered_patients: One-to-many relationship with Patient (patients registered by this receptionist)
    """
    __tablename__ = "receptionist_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    employee_id = Column(String(20), unique=True, nullable=False)
    department = Column(String(100), nullable=True)
    shift_schedule = Column(String(100), nullable=True)
    emergency_contact = Column(String(200), nullable=True)
    hire_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="receptionist_profile")
    registered_patients = relationship("Patient", back_populates="registered_by")
    
    def __repr__(self) -> str:
        return f"<ReceptionistProfile(employee_id='{self.employee_id}')>"