"""
Contact Request repository for database operations.

This module implements the data access layer for ContactRequest entity operations following
the API_SUMMARY specifications. This is for the PUBLIC contact form.
"""

from typing import Optional, List
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.domain.models import ContactRequest, ContactStatus


class ContactRequestRepository:
    """Repository class for ContactRequest CRUD operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize ContactRequestRepository with database session.
        
        Args:
            db (AsyncSession): Database session
        """
        self.db = db
    
    async def create(self, contact_data: dict) -> ContactRequest:
        """
        Create a new contact request (PUBLIC endpoint).
        
        Args:
            contact_data (dict): Contact request data
            
        Returns:
            ContactRequest: Created contact request instance
        """
        # Map frontend field names to database field names
        if 'aceptaPolitica' in contact_data:
            contact_data['acepta_politica'] = contact_data.pop('aceptaPolitica')
        
        # Set default status
        contact_data['status'] = ContactStatus.PENDING
        
        contact = ContactRequest(**contact_data)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact
    
    async def get_by_id(self, contact_id: UUID) -> Optional[ContactRequest]:
        """
        Get contact request by ID.
        
        Args:
            contact_id (UUID): Contact request's unique identifier
            
        Returns:
            Optional[ContactRequest]: Contact request instance if found, None otherwise
        """
        result = await self.db.execute(
            select(ContactRequest).where(ContactRequest.id == contact_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        status: Optional[ContactStatus] = None
    ) -> tuple[List[ContactRequest], int]:
        """
        Get all contact requests with pagination and optional status filter.
        
        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            status (Optional[ContactStatus]): Filter by status
            
        Returns:
            tuple[List[ContactRequest], int]: List of contact requests and total count
        """
        # Build query
        query = select(ContactRequest)
        count_query = select(func.count(ContactRequest.id))
        
        if status is not None:
            query = query.where(ContactRequest.status == status)
            count_query = count_query.where(ContactRequest.status == status)
        
        # Get total count
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get contact requests
        query = query.offset(skip).limit(limit).order_by(ContactRequest.created_at.desc())
        result = await self.db.execute(query)
        contacts = result.scalars().all()
        
        return contacts, total
    
    async def update_status(
        self,
        contact_id: UUID,
        status: ContactStatus
    ) -> Optional[ContactRequest]:
        """
        Update contact request status.
        
        Args:
            contact_id (UUID): Contact request's unique identifier
            status (ContactStatus): New status
            
        Returns:
            Optional[ContactRequest]: Updated contact request if found, None otherwise
        """
        await self.db.execute(
            update(ContactRequest)
            .where(ContactRequest.id == contact_id)
            .values(status=status)
        )
        await self.db.commit()
        
        return await self.get_by_id(contact_id)
    
    async def delete(self, contact_id: UUID) -> bool:
        """
        Delete a contact request (hard delete).
        
        Args:
            contact_id (UUID): Contact request's unique identifier
            
        Returns:
            bool: True if contact request was deleted, False otherwise
        """
        result = await self.db.execute(
            delete(ContactRequest).where(ContactRequest.id == contact_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def count_by_status(self, status: ContactStatus) -> int:
        """
        Count contact requests by status.
        
        Args:
            status (ContactStatus): Status to count
            
        Returns:
            int: Number of contact requests with the specified status
        """
        result = await self.db.execute(
            select(func.count(ContactRequest.id))
            .where(ContactRequest.status == status)
        )
        return result.scalar()
    
    async def count_all(self) -> int:
        """
        Count all contact requests.
        
        Returns:
            int: Total number of contact requests
        """
        result = await self.db.execute(select(func.count(ContactRequest.id)))
        return result.scalar()
    
    async def get_pending(self, limit: int = 10) -> List[ContactRequest]:
        """
        Get pending contact requests.
        
        Args:
            limit (int): Maximum number of records to return
            
        Returns:
            List[ContactRequest]: List of pending contact requests
        """
        query = (
            select(ContactRequest)
            .where(ContactRequest.status == ContactStatus.PENDING)
            .order_by(ContactRequest.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
