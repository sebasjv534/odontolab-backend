"""
Role model for the odontology system.

This module defines the Role entity and related enums for the dental clinic management system.
Includes role definitions for administrators, dentists, and receptionists.
"""

import uuid
from enum import Enum
from sqlalchemy import Column, String, DateTime, func, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class RoleType(str, Enum):
    """
    Enumeration of available roles in the system.
    
    Roles:
        ADMINISTRATOR: Full system access and user management
        DENTIST: Access to clinical records and interventions
        RECEPTIONIST: Patient management and appointment scheduling
    """
    ADMINISTRATOR = "administrator"
    DENTIST = "dentist"
    RECEPTIONIST = "receptionist"


class Role(Base):
    """
    Role model representing system roles.
    
    This model defines the different roles that users can have in the system,
    each with specific permissions and access levels.
    
    Attributes:
        id (UUID): Unique identifier for the role
        name (str): Role name (must be one of RoleType enum values)
        description (str): Detailed description of the role
        permissions (str): JSON string containing role permissions
        created_at (datetime): Timestamp of role creation
        updated_at (datetime): Timestamp of last update
    """
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    permissions = Column(Text, nullable=True)  # JSON string for permissions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="role")
    
    def __repr__(self) -> str:
        return f"<Role(name='{self.name}')>"