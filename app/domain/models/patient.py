"""
Patient model for the OdontoLab system.

This module defines the Patient entity following the odontolab_database.sql schema.
"""

import uuid
from datetime import date
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Text, Date, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from app.domain.models.enums import Gender


class Patient(Base):
    """
    Patient model for storing patient information.
    
    This model stores comprehensive patient information including personal details,
    contact information, and medical history for the dental clinic.
    
    Attributes:
        id (UUID): Unique identifier for the patient
        patient_number (str): Unique patient identification number (MVP field)
        first_name (str): Patient's first name
        last_name (str): Patient's last name
        email (str): Patient's email address
        phone (str): Patient's phone number
        date_of_birth (date): Patient's birth date
        gender (Gender): Patient's gender (MVP field)
        address (str): Patient's residential address (optional)
        emergency_contact_name (str): Emergency contact person name (optional)
        emergency_contact_phone (str): Emergency contact phone number (optional)
        medical_conditions (str): Pre-existing medical conditions (optional)
        allergies (str): Known allergies (optional)
        created_at (datetime): Registration timestamp
        updated_at (datetime): Last update timestamp
        created_by (UUID): Foreign key to user who created the patient record
        
    Relationships:
        creator: Many-to-one relationship with User (who created the patient)
        medical_records: One-to-many relationship with MedicalRecord
    """
    __tablename__ = "patients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_number = Column(String(20), unique=True, nullable=True, index=True, 
                           comment="Unique patient identification number")
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(SQLAEnum(Gender), nullable=True, comment="Patient gender")
    address = Column(Text, nullable=True)
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    medical_conditions = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="patients_created", foreign_keys=[created_by])
    medical_records = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Patient(name='{self.full_name}', email='{self.email}')>"
    
    @property
    def full_name(self) -> str:
        """Returns the patient's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> int:
        """Calculates and returns the patient's current age."""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
