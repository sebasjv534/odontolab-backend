# 🚀 Resumen Ejecutivo - API OdontoLab

## 📌 Descripción del Proyecto

Este documento es una **especificación técnica completa** para desarrollar el backend de OdontoLab, un sistema de gestión odontológica. El frontend está implementado en Next.js 15.5.3 y espera conectarse con una API RESTful desarrollada en **FastAPI (Python 3.10+)** con **PostgreSQL** como base de datos y **autenticación JWT**.

### 🛠️ Stack Tecnológico Backend

**Framework:** FastAPI 0.109.0+  
**Base de Datos:** PostgreSQL 14+  
**ORM:** SQLAlchemy 2.0 + Alembic (migraciones)  
**Autenticación:** JWT con python-jose  
**Hashing:** Passlib con bcrypt  
**Validación:** Pydantic 2.5+  
**Servidor:** Uvicorn con workers async

---

## 🎯 Objetivos Principales

1. **Autenticación segura** con JWT (JSON Web Tokens)
2. **Control de acceso basado en roles** (Admin, Dentist, Receptionist)
3. **CRUD completo** para Usuarios, Pacientes e Historias Clínicas
4. **Dashboard dinámico** con estadísticas personalizadas por rol
5. **API pública** para formulario de contacto
6. **Sistema de paginación** para listados grandes
7. **Validaciones robustas** en todos los endpoints

---

## 🔐 Sistema de Roles y Permisos

### **Admin (Administrador)**

- ✅ Gestión completa de usuarios (crear, listar, editar, desactivar)
- ✅ Gestión completa de pacientes
- ✅ Ver todas las historias clínicas
- ✅ Eliminar registros
- ✅ Acceso a estadísticas globales

### **Dentist (Odontólogo)**

- ✅ Crear y editar sus propias historias clínicas
- ✅ Ver pacientes y sus historias
- ✅ Acceso a estadísticas personales
- ❌ No puede gestionar usuarios
- ❌ No puede crear/editar pacientes

### **Receptionist (Recepcionista)**

- ✅ Crear y editar pacientes
- ✅ Ver lista de pacientes
- ✅ Gestionar citas (futuro)
- ✅ Acceso a estadísticas de citas
- ❌ No puede gestionar usuarios
- ❌ No puede crear/editar historias clínicas

---

## 📊 Modelos de Datos

### 1️⃣ **User (Usuarios del Sistema)**

| Campo | Tipo | Descripción | Obligatorio |
|-------|------|-------------|-------------|
| id | UUID | Identificador único | ✅ |
| email | String(255) | Email único (username) | ✅ |
| password_hash | String(255) | Contraseña hasheada (bcrypt) | ✅ |
| first_name | String(100) | Nombre | ✅ |
| last_name | String(100) | Apellido | ✅ |
| role | Enum | 'admin', 'dentist', 'receptionist' | ✅ |
| is_active | Boolean | Estado del usuario | ✅ |
| created_at | Datetime | Fecha de creación | Auto |
| updated_at | Datetime | Última actualización | Auto |

**Índices:** email, role, is_active

---

### 2️⃣ **Patient (Pacientes)**

| Campo | Tipo | Descripción | Obligatorio |
|-------|------|-------------|-------------|
| id | UUID | Identificador único | ✅ |
| first_name | String(100) | Nombre | ✅ |
| last_name | String(100) | Apellido | ✅ |
| email | String(255) | Correo electrónico | ✅ |
| phone | String(20) | Teléfono | ✅ |
| date_of_birth | Date | Fecha de nacimiento | ✅ |
| address | Text | Dirección completa | ❌ |
| emergency_contact_name | String(100) | Contacto de emergencia | ❌ |
| emergency_contact_phone | String(20) | Teléfono de emergencia | ❌ |
| medical_conditions | Text/JSON | Condiciones médicas | ❌ |
| allergies | Text/JSON | Alergias | ❌ |
| created_at | Datetime | Fecha de creación | Auto |
| updated_at | Datetime | Última actualización | Auto |
| created_by | UUID (FK) | Usuario que creó el registro | ✅ |

**Índices:** email, phone, created_by, FULLTEXT(first_name, last_name)

---

### 3️⃣ **MedicalRecord (Historias Clínicas)**

