"""
Medical records management endpoints for the OdontoLab system.

This module provides CRUD operations for medical records management.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.schemas.medical_record_schemas import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalRecordResponse,
    MedicalRecordListResponse
)
from app.domain.models import User
from app.application.services import MedicalRecordService
from app.insfraestructure.repositories import MedicalRecordRepository, PatientRepository
from app.presentation.api.dependencies import get_current_user, require_admin
from app.application.exceptions import NotFoundError, ValidationError, PermissionError

router = APIRouter()


async def get_medical_record_service(
    db: AsyncSession = Depends(get_db)
) -> MedicalRecordService:
    """Dependency to get medical record service."""
    medical_record_repository = MedicalRecordRepository(db)
    patient_repository = PatientRepository(db)
    return MedicalRecordService(medical_record_repository, patient_repository)


@router.post(
    "/",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new medical record"
)
async def create_medical_record(
    record_data: MedicalRecordCreate,
    medical_record_service: MedicalRecordService = Depends(get_medical_record_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new medical record (Dentist only).
    
    Args:
        record_data: Medical record creation data
        
    Returns:
        Created medical record information
    """
    try:
        record = await medical_record_service.create_medical_record(
            record_data,
            current_user
        )
        return MedicalRecordResponse.model_validate(record)
        
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
            detail="Failed to create medical record"
        )


@router.get(
    "/",
    response_model=MedicalRecordListResponse,
    summary="Get all medical records"
)
async def get_medical_records(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    medical_record_service: MedicalRecordService = Depends(get_medical_record_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all medical records with pagination.
    
    Dentists can only see their own records.
    Admins and receptionists can see all records.
    
    Args:
        page: Page number
        per_page: Items per page
        
    Returns:
        Paginated list of medical records
    """
    try:
        records, total = await medical_record_service.get_all_medical_records(
            page=page,
            per_page=per_page,
            current_user=current_user
        )
        
        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page
        
        return MedicalRecordListResponse(
            success=True,
            data=[MedicalRecordResponse.model_validate(record) for record in records],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medical records"
        )


@router.get(
    "/patient/{patient_id}",
    response_model=list[MedicalRecordResponse],
    summary="Get medical records by patient"
)
async def get_records_by_patient(
    patient_id: UUID,
    medical_record_service: MedicalRecordService = Depends(get_medical_record_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all medical records for a specific patient.
    
    Receptionists can only view records for patients they created.
    Admins and dentists can view all records.
    
    Args:
        patient_id: Patient ID
        
    Returns:
        List of medical records for the patient
    """
    try:
        records = await medical_record_service.get_records_by_patient(
            patient_id,
            current_user
        )
        return [MedicalRecordResponse.model_validate(record) for record in records]
        
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
            detail="Failed to retrieve medical records"
        )


@router.get(
    "/upcoming",
    response_model=list[MedicalRecordResponse],
    summary="Get upcoming appointments"
)
async def get_upcoming_appointments(
    medical_record_service: MedicalRecordService = Depends(get_medical_record_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get upcoming appointments.
    
    Returns all upcoming appointments for all users.
    
    Returns:
        List of medical records with upcoming appointments
    """
    try:
        records = await medical_record_service.get_upcoming_appointments()
        return [MedicalRecordResponse.model_validate(record) for record in records]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve upcoming appointments"
        )


@router.get(
    "/{record_id}",
    response_model=MedicalRecordResponse,
    summary="Get medical record by ID"
)
async def get_medical_record(
    record_id: UUID,
    medical_record_service: MedicalRecordService = Depends(get_medical_record_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get medical record by ID.
    
    Dentists can only view their own records unless they are admin.
    
    Args:
        record_id: Medical record ID
        
    Returns:
        Medical record information
    """
    try:
        record = await medical_record_service.get_medical_record_by_id(
            record_id,
            current_user
        )
        return MedicalRecordResponse.model_validate(record)
        
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
            detail="Failed to retrieve medical record"
        )


@router.put(
    "/{record_id}",
    response_model=MedicalRecordResponse,
    summary="Update medical record"
)
async def update_medical_record(
    record_id: UUID,
    record_data: MedicalRecordUpdate,
    medical_record_service: MedicalRecordService = Depends(get_medical_record_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update medical record.
    
    Only the dentist who created it or admin can update.
    Receptionists cannot update medical records.
    
    Args:
        record_id: Medical record ID
        record_data: Medical record update data
        
    Returns:
        Updated medical record information
    """
    try:
        record = await medical_record_service.update_medical_record(
            record_id,
            record_data,
            current_user
        )
        return MedicalRecordResponse.model_validate(record)
        
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
            detail="Failed to update medical record"
        )


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete medical record"
)
async def delete_medical_record(
    record_id: UUID,
    medical_record_service: MedicalRecordService = Depends(get_medical_record_service),
    current_user: User = Depends(require_admin)
):
    """
    Delete a medical record permanently (Admin only).
    
    Args:
        record_id: Medical record ID
        
    Returns:
        No content
    """
    try:
        await medical_record_service.delete_medical_record(record_id, current_user)
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
            detail="Failed to delete medical record"
        )
