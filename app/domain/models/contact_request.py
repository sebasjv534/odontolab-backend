"""
Contact Request model for the OdontoLab system.

This module defines the ContactRequest entity for public contact form submissions.
"""

import uuid
import enum
from sqlalchemy import Column, String, DateTime, func, Text, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ContactStatus(str, enum.Enum):
    """
    Enum for contact request status.
    
    Values:
        PENDING: Request is pending review
        CONTACTED: Request has been contacted
        RESOLVED: Request has been resolved
    """
    PENDING = "pending"
    CONTACTED = "contacted"
    RESOLVED = "resolved"


class ContactRequest(Base):
    """
    Contact Request model for public website contact form.
    
    This model stores contact requests submitted through the public website.
    No authentication is required to create these records.
    
    Attributes:
        id (UUID): Unique identifier for the contact request
        nombre (str): Full name of the person submitting the request
        cedula (str): ID document number
        email (str): Email address
        telefono (str): Phone number
        motivo (str): Reason for contact
        servicio (str): Service of interest (optional)
        acepta_politica (bool): Acceptance of privacy policy (must be True)
        status (ContactStatus): Current status of the request
        created_at (datetime): Submission timestamp
    """
    __tablename__ = "contact_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    cedula = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    telefono = Column(String(20), nullable=False)
    motivo = Column(String(255), nullable=False)
    servicio = Column(Text, nullable=True)
    acepta_politica = Column(Boolean, nullable=False, default=False)
    status = Column(Enum(ContactStatus, name="contact_status"), nullable=False, default=ContactStatus.PENDING, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self) -> str:
        return f"<ContactRequest(nombre='{self.nombre}', email='{self.email}', status='{self.status.value}')>"
