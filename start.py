#!/usr/bin/env python3
"""
Database initialization script for OdontoLab API.

This script initializes the database tables on first deployment.
"""

import asyncio
import sys
import os

async def init_database():
    """Initialize database tables if they don't exist."""
    try:
        from app.core.database import engine, Base
        # Import all models to register them with SQLAlchemy
        from app.domain.models.user_model import User
        from app.domain.models.role_model import Role
        from app.domain.models.profile_models import DentistProfile, ReceptionistProfile, AdministratorProfile
        from app.domain.models.clinical_models import Patient, ClinicalIntervention
        
        print("🗄️ Initializing database tables...")
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Don't exit with error in production, let the app start anyway
        print("⚠️ Continuing without database initialization...")

async def main():
    """Main function."""
    await init_database()

if __name__ == "__main__":
    asyncio.run(main())