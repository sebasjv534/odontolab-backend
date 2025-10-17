"""
Main API router for version 1.

This module defines the main router that includes all API endpoints
for the odontology system.
"""

from fastapi import APIRouter
from .auth import router as auth_router
# from .admin import router as admin_router  
# from .patients import router as patients_router
# from .clinical import router as clinical_router

api_router = APIRouter()

# Include authentication routes
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Include admin routes  
# api_router.include_router(admin_router, prefix="/admin", tags=["Administration"])

# Include patient management routes
# api_router.include_router(patients_router, prefix="/patients", tags=["Patients"])

# Include clinical management routes
# api_router.include_router(clinical_router, prefix="/clinical", tags=["Clinical"])

@api_router.get("/status", tags=["API"])
async def api_status():
    """API status endpoint."""
    return {
        "status": "operational",
        "version": "1.0",
        "endpoints": {
            "auth": "Authentication endpoints",
            "admin": "Administration endpoints", 
            "patients": "Patient management endpoints",
            "clinical": "Clinical management endpoints"
        }
    }