"""
Database initialization script for OdontoLab.
Creates tables and seeds initial data.
"""
import asyncio
from datetime import datetime, date
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

from app.core.database import Base
from app.core.config import get_settings
from app.core.security import hash_password
from app.domain.models import User, UserRole, Patient, ContactRequest


async def init_database():
    print('='*60)
    print('OdontoLab Database Initialization')
    print('='*60)
    
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    # Create tables
    print('Creating database tables...')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print('✓ Tables created!')
    
    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if users exist
        result = await session.execute(select(User))
        if result.scalars().first():
            print('Users already exist. Skipping.')
        else:
            print('Creating users...')
            users = [
                User(
                    email='admin@odontolab.com',
                    full_name='Administrador Principal',
                    hashed_password=hash_password('admin123'),
                    role=UserRole.ADMIN,
                    phone='0999999999',
                    is_active=True
                ),
                User(
                    email='dentista@odontolab.com',
                    full_name='Dr. Juan Pérez',
                    hashed_password=hash_password('dentista123'),
                    role=UserRole.DENTIST,
                    phone='0988888888',
                    is_active=True
                ),
                User(
                    email='recepcion@odontolab.com',
                    full_name='María González',
                    hashed_password=hash_password('recepcion123'),
                    role=UserRole.RECEPTIONIST,
                    phone='0977777777',
                    is_active=True
                )
            ]
            for user in users:
                session.add(user)
            await session.commit()
            print('✓ 3 users created!')
            
            # Get dentist and receptionist
            result = await session.execute(select(User).where(User.role==UserRole.DENTIST))
            dentist = result.scalars().first()
            result = await session.execute(select(User).where(User.role==UserRole.RECEPTIONIST))
            receptionist = result.scalars().first()
            
            # Create sample patients
            print('Creating sample patients...')
            patients = [
                Patient(
                    full_name='Carlos Rodríguez',
                    email='carlos@example.com',
                    phone='0987654321',
                    date_of_birth=date(1985, 3, 15),
                    address='Calle Principal 123',
                    blood_type='O+',
                    allergies=['Ninguna'],
                    emergency_contact_name='Ana Rodríguez',
                    emergency_contact_phone='0987654322',
                    created_by=receptionist.id
                ),
                Patient(
                    full_name='Laura Martínez',
                    email='laura@example.com',
                    phone='0976543210',
                    date_of_birth=date(1990, 7, 22),
                    address='Avenida Central 456',
                    blood_type='A+',
                    allergies=['Penicilina'],
                    emergency_contact_name='Pedro Martínez',
                    emergency_contact_phone='0976543211',
                    medical_conditions=['Hipertensión'],
                    created_by=receptionist.id
                ),
                Patient(
                    full_name='Roberto Sánchez',
                    email='roberto@example.com',
                    phone='0965432109',
                    date_of_birth=date(1992, 11, 5),
                    address='Boulevard Norte 789',
                    blood_type='B+',
                    emergency_contact_name='Luisa Sánchez',
                    emergency_contact_phone='0965432110',
                    created_by=dentist.id
                )
            ]
            for patient in patients:
                session.add(patient)
            await session.commit()
            print(f'✓ {len(patients)} patients created!')
            
            # Create contact requests
            print('Creating contact requests...')
            contacts = [
                ContactRequest(
                    full_name='Patricia López',
                    email='patricia@example.com',
                    phone='0954321098',
                    message='Me gustaría información sobre ortodoncia',
                    status='PENDING'
                ),
                ContactRequest(
                    full_name='Miguel Torres',
                    email='miguel@example.com',
                    phone='0943210987',
                    message='Solicito información sobre precios de implantes',
                    status='PENDING'
                )
            ]
            for contact in contacts:
                session.add(contact)
            await session.commit()
            print(f'✓ {len(contacts)} contact requests created!')
    
    await engine.dispose()
    
    print()
    print('='*60)
    print('✓ Database initialized successfully!')
    print('='*60)
    print()
    print('Default User Credentials:')
    print('-'*60)
    print('Admin:        admin@odontolab.com / admin123')
    print('Dentist:      dentista@odontolab.com / dentista123')
    print('Receptionist: recepcion@odontolab.com / recepcion123')
    print('-'*60)
    print()
    print('API: https://odontolab-backend.onrender.com')
    print('Docs: https://odontolab-backend.onrender.com/docs')
    print('='*60)


if __name__ == '__main__':
    asyncio.run(init_database())