| Campo | Tipo | Descripción | Obligatorio |
|-------|------|-------------|-------------|
| id | UUID | Identificador único | ✅ |
| patient_id | UUID (FK) | ID del paciente | ✅ |
| dentist_id | UUID (FK) | ID del odontólogo | ✅ |
| visit_date | Datetime | Fecha y hora de visita | ✅ |
| diagnosis | Text | Diagnóstico | ✅ |
| treatment | Text | Tratamiento realizado | ✅ |
| notes | Text | Notas adicionales | ❌ |
| teeth_chart | JSON | Odontograma digital | ❌ |
| next_appointment | Datetime | Próxima cita sugerida | ❌ |
| created_at | Datetime | Fecha de creación | Auto |
| updated_at | Datetime | Última actualización | Auto |

**Índices:** patient_id, dentist_id, visit_date

**Relaciones:**

- CASCADE DELETE con patients (si se elimina paciente, se eliminan historias)
- FOREIGN KEY con users(dentist_id)

---

### 4️⃣ **ContactRequest (Solicitudes de Contacto)**

| Campo | Tipo | Descripción | Obligatorio |
|-------|------|-------------|-------------|
| id | UUID | Identificador único | ✅ |
| nombre | String(100) | Nombre completo | ✅ |
| cedula | String(20) | Documento de identidad | ✅ |
| email | String(255) | Correo electrónico | ✅ |
| telefono | String(20) | Teléfono | ✅ |
| motivo | String(255) | Motivo de consulta | ✅ |
| servicio | Text | Tratamiento de interés | ❌ |
| acepta_politica | Boolean | Aceptación política datos | ✅ |
| status | Enum | 'pending', 'contacted', 'resolved' | Auto |
| created_at | Datetime | Fecha de creación | Auto |

**⚠️ IMPORTANTE:** Este endpoint es **PÚBLICO** (no requiere autenticación)

---

## 🔌 Endpoints Principales

### 🔐 **Autenticación**

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | /auth/login | Login con email y password | ❌ |
| GET | /auth/me | Obtener usuario autenticado | ✅ |
| POST | /auth/refresh | Refrescar access token | ✅ |

**Formato de Login:**

- Content-Type: `multipart/form-data`
- Campos: `username` (email), `password`
- Respuesta: `{access_token, token_type, user}`

---

### 👥 **Usuarios** (Solo Admin)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | /users/ | Crear usuario | Admin |
| GET | /users/ | Listar usuarios (paginado) | Admin |
| GET | /users/role/{role} | Usuarios por rol | Admin |
| PUT | /users/{id} | Actualizar usuario | Admin |
| PATCH | /users/{id}/deactivate | Desactivar usuario | Admin |

---

### 🏥 **Pacientes**

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | /patients/ | Crear paciente | Admin/Receptionist |
| GET | /patients/ | Listar pacientes (paginado) | ✅ |
| GET | /patients/{id} | Obtener paciente | ✅ |
| PUT | /patients/{id} | Actualizar paciente | Admin/Receptionist |
| GET | /patients/search?q={query} | Buscar pacientes | ✅ |
| DELETE | /patients/{id} | Eliminar paciente | Admin |

---

### 📋 **Historias Clínicas**

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | /medical-records/ | Crear historia | Dentist/Admin |
| GET | /medical-records/patient/{id} | Historias de paciente | ✅ |
| GET | /medical-records/{id} | Obtener historia | ✅ |
| PUT | /medical-records/{id} | Actualizar historia | Dentist*/Admin |
| GET | /medical-records/dentist/{id} | Historias de dentista | ✅ |
| DELETE | /medical-records/{id} | Eliminar historia | Admin |

**Dentist***: Solo puede editar sus propias historias

---

### 📊 **Dashboard**

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | /dashboard/stats | Estadísticas por rol | ✅ |
| GET | /dashboard/recent-activity | Actividad reciente | ✅ |

**Estadísticas por rol:**

**Admin:**

- total_patients, total_users, total_staff
- total_dentists, total_receptionists
- total_appointments, pending_appointments
- recent_records, monthly_revenue

**Dentist:**

- total_patients (asignados)
- total_appointments, pending_appointments
- recent_records (propios)

**Receptionist:**

- total_patients
- total_appointments, pending_appointments

---

### 📧 **Contacto** (Público)

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | /api/contact | Enviar solicitud de contacto | ❌ |

