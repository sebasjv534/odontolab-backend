"""
Contact request endpoints for the OdontoLab system.

This module provides endpoints for managing contact requests from the public form.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.schemas.contact_schemas import (
    ContactRequestCreate,
    ContactRequestResponse,
    ContactRequestListResponse
)
from app.domain.models import User, ContactStatus
from app.application.services import ContactService
from app.insfraestructure.repositories import ContactRequestRepository
from app.presentation.api.dependencies import get_current_user, require_admin_or_receptionist
from app.application.exceptions import NotFoundError, PermissionError

router = APIRouter()


async def get_contact_service(db: AsyncSession = Depends(get_db)) -> ContactService:
    """Dependency to get contact service."""
    contact_repository = ContactRequestRepository(db)
    return ContactService(contact_repository)


@router.post(
    "/",
    response_model=ContactRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new contact request"
)
async def create_contact_request(
    contact_data: ContactRequestCreate,
    contact_service: ContactService = Depends(get_contact_service)
):
    """
    Create a new contact request (Public endpoint - no authentication required).
    
    This endpoint is used by the public contact form on the website.
    
    Args:
        contact_data: Contact request data
        
    Returns:
        Created contact request information
    """
    try:
        contact = await contact_service.create_contact_request(contact_data)
        return ContactRequestResponse.model_validate(contact)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create contact request"
        )


@router.get(
    "/",
    response_model=ContactRequestListResponse,
    summary="Get all contact requests"
)
async def get_contact_requests(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[ContactStatus] = Query(None, description="Filter by status"),
    contact_service: ContactService = Depends(get_contact_service),
    current_user: User = Depends(require_admin_or_receptionist)
):
    """
    Get all contact requests with pagination (Admin and Receptionist only).
    
    Args:
        page: Page number
        per_page: Items per page
        status: Optional status filter (pending, contacted, resolved)
        
    Returns:
        Paginated list of contact requests
    """
    try:
        contacts, total = await contact_service.get_all_contact_requests(
            page=page,
            per_page=per_page,
            status=status,
            current_user=current_user
        )
        
        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page
        
        return ContactRequestListResponse(
            success=True,
            data=[ContactRequestResponse.model_validate(contact) for contact in contacts],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contact requests"
        )


@router.get(
    "/pending",
    response_model=list[ContactRequestResponse],
    summary="Get pending contact requests"
)
async def get_pending_contact_requests(
    contact_service: ContactService = Depends(get_contact_service),
    current_user: User = Depends(require_admin_or_receptionist)
):
    """
    Get all pending contact requests (Admin and Receptionist only).
    
    Returns:
        List of pending contact requests
    """
    try:
        contacts = await contact_service.get_pending_contact_requests(current_user)
        return [ContactRequestResponse.model_validate(contact) for contact in contacts]
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pending contact requests"
        )


@router.get(
    "/{contact_id}",
    response_model=ContactRequestResponse,
    summary="Get contact request by ID"
)
async def get_contact_request(
    contact_id: UUID,
    contact_service: ContactService = Depends(get_contact_service),
    current_user: User = Depends(require_admin_or_receptionist)
):
    """
    Get contact request by ID (Admin and Receptionist only).
    
    Args:
        contact_id: Contact request ID
        
    Returns:
        Contact request information
    """
    try:
        contact = await contact_service.get_contact_request_by_id(
            contact_id,
            current_user
        )
        return ContactRequestResponse.model_validate(contact)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve contact request"
        )


@router.patch(
    "/{contact_id}/status",
    response_model=ContactRequestResponse,
    summary="Update contact request status"
)
async def update_contact_status(
    contact_id: UUID,
    new_status: ContactStatus = Query(..., description="New status"),
    contact_service: ContactService = Depends(get_contact_service),
    current_user: User = Depends(require_admin_or_receptionist)
):
    """
    Update contact request status (Admin and Receptionist only).
    
    Args:
        contact_id: Contact request ID
        new_status: New status (pending, contacted, resolved)
        
    Returns:
        Updated contact request information
    """
    try:
        contact = await contact_service.update_contact_status(
            contact_id,
            new_status,
            current_user
        )
        return ContactRequestResponse.model_validate(contact)
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update contact request"
        )


@router.delete(
    "/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete contact request"
)
async def delete_contact_request(
    contact_id: UUID,
    contact_service: ContactService = Depends(get_contact_service),
    current_user: User = Depends(require_admin_or_receptionist)
):
    """
    Delete a contact request (Admin only).
    
    Args:
        contact_id: Contact request ID
        
    Returns:
        No content
    """
    try:
        await contact_service.delete_contact_request(contact_id, current_user)
        return None
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete contact request"
        )
