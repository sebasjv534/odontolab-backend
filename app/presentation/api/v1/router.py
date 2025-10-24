"""
Main API router for version 1.

This module defines the main router that includes all API endpoints
for the OdontoLab system.
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .patients import router as patients_router
from .medical_records import router as medical_records_router
from .dashboard import router as dashboard_router
from .contact import router as contact_router

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Include user management routes (Admin only)
api_router.include_router(users_router, prefix="/users", tags=["Users"])

# Include patient management routes
api_router.include_router(patients_router, prefix="/patients", tags=["Patients"])

# Include medical records routes
api_router.include_router(medical_records_router, prefix="/medical-records", tags=["Medical Records"])

# Include dashboard routes
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])

# Include contact request routes (Public + Admin/Receptionist)
api_router.include_router(contact_router, prefix="/contact", tags=["Contact"])


@api_router.get("/status", tags=["API"])
async def api_status():
    """API status endpoint."""
    return {
        "status": "operational",
        "version": "1.0.0",
        "service": "OdontoLab Backend API",
        "endpoints": {
            "auth": "Authentication endpoints (login, logout, me)",
            "users": "User management (Admin only)",
            "patients": "Patient management",
            "medical_records": "Medical records and appointments",
            "dashboard": "Dashboard statistics by role",
            "contact": "Contact requests from public form"
        }
    }