**Campos del formulario:**
```json
{
  "nombre": "string (obligatorio)",
  "cedula": "string (obligatorio, 7-15 dígitos)",
  "email": "string (obligatorio, formato email)",
  "telefono": "string (obligatorio, 7-10 dígitos)",
  "motivo": "string (obligatorio, min 10 caracteres)",
  "servicio": "string (opcional)",
  "aceptaPolitica": "boolean (obligatorio, debe ser true)"
}
```

**Acciones:**

1. Guardar en BD con status='pending'
2. Enviar email a admin@odontolab.com
3. (Opcional) Enviar confirmación al usuario

---

## 🔒 Seguridad y Autenticación JWT

### **Configuración JWT**

```python
SECRET_KEY = "clave-secura-generar-con-openssl"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
```

### **Estructura del Token**

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "admin|dentist|receptionist",
  "exp": 1234567890,
  "iat": 1234567890
}
```

### **Headers en Requests**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### **Almacenamiento en Frontend**

```javascript
localStorage.setItem('odontolab_token', access_token);
localStorage.setItem('odontolab_user', JSON.stringify(user));
```

---

## 📋 Formato de Respuestas

### **Respuestas Exitosas**

```json
{
  "success": true,
  "data": { /* objeto o array */ },
  "message": "Operation successful"
}
```

### **Respuestas con Paginación**

```json
{
  "success": true,
  "data": [ /* array de objetos */ ],
  "total": 150,
  "page": 1,
  "per_page": 10,
  "total_pages": 15
}
```

### **Respuestas de Error**

```json
{
  "detail": "Error message"
}
```

### **Errores de Validación**

```json
{
  "detail": "Validation error",
  "errors": {
    "email": ["Email already exists"],
    "password": ["Password must be at least 6 characters"]
  }
}
```

---

## 🎯 Usuarios de Prueba (Seeds)

```python
# Crear estos usuarios al inicializar la BD
users_seed = [
    {
        "email": "admin@odontolab.com",
        "password": "admin123",  # Hash con bcrypt
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin"
    },
    {
        "email": "dentist@odontolab.com",
        "password": "dentist123",
        "first_name": "Juan",
        "last_name": "Pérez",
        "role": "dentist"
    },
    {
        "email": "reception@odontolab.com",
        "password": "reception123",
        "first_name": "Ana",
        "last_name": "Martínez",
        "role": "receptionist"
    }
]
```

---

## ⚙️ Configuración del Entorno

### **Variables de Entorno (.env)**

```env
# Database PostgreSQL
DATABASE_URL=postgresql://username:password@localhost:5432/odontolab_db
# O para async:
# DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/odontolab_db

