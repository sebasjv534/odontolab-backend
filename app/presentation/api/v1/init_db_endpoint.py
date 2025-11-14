#!/usr/bin/env python
"""
Endpoint HTTP para inicializar la base de datos remotamente.
Alternativa al Shell para plan gratuito de Render.
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
import asyncio
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db, Base, engine
from app.core.security import hash_password
from app.domain.models import User, UserRole, Patient, ContactRequest

router = APIRouter(tags=["Database Init"])


async def verify_init_token(x_init_token: Optional[str] = Header(None)):
    """Verificar token de seguridad para inicialización."""
    import os
    expected_token = os.getenv("INIT_DB_TOKEN", "")
    
    if not expected_token:
        raise HTTPException(
            status_code=500,
            detail="INIT_DB_TOKEN not configured"
        )
    
    if x_init_token != expected_token:
        raise HTTPException(
            status_code=403,
            detail="Invalid initialization token"
        )
    
    return True


@router.post("/init-database")
async def initialize_database_endpoint(
    db: AsyncSession = Depends(get_db),
    authorized: bool = Depends(verify_init_token)
):
    """
    Inicializa la base de datos con datos por defecto.
    
    **Seguridad**: Requiere header X-Init-Token con el token configurado.
    
    **Uso**:
    ```bash
    curl -X POST https://tu-app.onrender.com/api/v1/init-database \
         -H "X-Init-Token: tu-token-secreto"
    ```
    """
    try:
        # Verificar si ya hay usuarios
        result = await db.execute(select(User))
        existing_user = result.scalars().first()
        
        if existing_user:
            return {
                "status": "already_initialized",
                "message": "Database already contains users",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Crear usuarios por defecto
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
            db.add(user)
        
        await db.commit()
        
        # Obtener usuarios creados
        result = await db.execute(select(User).where(User.role == UserRole.DENTIST))
        dentist = result.scalars().first()
        
        result = await db.execute(select(User).where(User.role == UserRole.RECEPTIONIST))
        receptionist = result.scalars().first()
        
        # Crear pacientes de ejemplo
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
            db.add(patient)
        
        await db.commit()
        
        # Crear solicitudes de contacto
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
            db.add(contact)
        
        await db.commit()
        
        return {
            "status": "success",
            "message": "Database initialized successfully",
            "users_created": len(users),
            "patients_created": len(patients),
            "contacts_created": len(contacts),
            "credentials": {
                "admin": "admin@odontolab.com / admin123",
                "dentist": "dentista@odontolab.com / dentista123",
                "receptionist": "recepcion@odontolab.com / recepcion123"
            },
            "warning": "⚠️ Change default passwords immediately!",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing database: {str(e)}"
        )


@router.get("/check-init-status")
async def check_initialization_status(db: AsyncSession = Depends(get_db)):
    """
    Verifica si la base de datos ya está inicializada.
    
    **Público**: No requiere autenticación.
    """
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        return {
            "initialized": len(users) > 0,
            "users_count": len(users),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "initialized": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
