"""
Contact Request service for the OdontoLab system.

This module provides business logic for contact request management.
"""

from typing import Optional
from uuid import UUID

from app.domain.models import ContactRequest, User, UserRole, ContactStatus
from app.domain.schemas.contact_schemas import ContactRequestCreate
from app.insfraestructure.repositories import ContactRequestRepository
from app.application.exceptions import NotFoundError, PermissionError


class ContactService:
    """Service for contact request management operations."""
    
    def __init__(self, contact_repository: ContactRequestRepository):
        """Initialize the contact service."""
        self.contact_repository = contact_repository
    
    async def create_contact_request(
        self,
        contact_data: ContactRequestCreate
    ) -> ContactRequest:
        """Create a new contact request (Public endpoint - no auth required)."""
        contact_dict = contact_data.model_dump()
        contact = await self.contact_repository.create(contact_dict)
        return contact
    
    async def get_contact_request_by_id(
        self,
        contact_id: UUID,
        current_user: User
    ) -> ContactRequest:
        """Get contact request by ID (Admin and Receptionist only)."""
        if current_user.role not in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
            raise PermissionError("You don't have permission to view contact requests")
        
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact:
            raise NotFoundError("Contact request not found")
        return contact
    
    async def get_all_contact_requests(
        self,
        page: int = 1,
        per_page: int = 10,
        status: Optional[ContactStatus] = None,
        current_user: User = None
    ) -> tuple[list[ContactRequest], int]:
        """Get all contact requests with pagination and filters."""
        if current_user and current_user.role not in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
            raise PermissionError("You don't have permission to view contact requests")
        
        skip = (page - 1) * per_page
        contacts, total = await self.contact_repository.get_all(
            skip=skip,
            limit=per_page,
            status=status
        )
        return contacts, total
    
    async def get_pending_contact_requests(
        self,
        current_user: User
    ) -> list[ContactRequest]:
        """Get all pending contact requests."""
        if current_user.role not in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
            raise PermissionError("You don't have permission to view contact requests")
        
        contacts = await self.contact_repository.get_pending()
        return contacts
    
    async def update_contact_status(
        self,
        contact_id: UUID,
        status: ContactStatus,
        current_user: User
    ) -> ContactRequest:
        """Update contact request status (Admin and Receptionist only)."""
        if current_user.role not in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
            raise PermissionError("You don't have permission to update contact requests")
        
        # Check if contact exists
        contact = await self.contact_repository.get_by_id(contact_id)
        if not contact:
            raise NotFoundError("Contact request not found")
        
        # Update status
        updated_contact = await self.contact_repository.update_status(contact_id, status)
        return updated_contact
    
    async def delete_contact_request(
        self,
        contact_id: UUID,
        current_user: User
    ) -> bool:
        """Delete a contact request (Admin only)."""
        if current_user.role != UserRole.ADMIN:
            raise PermissionError("Only administrators can delete contact requests")
        
        success = await self.contact_repository.delete(contact_id)
        if not success:
            raise NotFoundError("Contact request not found")
        return success
    
    async def count_contact_requests_by_status(
        self,
        status: ContactStatus
    ) -> int:
        """Count contact requests by status."""
        return await self.contact_repository.count_by_status(status)