# JWT Configuration
SECRET_KEY=generar-con-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS - Frontend URLs
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Email Configuration (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=app-password-aqui
EMAIL_FROM=noreply@odontolab.com
ADMIN_EMAIL=admin@odontolab.com

# Application
APP_NAME=OdontoLab API
APP_VERSION=1.0.0
DEBUG=True
PORT=8000

# Database Connection Pool (Opcional)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_PRE_PING=True
```

### **Estructura del Proyecto FastAPI (Recomendada)**

```
backend/
├── alembic/                      # Migraciones de base de datos
│   ├── versions/                 # Archivos de migración
│   ├── env.py
│   └── alembic.ini
├── app/
│   ├── __init__.py
│   ├── main.py                   # Punto de entrada FastAPI
│   ├── config.py                 # Configuración y variables de entorno
│   ├── dependencies.py           # Dependencias globales (DB session, auth)
│   │
│   ├── api/                      # Endpoints organizados
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # Endpoints de autenticación
│   │   │   ├── users.py          # Endpoints de usuarios
│   │   │   ├── patients.py       # Endpoints de pacientes
│   │   │   ├── medical_records.py
│   │   │   ├── dashboard.py
│   │   │   └── contact.py
│   │   └── deps.py               # Dependencias de API (permisos, current_user)
│   │
│   ├── core/                     # Lógica de negocio core
│   │   ├── __init__.py
│   │   ├── security.py           # JWT, password hashing
│   │   ├── config.py             # Configuración de la app
│   │   └── exceptions.py         # Excepciones personalizadas
│   │
│   ├── models/                   # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── base.py               # Base class para modelos
│   │   ├── user.py
│   │   ├── patient.py
│   │   ├── medical_record.py
│   │   └── contact_request.py
│   │
│   ├── schemas/                  # Schemas Pydantic (validación)
│   │   ├── __init__.py
│   │   ├── user.py               # UserCreate, UserUpdate, UserInDB
│   │   ├── patient.py
│   │   ├── medical_record.py
│   │   ├── contact.py
│   │   └── token.py              # Token, TokenData
│   │
│   ├── crud/                     # Operaciones CRUD
│   │   ├── __init__.py
│   │   ├── base.py               # CRUD genérico base
│   │   ├── user.py               # CRUDUser
│   │   ├── patient.py            # CRUDPatient
│   │   └── medical_record.py
│   │
│   ├── db/                       # Configuración de base de datos
│   │   ├── __init__.py
│   │   ├── base.py               # Importar todos los modelos
│   │   ├── session.py            # Sesión de DB y engine
│   │   └── init_db.py            # Seeds iniciales
│   │
│   └── utils/                    # Utilidades
│       ├── __init__.py
│       ├── email.py              # Envío de emails
│       └── pagination.py         # Helpers de paginación
│
├── tests/                        # Tests
│   ├── __init__.py
│   ├── conftest.py
│   └── api/
│       └── test_auth.py
│
├── .env                          # Variables de entorno
├── .env.example                  # Ejemplo de variables
├── requirements.txt              # Dependencias
├── pyproject.toml               # Configuración del proyecto (opcional)
└── README.md
```

### **CORS Configuration (main.py)**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Database Session Configuration (db/session.py)**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create engine with connection pool
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    echo=settings.DEBUG  # Log SQL queries in debug mode
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 📦 Dependencias Python

```txt
# Core Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0

# Database & ORM
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9          # PostgreSQL adapter
asyncpg==0.29.0                 # Async PostgreSQL driver (opcional)

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Validation & Configuration
pydantic==2.5.3
pydantic-settings==2.1.0
email-validator==2.1.0

# Environment & Configuration
python-dotenv==1.0.0

# Optional (Recomendado)
fastapi-pagination==0.12.0      # Paginación automática
python-slugify==8.0.1           # Para slugs de URLs
```

---

## 🧪 Comandos de Prueba (cURL)

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -F "username=admin@odontolab.com" \
  -F "password=admin123"
```

### Crear Paciente

```bash
curl -X POST http://localhost:8000/patients/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "María",
    "last_name": "García",
    "email": "maria@email.com",
    "phone": "3001234567",
    "date_of_birth": "1990-05-15"
  }'
```

### Crear Historia Clínica

```bash
curl -X POST http://localhost:8000/medical-records/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "UUID_DEL_PACIENTE",
    "visit_date": "2025-01-20T14:30:00",
    "diagnosis": "Caries dental",
    "treatment": "Restauración con resina"
  }'
```

---

## 📞 Información del Frontend

**URL de Desarrollo:** http://localhost:3000  
**Framework:** Next.js 15.5.3 + React 19.1.0  
**Repositorio:** odontolab-ingenieria-web  
**Branch:** develop  

**Archivo de servicios API:** `src/lib/api.ts`  
**Tipos TypeScript:** `src/types/index.ts`  
**Hook de Auth:** `src/hooks/useAuth.ts`  

---

## 🎯 Puntos Críticos

### ⚠️ **MUY IMPORTANTE**

1. **JWT Secret Key:** Generar con `openssl rand -hex 32`
2. **Passwords:** SIEMPRE hashear con bcrypt (factor 12+)
3. **UUIDs:** Usar UUID v4 para todos los IDs
4. **Timestamps:** Almacenar en UTC
5. **CORS:** Configurar correctamente para localhost:3000
6. **Validaciones:** Validar TODOS los inputs
7. **Permisos:** Verificar roles en CADA endpoint
8. **Cascade Delete:** Patient -> MedicalRecords
9. **Paginación:** Default: page=1, per_page=10
10. **Búsqueda:** Case-insensitive en búsqueda de pacientes

---

## � Implementación de Autenticación JWT con FastAPI

### **Instalación de Dependencias**

```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

### **Configuración de Seguridad (app/core/security.py)**

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# Configuración
SECRET_KEY = "YOUR_SECRET_KEY_HERE"  # Generar con: openssl rand -hex 32
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera hash de contraseña con bcrypt"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decodifica y valida el token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

### **Dependencias de Autenticación (app/api/deps.py)**

```python
from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import oauth2_scheme, decode_token
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.user import RoleEnum

def get_db() -> Generator:
    """Dependencia para obtener sesión de BD"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Obtiene el usuario actual desde el token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verifica que el usuario esté activo"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

def require_role(allowed_roles: list[RoleEnum]):
    """Decorador para verificar roles"""
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker

# Shortcuts para roles comunes
require_admin = require_role([RoleEnum.admin])
require_dentist = require_role([RoleEnum.dentist])
require_receptionist = require_role([RoleEnum.receptionist, RoleEnum.admin])
```

### **Endpoint de Login (app/api/v1/auth.py)**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.api.deps import get_db, get_current_active_user
from app.core.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.user import User
from app.schemas.auth import Token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Endpoint de autenticación"""
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Obtiene información del usuario actual"""
    return current_user
```

### **Ejemplo de Uso en Endpoints Protegidos**

```python
from app.api.deps import require_admin, require_dentist, require_receptionist

# Endpoint solo para administradores
@router.post("/users/", dependencies=[Depends(require_admin)])
async def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # Solo admin puede crear usuarios
    return create_user_logic(db, user_in)

# Endpoint solo para dentistas
@router.post("/medical-records/", dependencies=[Depends(require_dentist)])
async def create_medical_record(
    record_in: MedicalRecordCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Solo dentistas pueden crear historias clínicas
    return create_record_logic(db, record_in, current_user.id)

# Endpoint para recepcionistas y admins
@router.post("/patients/", dependencies=[Depends(require_receptionist)])
async def create_patient(patient_in: PatientCreate, db: Session = Depends(get_db)):
    # Recepcionistas y admins pueden crear pacientes
    return create_patient_logic(db, patient_in)
```

---

## 🗄️ Configuración de Alembic (Migraciones)

### **Instalación**

```bash
pip install alembic
alembic init alembic
```

### **Configurar alembic.ini**

```ini
sqlalchemy.url = postgresql://username:password@localhost:5432/odontolab_db
```

### **Configurar alembic/env.py**

```python
from app.db.base import Base  # Importa todos los modelos
from app.core.config import settings

target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

### **Comandos de Migraciones**

```bash
# Crear migración automática
alembic revision --autogenerate -m "Create users table"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial
alembic history

# Resetear BD (con precaución)
alembic downgrade base
alembic upgrade head
```

---

## ✅ Checklist de Implementación

### **Fase 1: Setup Inicial** (Día 1)

- [ ] Crear proyecto FastAPI con estructura modular
- [ ] Configurar PostgreSQL (crear base de datos)
- [ ] Configurar variables de entorno (.env)
- [ ] Instalar dependencias (requirements.txt)
- [ ] Configurar SQLAlchemy con PostgreSQL
- [ ] Configurar Alembic para migraciones
- [ ] Configurar CORS para Next.js
- [ ] Crear archivo main.py con app FastAPI
- [ ] Implementar health check endpoint (GET /)

### **Fase 2: Modelos y Base de Datos** (Día 2)

- [ ] Crear modelo Base con timestamps automáticos
- [ ] Implementar modelo User con enum de roles
- [ ] Implementar modelo Patient
- [ ] Implementar modelo MedicalRecord
- [ ] Implementar modelo ContactRequest
- [ ] Configurar relaciones (Foreign Keys, CASCADE)
- [ ] Crear primera migración con Alembic
- [ ] Aplicar migración a BD
- [ ] Crear índices necesarios (email, phone, etc.)

### **Fase 3: Schemas Pydantic** (Día 3)

- [ ] Schema base con ConfigDict
- [ ] UserCreate, UserUpdate, UserInDB schemas
- [ ] PatientCreate, PatientUpdate, PatientInDB
- [ ] MedicalRecordCreate, MedicalRecordUpdate
- [ ] ContactRequestCreate
- [ ] Token, TokenData schemas
- [ ] Response models (ApiResponse, PaginatedResponse)
- [ ] Configurar from_attributes en schemas

### **Fase 4: Autenticación JWT** (Día 4)

- [ ] Implementar password hashing con passlib
- [ ] Crear función verify_password
- [ ] Crear función get_password_hash
- [ ] Implementar create_access_token
- [ ] Implementar decode_token con manejo de errores
- [ ] Crear dependency get_current_user
- [ ] Crear dependency get_current_active_user
- [ ] Decoradores de verificación de roles
- [ ] POST /auth/login (OAuth2PasswordRequestForm)
- [ ] GET /auth/me
- [ ] POST /auth/refresh

### **Fase 5: CRUD Base** (Día 5)

- [ ] Crear clase CRUDBase genérica
- [ ] Implementar get (by ID)
- [ ] Implementar get_multi (con paginación)
- [ ] Implementar create
- [ ] Implementar update
- [ ] Implementar delete / soft delete
- [ ] Implementar búsqueda con filtros

### **Fase 6: Endpoints de Usuarios** (Día 6)

- [ ] POST /users/ (admin only)
- [ ] GET /users/ (paginado, admin only)
- [ ] GET /users/{id} (admin only)
- [ ] GET /users/role/{role} (admin only)
- [ ] PUT /users/{id} (admin only)
- [ ] PATCH /users/{id}/deactivate (admin only)
- [ ] Middleware de verificación de permisos
- [ ] Tests unitarios de endpoints

### **Fase 7: Endpoints de Pacientes** (Día 7)

- [ ] POST /patients/ (receptionist/admin)
- [ ] GET /patients/ (paginado)
- [ ] GET /patients/{id}
- [ ] PUT /patients/{id} (receptionist/admin)
- [ ] GET /patients/search (full-text search)
- [ ] DELETE /patients/{id} (admin only)
- [ ] Validaciones de campos
- [ ] Tests unitarios

### **Fase 8: Endpoints de Historias Clínicas** (Día 8)

- [ ] POST /medical-records/ (dentist only)
- [ ] GET /medical-records/patient/{id}
- [ ] GET /medical-records/{id}
- [ ] PUT /medical-records/{id} (owner/admin)
- [ ] GET /medical-records/dentist/{id}
- [ ] DELETE /medical-records/{id} (admin only)
- [ ] Validación: dentist solo edita propias
- [ ] Tests unitarios

### **Fase 9: Dashboard & Estadísticas** (Día 9)

- [ ] GET /dashboard/stats (filtrado por rol)
- [ ] Queries optimizadas con COUNT, GROUP BY
- [ ] Caché de estadísticas (opcional)
- [ ] GET /dashboard/recent-activity
- [ ] Sistema de logs de actividad
- [ ] Tests de performance

### **Fase 10: Endpoint Público de Contacto** (Día 10)

- [ ] POST /api/contact (sin autenticación)
- [ ] Validaciones robustas
- [ ] Implementar envío de emails con SMTP
- [ ] Email a admin con datos del contacto
- [ ] Email de confirmación al usuario (opcional)
- [ ] Rate limiting para prevenir spam
- [ ] Tests de integración

### **Fase 11: Seeds y Datos de Prueba** (Día 11)

- [ ] Script de inicialización (init_db.py)
- [ ] Crear usuarios seed (admin, dentist, receptionist)
- [ ] Crear pacientes de ejemplo
- [ ] Crear historias clínicas de ejemplo
- [ ] Comando para resetear BD
- [ ] Documentar credenciales de prueba

### **Fase 12: Testing, Documentación & Deploy** (Día 12-14)

- [ ] Tests unitarios completos (pytest)
- [ ] Tests de integración
- [ ] Tests de autenticación y permisos
- [ ] Documentación Swagger/OpenAPI automática
- [ ] README del backend
- [ ] Guía de instalación y configuración
- [ ] Docker & Docker Compose (opcional)
- [ ] CI/CD con GitHub Actions (opcional)
- [ ] Deploy en servidor (Railway, Render, AWS)

---

## �📚 Documentación Adicional

Ver archivo completo: **`API_SPECIFICATIONS.md`** para:

- Ejemplos detallados de requests/responses
- Casos de prueba específicos
- Estructura completa del odontograma (teeth_chart)
- Configuración de email SMTP
- Más ejemplos de validaciones

---

**Creado:** 23 de Octubre de 2025  
**Versión:** 1.0.0  
**Para:** Desarrollo Backend OdontoLab API
