"""
Medical Record model for the OdontoLab system.

This module defines the MedicalRecord entity following the odontolab_database.sql schema.
"""

import uuid
from sqlalchemy import Column, String, DateTime, func, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.core.database import Base


class MedicalRecord(Base):
    """
    Medical Record model for storing clinical histories.
    
    This model stores comprehensive dental clinical records including diagnosis,
    treatment performed, and dental chart information.
    
    Attributes:
        id (UUID): Unique identifier for the medical record
        patient_id (UUID): Foreign key reference to the Patient
        dentist_id (UUID): Foreign key reference to the User (dentist)
        visit_date (datetime): Date and time of the visit
        diagnosis (str): Clinical diagnosis
        treatment (str): Treatment performed
        notes (str): Additional clinical notes (optional)
        teeth_chart (dict): Digital odontogram in JSON format (optional)
        next_appointment (datetime): Scheduled next appointment (optional)
        created_at (datetime): Record creation timestamp
        updated_at (datetime): Last update timestamp
        
    Relationships:
        patient: Many-to-one relationship with Patient model
        dentist: Many-to-one relationship with User model (role=dentist)
    """
    __tablename__ = "medical_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    dentist_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    visit_date = Column(DateTime(timezone=True), nullable=False, index=True)
    diagnosis = Column(Text, nullable=False)
    treatment = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    teeth_chart = Column(JSONB, nullable=True)
    next_appointment = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    dentist = relationship("User", back_populates="medical_records", foreign_keys=[dentist_id])
    
    def __repr__(self) -> str:
        return f"<MedicalRecord(id='{self.id}', patient_id='{self.patient_id}')>"
