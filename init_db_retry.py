#!/usr/bin/env python
"""
Script para inicializar la base de datos con manejo de reintentos.
Optimizado para el plan gratuito de Render con timeouts.
"""
import asyncio
import sys
from datetime import datetime, date
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

from app.core.database import Base
from app.core.config import get_settings
from app.core.security import hash_password
from app.domain.models import User, UserRole, Patient, ContactRequest


async def init_database_with_retry(max_retries=3):
    """Inicializa la base de datos con reintentos en caso de timeout."""
    
    for attempt in range(max_retries):
        try:
            print(f'\n{"="*60}')
            print(f'OdontoLab Database Initialization - Attempt {attempt + 1}/{max_retries}')
            print(f'{"="*60}\n')
            
            settings = get_settings()
            
            # Crear engine con timeouts más largos
            engine = create_async_engine(
                settings.DATABASE_URL,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={
                    "timeout": 30,
                    "command_timeout": 30,
                }
            )
            
            # Crear tablas
            print('Creating database tables...')
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            print('✓ Tables created successfully!\n')
            
            # Crear sesión
            async_session = sessionmaker(
                engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )
            
            async with async_session() as session:
                # Verificar si ya existen usuarios
                result = await session.execute(select(User))
                existing_user = result.scalars().first()
                
                if existing_user:
                    print('✓ Users already exist. Database is initialized.')
                    print(f'\n{"="*60}')
                    print('Database ready to use!')
                    print(f'{"="*60}\n')
                    await engine.dispose()
                    return True
                
                # Crear usuarios
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
                print('✓ 3 users created!\n')
                
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
                print(f'✓ {len(patients)} patients created!\n')
                
                # Crear solicitudes de contacto
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
                print(f'✓ {len(contacts)} contact requests created!\n')
            
            await engine.dispose()
            
            # Mostrar credenciales
            print(f'{"="*60}')
            print('✓ Database initialized successfully!')
            print(f'{"="*60}\n')
            print('Default User Credentials:')
            print('-'*60)
            print('Admin:        admin@odontolab.com / admin123')
            print('Dentist:      dentista@odontolab.com / dentista123')
            print('Receptionist: recepcion@odontolab.com / recepcion123')
            print('-'*60)
            print('\nAPI: https://odontolab-backend.onrender.com')
            print('Docs: https://odontolab-backend.onrender.com/docs')
            print(f'{"="*60}\n')
            
            return True
            
        except asyncio.TimeoutError:
            print(f'\n✗ Timeout on attempt {attempt + 1}')
            if attempt < max_retries - 1:
                print(f'Retrying in 5 seconds...\n')
                await asyncio.sleep(5)
            else:
                print('\n✗ Failed after all retries due to timeout')
                print('This is common on Render free tier.')
                print('\nYou can run this script manually from Render Shell:')
                print('  1. Go to Render Dashboard → Your Service → Shell')
                print('  2. Run: python init_db_retry.py')
                return False
                
        except Exception as e:
            print(f'\n✗ Error on attempt {attempt + 1}: {str(e)}')
            if attempt < max_retries - 1:
                print(f'Retrying in 5 seconds...\n')
                await asyncio.sleep(5)
            else:
                print(f'\n✗ Failed after all retries: {str(e)}')
                return False
    
    return False


if __name__ == '__main__':
    success = asyncio.run(init_database_with_retry())
    sys.exit(0 if success else 1)
