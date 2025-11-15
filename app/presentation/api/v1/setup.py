"""
Endpoint de registro inicial del administrador.
Solo para ambiente educativo - Se desactiva después del primer registro.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr, Field

from app.core.database import get_db, engine, Base
from app.core.security import hash_password
from app.domain.models import User, UserRole

router = APIRouter(tags=["Setup"])


class AdminRegistrationRequest(BaseModel):
    """Schema para registro del primer administrador."""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Contraseña mínimo 6 caracteres")
    full_name: str = Field(..., min_length=3, description="Nombre completo")
    phone: str = Field(..., min_length=10, max_length=15, description="Teléfono")


@router.post("/setup/register-admin")
async def register_first_admin(
    data: AdminRegistrationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Registra el primer administrador del sistema.
    
    **🔧 Crea las tablas automáticamente si no existen**.
    
    **Solo para ambiente educativo**: Este endpoint se desactiva automáticamente 
    después de registrar el primer usuario.
    
    **Uso**:
    ```bash
    curl -X POST https://tu-app.onrender.com/api/v1/setup/register-admin \
         -H "Content-Type: application/json" \
         -d '{
           "email": "admin@odontolab.com",
           "password": "tupassword",
           "full_name": "Administrador Principal",
           "phone": "0999999999"
         }'
    ```
    
    **Respuesta exitosa**:
    ```json
    {
      "status": "success",
      "message": "Administrador registrado exitosamente",
      "admin": {
        "id": 1,
        "email": "admin@odontolab.com",
        "full_name": "Administrador Principal",
        "role": "ADMIN"
      },
      "credentials": {
        "email": "admin@odontolab.com",
        "password": "[tu password]"
      },
      "next_steps": "Usa estas credenciales para hacer login en /api/v1/auth/login"
    }
    ```
    """
    try:
        # PASO 1: Crear tablas si no existen
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # PASO 2: Verificar si ya existe algún usuario
        result = await db.execute(select(User))
        existing_users = result.scalars().all()
        
        if len(existing_users) > 0:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Sistema ya inicializado",
                    "message": "Ya existe al menos un usuario registrado. Este endpoint está desactivado.",
                    "hint": "Usa /api/v1/auth/login para acceder con tus credenciales existentes"
                }
            )
        
        # Verificar que el email no esté en uso (redundante pero seguro)
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalars().first():
            raise HTTPException(
                status_code=400,
                detail="El email ya está registrado"
            )
        
        # Crear el primer administrador
        admin = User(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            role=UserRole.ADMIN,
            phone=data.phone,
            is_active=True
        )
        
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        
        return {
            "status": "success",
            "message": "✅ Administrador registrado exitosamente",
            "database_initialized": True,
            "admin": {
                "id": admin.id,
                "email": admin.email,
                "full_name": admin.full_name,
                "role": admin.role.value,
                "phone": admin.phone
            },
            "credentials": {
                "email": data.email,
                "password": data.password
            },
            "next_steps": [
                "1. Guarda estas credenciales en un lugar seguro",
                "2. Haz login en /api/v1/auth/login",
                "3. Usa el token para acceder a los endpoints protegidos",
                "4. Crea otros usuarios (dentistas, recepcionistas) desde /api/v1/users"
            ],
            "warning": "⚠️ Este endpoint ahora está desactivado. Solo el primer registro es permitido.",
            "api_docs": "https://odontolab-api.onrender.com/docs"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al registrar administrador: {str(e)}"
        )


@router.get("/setup/status")
async def check_setup_status(db: AsyncSession = Depends(get_db)):
    """
    Verifica el estado de inicialización del sistema.
    
    **Público**: No requiere autenticación.
    
    **Respuesta cuando NO hay usuarios**:
    ```json
    {
      "initialized": false,
      "message": "Sistema sin inicializar",
      "action": "Registra el primer admin en /api/v1/setup/register-admin"
    }
    ```
    
    **Respuesta cuando YA hay usuarios**:
    ```json
    {
      "initialized": true,
      "users_count": 3,
      "message": "Sistema inicializado",
      "action": "Usa /api/v1/auth/login para acceder"
    }
    ```
    """
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        if len(users) == 0:
            return {
                "initialized": False,
                "users_count": 0,
                "message": "Sistema sin inicializar",
                "action": "Registra el primer administrador en /api/v1/setup/register-admin",
                "endpoint": "/api/v1/setup/register-admin",
                "method": "POST"
            }
        else:
            return {
                "initialized": True,
                "users_count": len(users),
                "message": "Sistema inicializado correctamente",
                "action": "Usa /api/v1/auth/login para acceder al sistema",
                "endpoint": "/api/v1/auth/login",
                "method": "POST"
            }
    except Exception as e:
        return {
            "initialized": False,
            "error": str(e),
            "message": "Error al verificar estado del sistema"
        }
