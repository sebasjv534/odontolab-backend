"""
Patient and clinical models for the odontology system.

This module defines models for patient management and clinical interventions,
supporting the core functionality of the dental clinic management system.
"""

import uuid
from enum import Enum
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Text, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class Gender(str, Enum):
    """Gender enumeration for patient records."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class InterventionType(str, Enum):
    """Types of dental interventions."""
    CONSULTATION = "consultation"
    CLEANING = "cleaning"
    FILLING = "filling"
    EXTRACTION = "extraction"
    ROOT_CANAL = "root_canal"
    CROWN = "crown"
    BRIDGE = "bridge"
    IMPLANT = "implant"
    ORTHODONTICS = "orthodontics"
    SURGERY = "surgery"
    EMERGENCY = "emergency"
    OTHER = "other"


class Patient(Base):
    """
    Patient model for dental clinic management.
    
    This model stores patient information and serves as the central entity
    for all clinical records and appointments.
    
    Attributes:
        id (UUID): Unique identifier for the patient
        patient_number (str): Unique patient identification number
        first_name (str): Patient's first name
        last_name (str): Patient's last name
        date_of_birth (date): Patient's birth date
        gender (Gender): Patient's gender
        phone (str): Primary contact phone number
        email (str): Patient's email address
        address (str): Patient's residential address
        emergency_contact_name (str): Emergency contact person name
        emergency_contact_phone (str): Emergency contact phone number
        medical_history (str): Relevant medical history
        allergies (str): Known allergies and reactions
        insurance_info (str): Insurance information
        registered_by_id (UUID): Foreign key to receptionist who registered the patient
        created_at (datetime): Registration timestamp
        updated_at (datetime): Last update timestamp
        
    Relationships:
        registered_by: Many-to-one relationship with ReceptionistProfile
        clinical_interventions: One-to-many relationship with ClinicalIntervention
    """
    __tablename__ = "patients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_number = Column(String(20), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    medical_history = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    insurance_info = Column(Text, nullable=True)
    registered_by_id = Column(UUID(as_uuid=True), ForeignKey("receptionist_profiles.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    registered_by = relationship("ReceptionistProfile", back_populates="registered_patients")
    clinical_interventions = relationship("ClinicalIntervention", back_populates="patient")
    
    def __repr__(self) -> str:
        return f"<Patient(patient_number='{self.patient_number}', name='{self.full_name}')>"
    
    @property
    def full_name(self) -> str:
        """Returns the patient's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self) -> int:
        """Calculates and returns the patient's current age."""
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class ClinicalIntervention(Base):
    """
    Clinical intervention model for recording dental procedures.
    
    This model stores information about dental procedures performed on patients,
    including diagnosis, treatment, and follow-up notes.
    
    Attributes:
        id (UUID): Unique identifier for the intervention
        patient_id (UUID): Foreign key reference to the Patient
        dentist_id (UUID): Foreign key reference to the DentistProfile
        intervention_type (InterventionType): Type of dental intervention
        diagnosis (str): Clinical diagnosis
        treatment_description (str): Detailed treatment description
        notes (str): Additional clinical notes
        cost (Decimal): Cost of the intervention
        intervention_date (datetime): Date and time of the intervention
        follow_up_date (datetime): Scheduled follow-up date (if applicable)
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Last update timestamp
        
    Relationships:
        patient: Many-to-one relationship with Patient model
        dentist: Many-to-one relationship with DentistProfile model
    """
    __tablename__ = "clinical_interventions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    dentist_id = Column(UUID(as_uuid=True), ForeignKey("dentist_profiles.id"), nullable=False)
    intervention_type = Column(String(50), nullable=False)
    diagnosis = Column(Text, nullable=False)
    treatment_description = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    cost = Column(Numeric(10, 2), nullable=True, comment="Cost of the intervention")
    intervention_date = Column(DateTime(timezone=True), nullable=False)
    follow_up_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="clinical_interventions")
    dentist = relationship("DentistProfile", back_populates="clinical_interventions")
    
    def __repr__(self) -> str:
        return f"<ClinicalIntervention(id='{self.id}', type='{self.intervention_type}')>"