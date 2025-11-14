#!/usr/bin/env python
"""
Script para inicializar la base de datos en Render.
Optimizado para el plan gratuito con manejo de conexiones lentas.
"""
import asyncio
import sys
import os
from datetime import datetime, date
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

from app.core.database import Base
from app.core.config import get_settings
from app.core.security import hash_password
from app.domain.models import User, UserRole, Patient, ContactRequest


async def wait_for_db(engine, max_attempts=10):
    """Esperar a que la base de datos esté disponible."""
    for attempt in range(max_attempts):
        try:
            async with engine.connect() as conn:
                await conn.execute(select(1))
            print('✓ Database connection established!')
            return True
        except Exception as e:
            print(f'Waiting for database... (attempt {attempt + 1}/{max_attempts})')
            if attempt < max_attempts - 1:
                await asyncio.sleep(3)
            else:
                print(f'✗ Could not connect to database: {str(e)}')
                return False
    return False


async def init_database():
    """Inicializa la base de datos con datos iniciales."""
    print('\n' + '='*60)
    print('🚀 OdontoLab Database Initialization - Render Deployment')
    print('='*60 + '\n')
    
    try:
        settings = get_settings()
        
        # Convertir DATABASE_URL a asyncpg si es necesario
        db_url = settings.DATABASE_URL
        if db_url.startswith('postgresql://'):
            db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
        
        print(f'📊 Database URL configured: {db_url[:30]}...')
        
        # Crear engine con configuración optimizada para Render free tier
        engine = create_async_engine(
            db_url,
            echo=False,
            pool_size=2,
            max_overflow=0,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                "timeout": 60,
                "command_timeout": 60,
                "server_settings": {
                    "application_name": "odontolab_init"
                }
            }
        )
        
        # Esperar a que la base de datos esté disponible
        print('\n⏳ Waiting for database connection...')
        if not await wait_for_db(engine):
            print('\n✗ Failed to connect to database')
            sys.exit(1)
        
        # Crear tablas
        print('\n📋 Creating database tables...')
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print('✓ Tables created successfully!')
        except Exception as e:
            print(f'✗ Error creating tables: {str(e)}')
            raise
        
        # Crear sesión
        async_session = sessionmaker(
            engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
        
        async with async_session() as session:
            # Verificar si ya existen usuarios
            print('\n🔍 Checking existing data...')
            result = await session.execute(select(User))
            existing_user = result.scalars().first()
            
            if existing_user:
                print('✓ Users already exist. Database is already initialized.')
                print('\n' + '='*60)
                print('✅ Database is ready!')
                print('='*60 + '\n')
                await engine.dispose()
                return True
            
            # Crear usuarios
            print('\n👥 Creating default users...')
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
            print('✓ 3 users created successfully!')
            
            # Obtener usuarios para asignar a pacientes
            result = await session.execute(
                select(User).where(User.role == UserRole.DENTIST)
            )
            dentist = result.scalars().first()
            
            result = await session.execute(
                select(User).where(User.role == UserRole.RECEPTIONIST)
            )
            receptionist = result.scalars().first()
            
            # Crear pacientes de ejemplo
            print('\n🏥 Creating sample patients...')
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
            
            # Crear solicitudes de contacto
            print('\n📧 Creating contact requests...')
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
        
        # Mostrar credenciales
        print('\n' + '='*60)
        print('✅ Database initialized successfully!')
        print('='*60)
        print('\n🔐 Default User Credentials:')
        print('-'*60)
        print('Admin:        admin@odontolab.com / admin123')
        print('Dentist:      dentista@odontolab.com / dentista123')
        print('Receptionist: recepcion@odontolab.com / recepcion123')
        print('-'*60)
        print('\n⚠️  IMPORTANT: Change these passwords after first deployment!')
        print('\n📚 API Documentation: https://[your-app].onrender.com/docs')
        print('='*60 + '\n')
        
        return True
        
    except Exception as e:
        print(f'\n✗ Error during initialization: {str(e)}')
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    try:
        success = asyncio.run(init_database())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print('\n\n✗ Initialization cancelled by user')
        sys.exit(1)
    except Exception as e:
        print(f'\n✗ Fatal error: {str(e)}')
        sys.exit(1)
