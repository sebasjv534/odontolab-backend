"""
User model for the odontology system.

This module defines the User entity and related relationships for authentication
and authorization in the dental clinic management system.
"""

import uuid
from sqlalchemy import Column, String, DateTime, func, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class User(Base):
    """
    User model representing system users.
    
    This model handles user authentication, profile information, and role assignment.
    Each user has a role that determines their permissions and access levels.
    
    Attributes:
        id (UUID): Unique identifier for the user
        username (str): Unique username for login
        email (str): User's email address (unique)
        password_hash (str): Bcrypt hashed password
        first_name (str): User's first name
        last_name (str): User's last name
        phone (str): Contact phone number
        is_active (bool): Whether the user account is active
        role_id (UUID): Foreign key reference to the user's role
        created_at (datetime): Account creation timestamp
        updated_at (datetime): Last profile update timestamp
        
    Relationships:
        role: Many-to-one relationship with Role model
        dentist_profile: One-to-one relationship with DentistProfile (if user is dentist)
        receptionist_profile: One-to-one relationship with ReceptionistProfile (if user is receptionist)
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    role = relationship("Role", back_populates="users")
    dentist_profile = relationship("DentistProfile", back_populates="user", uselist=False)
    receptionist_profile = relationship("ReceptionistProfile", back_populates="user", uselist=False)
    
    def __repr__(self) -> str:
        return f"<User(username='{self.username}', email='{self.email}')>"
    
    @property
    def full_name(self) -> str:
        """Returns the user's full name."""
        return f"{self.first_name} {self.last_name}"

    