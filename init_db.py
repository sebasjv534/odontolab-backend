"""
Database initialization script for the odontology system.

This script creates the database tables and initializes default roles
and a default administrator user.
"""

import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.config import get_settings
from app.domain.models.role_model import Role, RoleType
from app.domain.models.user_model import User
from app.domain.models.profile_models import AdministratorProfile
from app.core.security import hash_password


async def init_database():
    """
    Initialize the database with tables and default data.
    """
    settings = get_settings()
    
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Check if roles already exist
        from sqlalchemy.future import select
        result = await session.execute(select(Role))
        existing_roles = result.scalars().all()
        
        if not existing_roles:
            print("Creating default roles...")
            
            # Create default roles
            roles = [
                Role(
                    id=uuid.uuid4(),
                    name=RoleType.ADMINISTRATOR.value,
                    description="System administrator with full access",
                    permissions='{"all": true}'
                ),
                Role(
                    id=uuid.uuid4(),
                    name=RoleType.DENTIST.value,
                    description="Dentist with access to clinical records and interventions",
                    permissions='{"clinical": true, "patients": true}'
                ),
                Role(
                    id=uuid.uuid4(),
                    name=RoleType.RECEPTIONIST.value,
                    description="Receptionist with access to patient management",
                    permissions='{"patients": true, "appointments": true}'
                )
            ]
            
            for role in roles:
                session.add(role)
            
            await session.commit()
            print("Default roles created successfully!")
            
            # Get administrator role
            admin_role_result = await session.execute(
                select(Role).where(Role.name == RoleType.ADMINISTRATOR.value)
            )
            admin_role = admin_role_result.scalar_one()
            
            # Check if admin user exists
            admin_user_result = await session.execute(
                select(User).where(User.email == "admin@odontolab.com")
            )
            existing_admin = admin_user_result.scalar_one_or_none()
            
            if not existing_admin:
                print("Creating default administrator user...")
                
                # Create default admin user
                admin_user = User(
                    id=uuid.uuid4(),
                    email="admin@odontolab.com",
                    password_hash=hash_password("admin123456"),
                    first_name="System",
                    last_name="Administrator",
                    is_active=True,
                    is_verified=True,
                    role_id=admin_role.id
                )
                
                session.add(admin_user)
                await session.commit()
                await session.refresh(admin_user)
                
                # Create administrator profile
                admin_profile = AdministratorProfile(
                    id=uuid.uuid4(),
                    user_id=admin_user.id,
                    department="IT",
                    permissions_level="full"
                )
                
                session.add(admin_profile)
                await session.commit()
                
                print("Default administrator user created successfully!")
                print("Email: admin@odontolab.com")
                print("Password: admin123456")
                print("Please change the password after first login!")
            
        else:
            print("Roles already exist. Skipping role creation.")
    
    await engine.dispose()
    print("Database initialization completed!")


if __name__ == "__main__":
    asyncio.run(init_database())