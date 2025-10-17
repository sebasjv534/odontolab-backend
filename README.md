# OdontoLab Backend API

Una API REST completa para la gestión de clínicas odontológicas, construida con FastAPI, PostgreSQL y SQLAlchemy. Incluye autenticación JWT, gestión de usuarios basada en roles, y funcionalidades específicas para administradores, dentistas y recepcionistas.

## 🚀 Características Principales

### Autenticación y Autorización
- **JWT (JSON Web Tokens)** para autenticación segura
- **Sistema de roles** con permisos específicos:
  - **Administrador**: Gestión completa del sistema y usuarios
  - **Dentista**: Gestión de registros clínicos e intervenciones
  - **Recepcionista**: Gestión de pacientes y citas

### Gestión de Usuarios
- Registro y autenticación de usuarios
- Perfiles específicos por rol
- Gestión de credenciales y permisos
- Sistema de activación/desactivación de cuentas

### Gestión Clínica
- **Gestión de Pacientes**: Registro completo con datos médicos
- **Registros Clínicos**: Historial médico detallado
- **Intervenciones Dentales**: Registro de procedimientos y tratamientos
- **Búsqueda y Filtrado**: Sistema avanzado de búsqueda

### Arquitectura
- **Clean Architecture** con separación de capas
- **Repository Pattern** para acceso a datos
- **Dependency Injection** para inversión de dependencias
- **Async/Await** para operaciones no bloqueantes

## 🛠️ Stack Tecnológico

- **Framework**: FastAPI 0.104+
- **Base de Datos**: PostgreSQL con SQLAlchemy (async)
- **Autenticación**: JWT con python-jose
- **Validación**: Pydantic v2
- **Migraciones**: Alembic
- **Testing**: pytest con pytest-asyncio
- **Seguridad**: bcrypt para hashing de contraseñas
- **Documentación**: OpenAPI/Swagger automática

## 📋 Requisitos Previos

- Python 3.11+
- PostgreSQL 13+
- pip o poetry para gestión de dependencias

## 🔧 Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd odontolab-backend
```

### 2. Crear Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Copiar el archivo de ejemplo y configurar las variables:

```bash
cp .env.example .env
```

Editar el archivo `.env` con tus configuraciones:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/odontolab_db

# JWT Configuration
SECRET_KEY=your-super-secret-key-at-least-32-characters-long-for-jwt-security
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Application Configuration
PROJECT_NAME=OdontoLab API
VERSION=1.0.0
DEBUG=false
ENVIRONMENT=development

# API Configuration  
API_V1_STR=/api/v1
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### 5. Configurar Base de Datos

Crear la base de datos PostgreSQL:

```sql
CREATE DATABASE odontolab_db;
CREATE USER odontolab_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE odontolab_db TO odontolab_user;
```

### 6. Inicializar Base de Datos

Ejecutar el script de inicialización:

```bash
python init_db.py
```

Este script:
- Crea todas las tablas necesarias
- Inserta los roles por defecto (administrador, dentista, recepcionista)
- Crea un usuario administrador por defecto:
  - **Email**: admin@odontolab.com
  - **Password**: admin123456

⚠️ **IMPORTANTE**: Cambiar la contraseña del administrador después del primer login.

## 🚀 Ejecución

### Desarrollo

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Producción

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

La API estará disponible en:
- **URL Base**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 Documentación de la API

### Endpoints Principales

#### Autenticación
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/refresh` - Refrescar token

#### Gestión de Usuarios (Solo Administradores)
- `POST /api/v1/admin/users/administrator` - Crear administrador
- `POST /api/v1/admin/users/dentist` - Crear dentista
- `POST /api/v1/admin/users/receptionist` - Crear recepcionista
- `GET /api/v1/admin/users` - Listar usuarios
- `GET /api/v1/admin/users/{user_id}` - Obtener usuario específico
- `PUT /api/v1/admin/users/{user_id}` - Actualizar usuario
- `DELETE /api/v1/admin/users/{user_id}` - Eliminar usuario

#### Gestión de Pacientes (Recepcionistas)
- `POST /api/v1/patients` - Registrar paciente
- `GET /api/v1/patients` - Listar pacientes
- `GET /api/v1/patients/{patient_id}` - Obtener paciente específico
- `PUT /api/v1/patients/{patient_id}` - Actualizar paciente
- `GET /api/v1/patients/search?q={query}` - Buscar pacientes

#### Gestión Clínica (Dentistas)
- `POST /api/v1/clinical/records` - Crear registro clínico
- `GET /api/v1/clinical/records` - Listar registros clínicos
- `GET /api/v1/clinical/records/{record_id}` - Obtener registro específico
- `PUT /api/v1/clinical/records/{record_id}` - Actualizar registro

