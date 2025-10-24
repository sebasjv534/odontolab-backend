"""
Dashboard endpoints for the OdontoLab system.

This module provides dashboard statistics based on user role.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

from app.core.database import get_db
from app.domain.schemas.dashboard_schemas import (
    AdminDashboardStats,
    DentistDashboardStats,
    ReceptionistDashboardStats
)
from app.domain.models import User, UserRole
from app.application.services import DashboardService
from app.insfraestructure.repositories import (
    UserRepository,
    PatientRepository,
    MedicalRecordRepository,
    ContactRequestRepository
)
from app.presentation.api.dependencies import get_current_user

router = APIRouter()


async def get_dashboard_service(
    db: AsyncSession = Depends(get_db)
) -> DashboardService:
    """Dependency to get dashboard service."""
    user_repository = UserRepository(db)
    patient_repository = PatientRepository(db)
    medical_record_repository = MedicalRecordRepository(db)
    contact_repository = ContactRequestRepository(db)
    return DashboardService(
        user_repository,
        patient_repository,
        medical_record_repository,
        contact_repository
    )


@router.get(
    "/stats",
    response_model=Union[AdminDashboardStats, DentistDashboardStats, ReceptionistDashboardStats],
    summary="Get dashboard statistics"
)
async def get_dashboard_stats(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard statistics based on user role.
    
    Returns different statistics depending on the user's role:
    - Admins: Complete system statistics
    - Dentists: Personal statistics (patients treated, records created, appointments)
    - Receptionists: Patient management and contact statistics
    
    Returns:
        Dashboard statistics appropriate for the user's role
    """
    try:
        stats = await dashboard_service.get_dashboard_stats_by_role(current_user)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard statistics"
        )


@router.get(
    "/admin",
    response_model=AdminDashboardStats,
    summary="Get admin dashboard statistics"
)
async def get_admin_dashboard_stats(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get admin dashboard statistics (Admin only).
    
    Returns comprehensive system statistics including:
    - Total users, dentists, receptionists
    - Total and recent patients
    - Total and recent medical records
    - Contact requests (pending and total)
    - Upcoming appointments
    
    Returns:
        Complete admin dashboard statistics
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required"
        )
    
    try:
        stats = await dashboard_service.get_admin_dashboard_stats()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve admin dashboard statistics"
        )


@router.get(
    "/dentist",
    response_model=DentistDashboardStats,
    summary="Get dentist dashboard statistics"
)
async def get_dentist_dashboard_stats(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get dentist dashboard statistics (Dentist only).
    
    Returns personal statistics including:
    - Total unique patients treated
    - Total medical records created
    - Recent medical records (last 30 days)
    - Upcoming appointments
    - Today's appointments
    
    Returns:
        Dentist-specific dashboard statistics
    """
    if current_user.role != UserRole.DENTIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dentist privileges required"
        )
    
    try:
        stats = await dashboard_service.get_dentist_dashboard_stats(current_user.id)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dentist dashboard statistics"
        )


@router.get(
    "/receptionist",
    response_model=ReceptionistDashboardStats,
    summary="Get receptionist dashboard statistics"
)
async def get_receptionist_dashboard_stats(
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get receptionist dashboard statistics (Receptionist only).
    
    Returns statistics including:
    - Total patients registered by this receptionist
    - Recent patients (last 30 days)
    - Pending contact requests
    - Total contact requests
    - Upcoming appointments
    - Today's appointments
    
    Returns:
        Receptionist-specific dashboard statistics
    """
    if current_user.role != UserRole.RECEPTIONIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Receptionist privileges required"
        )
    
    try:
        stats = await dashboard_service.get_receptionist_dashboard_stats(current_user.id)
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve receptionist dashboard statistics"
        )
