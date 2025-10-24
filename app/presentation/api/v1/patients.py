"""
Patient management endpoints for the OdontoLab system.

This module provides CRUD operations for patient management.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.schemas.patient_schemas import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse
)
from app.domain.models import User
from app.application.services import PatientService
from app.insfraestructure.repositories import PatientRepository
from app.presentation.api.dependencies import get_current_user, require_admin
from app.application.exceptions import NotFoundError, ValidationError, PermissionError

router = APIRouter()


async def get_patient_service(db: AsyncSession = Depends(get_db)) -> PatientService:
    """Dependency to get patient service."""
    patient_repository = PatientRepository(db)
    return PatientService(patient_repository)


@router.post(
    "/",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new patient"
)
async def create_patient(
    patient_data: PatientCreate,
    patient_service: PatientService = Depends(get_patient_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new patient.
    
    Available for all authenticated users.
    
    Args:
        patient_data: Patient creation data
        
    Returns:
        Created patient information
    """
    try:
        patient = await patient_service.create_patient(patient_data, current_user)
        return PatientResponse.model_validate(patient)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create patient"
        )


@router.get(
    "/",
    response_model=PatientListResponse,
    summary="Get all patients"
)
async def get_patients(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    patient_service: PatientService = Depends(get_patient_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all patients with pagination.
    
    Receptionists can only see patients they created.
    Admins and dentists can see all patients.
    
    Args:
        page: Page number
        per_page: Items per page
        
    Returns:
        Paginated list of patients
    """
    try:
        patients, total = await patient_service.get_all_patients(
            page=page,
            per_page=per_page,
            current_user=current_user
        )
        
        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page
        
        return PatientListResponse(
            success=True,
            data=[PatientResponse.model_validate(patient) for patient in patients],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patients"
        )


@router.get(
    "/search",
    response_model=PatientListResponse,
    summary="Search patients"
)
async def search_patients(
    q: str = Query(..., min_length=2, description="Search term"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    patient_service: PatientService = Depends(get_patient_service),
    current_user: User = Depends(get_current_user)
):
    """
    Search patients by name, email, or phone.
    
    Receptionists can only search patients they created.
    Admins and dentists can search all patients.
    
    Args:
        q: Search term
        page: Page number
        per_page: Items per page
        
    Returns:
        Paginated list of matching patients
    """
    try:
        patients, total = await patient_service.search_patients(
            search_term=q,
            page=page,
            per_page=per_page,
            current_user=current_user
        )
        
        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page
        
        return PatientListResponse(
            success=True,
            data=[PatientResponse.model_validate(patient) for patient in patients],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search patients"
        )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Get patient by ID"
)
async def get_patient(
    patient_id: UUID,
    patient_service: PatientService = Depends(get_patient_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get patient by ID.
    
    Receptionists can only view patients they created.
    Admins and dentists can view any patient.
    
    Args:
        patient_id: Patient ID
        
    Returns:
        Patient information
    """
    try:
        patient = await patient_service.get_patient_by_id(patient_id, current_user)
        return PatientResponse.model_validate(patient)
        
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
            detail="Failed to retrieve patient"
        )


@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Update patient"
)
async def update_patient(
    patient_id: UUID,
    patient_data: PatientUpdate,
    patient_service: PatientService = Depends(get_patient_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update patient information.
    
    Receptionists can only update patients they created.
    Admins and dentists can update any patient.
    
    Args:
        patient_id: Patient ID
        patient_data: Patient update data
        
    Returns:
        Updated patient information
    """
    try:
        patient = await patient_service.update_patient(
            patient_id,
            patient_data,
            current_user
        )
        return PatientResponse.model_validate(patient)
        
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
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update patient"
        )


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete patient"
)
async def delete_patient(
    patient_id: UUID,
    patient_service: PatientService = Depends(get_patient_service),
    current_user: User = Depends(require_admin)
):
    """
    Delete a patient permanently (Admin only).
    
    Note: This will also delete all associated medical records due to CASCADE.
    
    Args:
        patient_id: Patient ID
        
    Returns:
        No content
    """
    try:
        await patient_service.delete_patient(patient_id, current_user)
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
            detail="Failed to delete patient"
        )