- `POST /api/v1/clinical/interventions` - Crear intervención
- `GET /api/v1/clinical/interventions` - Listar intervenciones
- `GET /api/v1/clinical/interventions/{intervention_id}` - Obtener intervención específica
- `PUT /api/v1/clinical/interventions/{intervention_id}` - Actualizar intervención

### Modelos de Datos

#### Usuario
```json
{
  \"id\": \"uuid\",
  \"email\": \"string\",
  \"first_name\": \"string\",
  \"last_name\": \"string\",
  \"is_active\": \"boolean\",
  \"role\": \"string\",
  \"created_at\": \"datetime\"
}
```

#### Paciente
```json
{
  \"id\": \"uuid\",
  \"first_name\": \"string\",
  \"last_name\": \"string\",
  \"document_type\": \"string\",
  \"document_number\": \"string\",
  \"email\": \"string\",
  \"phone\": \"string\",
  \"date_of_birth\": \"date\",
  \"gender\": \"string\",
  \"blood_type\": \"string\",
  \"address\": \"string\",
  \"city\": \"string\",
  \"insurance_provider\": \"string\",
  \"insurance_number\": \"string\",
  \"allergies\": \"string\",
  \"medical_conditions\": \"string\",
  \"medications\": \"string\",
  \"age\": \"integer\",
  \"created_at\": \"datetime\"
}
```

#### Intervención Dental
```json
{
  \"id\": \"uuid\",
  \"clinical_record_id\": \"uuid\",
  \"dentist_id\": \"uuid\",
  \"intervention_type\": \"string\",
  \"tooth_number\": \"string\",
  \"procedure_description\": \"string\",
  \"materials_used\": \"string\",
  \"duration_minutes\": \"string\",
  \"cost\": \"decimal\",
  \"notes\": \"string\",
  \"performed_at\": \"datetime\",
  \"created_at\": \"datetime\"
}
```

## 🏗️ Arquitectura del Sistema

### Estructura de Carpetas

```
app/
├── __init__.py
├── main.py                     # Punto de entrada de la aplicación
├── core/                       # Configuración y utilidades centrales
│   ├── __init__.py
│   ├── config.py              # Configuración de la aplicación
│   ├── database.py            # Configuración de base de datos
│   └── security.py            # Utilidades de seguridad
├── domain/                     # Capa de dominio
│   ├── __init__.py
│   ├── models/                # Modelos de dominio (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── user_model.py
│   │   ├── role_model.py
│   │   ├── profile_models.py
│   │   └── clinical_models.py
│   └── schemas/               # Esquemas de validación (Pydantic)
│       ├── __init__.py
│       ├── auth_schemas.py
│       ├── user_schemas.py
│       └── clinical_schemas.py
├── application/               # Capa de aplicación
│   ├── __init__.py
│   ├── exceptions.py         # Excepciones personalizadas
│   ├── interfaces/           # Interfaces/Contratos
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   └── clinical_repository.py
│   └── services/             # Servicios de aplicación
│       ├── __init__.py
│       ├── auth_service.py
│       ├── user_service.py
│       └── clinical_service.py
├── infrastructure/           # Capa de infraestructura
│   ├── __init__.py
│   └── repositories/        # Implementaciones de repositorios
│       ├── __init__.py
│       ├── user_repository.py
│       └── clinical_repository.py
└── presentation/            # Capa de presentación
    ├── __init__.py
    └── api/                # Controladores de API
        ├── __init__.py
        └── v1/             # Versión 1 de la API
            ├── __init__.py
            ├── auth.py
            ├── admin.py
            ├── patients.py
            └── clinical.py
```

### Patrones de Diseño Utilizados

1. **Repository Pattern**: Abstrae el acceso a datos
2. **Dependency Injection**: Permite intercambiar implementaciones
3. **Clean Architecture**: Separación clara de responsabilidades
4. **Factory Pattern**: Para la creación de objetos complejos
5. **Strategy Pattern**: Para diferentes estrategias de autenticación

## 🛡️ Seguridad

### Autenticación JWT
- Tokens seguros con expiración configurable
- Refresh tokens para sesiones prolongadas
- Blacklist de tokens revocados

### Autorización Basada en Roles
- Permisos granulares por endpoint
- Middleware de autorización automático
- Validación de permisos por operación

### Protección de Datos
- Hash seguro de contraseñas con bcrypt
- Validación de entrada con Pydantic
- Sanitización de datos de salida

### CORS y Headers de Seguridad
- Configuración CORS restrictiva
- Headers de seguridad apropiados
- Rate limiting (configurable)

## 🚢 Despliegue en Render

### 1. Preparar la Aplicación

Crear `render.yaml`:

```yaml
services:
  - type: web
    name: odontolab-backend
    env: python
    buildCommand: pip install -r requirements.txt && python init_db.py
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: odontolab-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: ENVIRONMENT
        value: production

databases:
  - name: odontolab-db
    databaseName: odontolab
    user: odontolab
```

### 2. Variables de Entorno en Render

Configurar en el dashboard de Render:
- `SECRET_KEY`: Clave secreta para JWT (auto-generada)
- `DATABASE_URL`: URL de PostgreSQL (auto-configurada)
- `ENVIRONMENT`: production
- `CORS_ORIGINS`: URLs de tu frontend

### 3. Comandos de Despliegue

```bash
# Build Command
pip install -r requirements.txt && python init_db.py

# Start Command  
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
```

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_auth.py
pytest tests/test_users.py
pytest tests/test_patients.py

# Con cobertura
pytest --cov=app tests/
```

### Estructura de Tests

```
tests/
├── __init__.py
├── conftest.py              # Configuración global de tests
├── test_auth.py             # Tests de autenticación
├── test_admin.py            # Tests de funciones de admin
├── test_patients.py         # Tests de gestión de pacientes
├── test_clinical.py         # Tests de funciones clínicas
└── fixtures/               # Datos de prueba
    ├── users.py
    ├── patients.py
    └── clinical.py
```

## 📈 Monitoreo y Logging

### Logging
- Logs estructurados con información contextual
- Diferentes niveles de log por ambiente
- Rotación automática de archivos de log

### Métricas
- Tiempo de respuesta de endpoints
- Número de requests por minuto
- Errores por endpoint
- Uso de memoria y CPU

## 🔄 Flujo de Trabajo de la Aplicación

### 1. Flujo de Autenticación
1. Usuario envía credenciales a `/auth/login`
2. Sistema valida credenciales contra la base de datos
3. Si son válidas, genera JWT token
4. Cliente incluye token en header `Authorization: Bearer <token>`
5. Middleware valida token en cada request protegido

### 2. Flujo de Registro de Usuario (Admin)
1. Administrador accede a endpoints de gestión de usuarios
2. Crea usuario con rol específico (dentista/recepcionista)
3. Sistema crea usuario y perfil asociado
4. Notifica al nuevo usuario (email/SMS)

### 3. Flujo de Gestión de Pacientes (Recepcionista)
1. Recepcionista registra nuevo paciente
2. Sistema genera número único de paciente
3. Almacena información completa del paciente
4. Permite búsqueda y actualización posterior

### 4. Flujo de Intervención Clínica (Dentista)
1. Dentista selecciona paciente
2. Crea registro clínico para la visita
3. Registra intervenciones específicas
4. Sistema mantiene historial completo

## 🤝 Contribución

### Proceso de Desarrollo

1. Fork del repositorio
2. Crear rama para nueva funcionalidad: `git checkout -b feature/nueva-funcionalidad`
3. Realizar cambios y commits descriptivos
4. Ejecutar tests: `pytest`
5. Actualizar documentación si es necesario
6. Crear Pull Request

### Estándares de Código

- **PEP 8** para estilo de Python
- **Type hints** obligatorios
- **Docstrings** para todas las funciones públicas
- **Tests unitarios** para nueva funcionalidad
- **Nombres descriptivos** en inglés para código
- **Comentarios en español** para documentación

### Convenciones de Commit
```
feat: nueva funcionalidad
fix: corrección de bug
docs: actualización de documentación
test: agregar o modificar tests
refactor: refactorización de código
perf: mejora de rendimiento
```

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Soporte

Para soporte técnico o consultas:
- **Email**: support@odontolab.com
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Documentación**: [Wiki del Proyecto](https://github.com/your-repo/wiki)

## 📝 Changelog

### v1.0.0 (2024-01-XX)
- ✅ Sistema de autenticación JWT
- ✅ Gestión de usuarios por roles
- ✅ CRUD completo de pacientes
- ✅ Sistema de registros clínicos
- ✅ Gestión de intervenciones dentales
- ✅ API REST completa con documentación
- ✅ Despliegue listo para producción

### Próximas Funcionalidades
- 🔄 Sistema de citas
- 🔄 Notificaciones por email/SMS
- 🔄 Reportes y estadísticas
- 🔄 Integración con sistemas de pago
- 🔄 App móvil complementaria

---

**Desarrollado con ❤️ para la modernización de clínicas odontológicas**