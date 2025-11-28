# 🔌 Guía de API para Frontend - OdontoLab

## 🌐 URL Base

```
Producción: https://odontolab-backend.onrender.com
```

## 📚 Documentación Interactiva

- **Swagger UI**: `https://odontolab-backend.onrender.com/docs`
- **ReDoc**: `https://odontolab-backend.onrender.com/redoc`

---

## 🔐 Autenticación

Todos los endpoints (excepto `/api/v1/contact` POST) requieren autenticación JWT.

### Headers Requeridos

```javascript
headers: {
  'Authorization': 'Bearer ' + accessToken,
  'Content-Type': 'application/json'
}
```

---

## 📋 Endpoints Disponibles

### 1. Autenticación (`/api/v1/auth`)

#### Login

```http
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@odontolab.com&password=admin123
```

**Respuesta:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "admin@odontolab.com",
    "full_name": "Administrador Principal",
    "role": "ADMIN",
    "is_active": true
  }
}
```

#### Obtener Usuario Actual

```http
GET /api/v1/auth/me
Authorization: Bearer {token}
```

#### Refrescar Token

```http
POST /api/v1/auth/refresh
Authorization: Bearer {token}
```

#### Logout

```http
POST /api/v1/auth/logout
Authorization: Bearer {token}
```

---

### 2. Usuarios (`/api/v1/users`) - 🔒 Solo Admin

#### Crear Usuario

```http
POST /api/v1/users
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "nuevo@odontolab.com",
  "password": "password123",
  "full_name": "Nombre Completo",
  "role": "DENTIST",
  "phone": "0987654321"
}
```

#### Listar Usuarios

```http
GET /api/v1/users?skip=0&limit=10
Authorization: Bearer {token}
```

#### Obtener Usuario

```http
GET /api/v1/users/{user_id}
Authorization: Bearer {token}
```

#### Actualizar Usuario

```http
PUT /api/v1/users/{user_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "Nombre Actualizado",
  "phone": "0999999999",
  "role": "RECEPTIONIST"
}
```

#### Desactivar Usuario

```http
PATCH /api/v1/users/{user_id}/deactivate
Authorization: Bearer {token}
```

#### Eliminar Usuario

```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer {token}
```

---

### 3. Pacientes (`/api/v1/patients`)

#### Crear Paciente

```http
POST /api/v1/patients
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "Juan Pérez",
  "email": "juan@email.com",
  "phone": "0987654321",
  "date_of_birth": "1990-01-15",
  "address": "Av. Principal 123",
  "blood_type": "O+",
  "allergies": ["Penicilina"],
  "emergency_contact_name": "María Pérez",
  "emergency_contact_phone": "0987654322"
}
```

#### Listar Pacientes

```http
GET /api/v1/patients?skip=0&limit=10
Authorization: Bearer {token}
```

#### Buscar Pacientes

```http
GET /api/v1/patients/search?q=juan
Authorization: Bearer {token}
```

#### Obtener Paciente

```http
GET /api/v1/patients/{patient_id}
Authorization: Bearer {token}
```

#### Actualizar Paciente

```http
PUT /api/v1/patients/{patient_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "Juan Pérez Actualizado",
  "phone": "0999999999"
}
```

#### Eliminar Paciente

```http
DELETE /api/v1/patients/{patient_id}
Authorization: Bearer {token}
```

🔒 Solo Admin

---

### 4. Historias Clínicas (`/api/v1/medical-records`)

#### Crear Historia Clínica

```http
POST /api/v1/medical-records
Authorization: Bearer {token}
Content-Type: application/json

{
  "patient_id": 1,
  "diagnosis": "Caries dental en molar superior",
  "treatment": "Limpieza y obturación",
  "treatment_date": "2025-10-23",
  "next_appointment": "2025-11-23T10:00:00",
  "notes": "Paciente con buena respuesta al tratamiento",
  "dental_chart": {
    "18": {"status": "healthy", "notes": ""},
    "17": {"status": "missing", "notes": "Extraído previamente"},
    "16": {"status": "cavity", "notes": "Requiere tratamiento"}
  },
  "prescriptions": ["Ibuprofeno 400mg cada 8 horas por 3 días"]
}
```

🔒 Solo Dentist

#### Listar Historias Clínicas

```http
GET /api/v1/medical-records?skip=0&limit=10
Authorization: Bearer {token}
```

#### Historias por Paciente

```http
GET /api/v1/medical-records/patient/{patient_id}
Authorization: Bearer {token}
```

#### Citas Próximas

```http
GET /api/v1/medical-records/upcoming
Authorization: Bearer {token}
```

#### Obtener Historia Clínica

```http
GET /api/v1/medical-records/{record_id}
Authorization: Bearer {token}
```

#### Actualizar Historia Clínica

```http
PUT /api/v1/medical-records/{record_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "diagnosis": "Diagnóstico actualizado",
  "notes": "Notas adicionales"
}
```

#### Eliminar Historia Clínica

```http
DELETE /api/v1/medical-records/{record_id}
Authorization: Bearer {token}
```

🔒 Solo Admin

---

### 5. Dashboard (`/api/v1/dashboard`)

#### Estadísticas Generales

```http
GET /api/v1/dashboard/stats
Authorization: Bearer {token}
```

**Respuesta:**

```json
{
  "total_patients": 150,
  "total_appointments": 45,
  "total_records": 320,
  "pending_contacts": 5
}
```

#### Dashboard Administrador

```http
GET /api/v1/dashboard/admin
Authorization: Bearer {token}
```

🔒 Solo Admin

**Respuesta:**

```json
{
  "total_users": 10,
  "active_users": 8,
  "total_patients": 150,
  "total_records": 320,
  "total_contacts": 25,
  "pending_contacts": 5,
  "users_by_role": {
    "ADMIN": 2,
    "DENTIST": 5,
    "RECEPTIONIST": 3
  }
}
```

#### Dashboard Dentista

```http
GET /api/v1/dashboard/dentist
Authorization: Bearer {token}
```

🔒 Solo Dentist

**Respuesta:**

```json
{
  "my_patients": 45,
  "my_records": 120,
  "upcoming_appointments": 8,
  "records_this_month": 15
}
```

#### Dashboard Recepcionista

```http
GET /api/v1/dashboard/receptionist
Authorization: Bearer {token}
```

🔒 Solo Receptionist

**Respuesta:**

```json
{
  "total_patients": 150,
  "my_patients": 50,
  "upcoming_appointments": 12,
  "pending_contacts": 5
}
```

---

### 6. Contacto (`/api/v1/contact`)

#### Crear Solicitud de Contacto

```http
POST /api/v1/contact
Content-Type: application/json

{
  "full_name": "Pedro García",
  "email": "pedro@email.com",
  "phone": "0987654321",
  "message": "Me gustaría agendar una cita para limpieza dental"
}
```

✅ **PÚBLICO - No requiere autenticación**

#### Listar Solicitudes

```http
GET /api/v1/contact?skip=0&limit=10
Authorization: Bearer {token}
```

#### Solicitudes Pendientes

```http
GET /api/v1/contact/pending
Authorization: Bearer {token}
```

#### Obtener Solicitud

```http
GET /api/v1/contact/{contact_id}
Authorization: Bearer {token}
```

#### Actualizar Estado

```http
PATCH /api/v1/contact/{contact_id}/status
Authorization: Bearer {token}
Content-Type: application/json

{
  "status": "CONTACTED"
}
```

**Estados disponibles:** `PENDING`, `CONTACTED`, `SCHEDULED`, `REJECTED`

#### Eliminar Solicitud

```http
DELETE /api/v1/contact/{contact_id}
Authorization: Bearer {token}
```

---

## 🎭 Roles y Permisos

### ADMIN (Administrador)

- ✅ Acceso completo a todos los endpoints
- ✅ Gestión de usuarios (CRUD)
- ✅ Eliminar pacientes e historias clínicas
- ✅ Ver dashboard completo

### DENTIST (Dentista)

- ✅ Crear y editar historias clínicas propias
- ✅ Ver y gestionar pacientes
- ✅ Ver dashboard de dentista
- ❌ No puede gestionar usuarios
- ❌ No puede eliminar registros

### RECEPTIONIST (Recepcionista)

- ✅ Crear y gestionar pacientes propios
- ✅ Ver solicitudes de contacto
- ✅ Ver dashboard de recepcionista
- ❌ No puede crear historias clínicas
- ❌ No puede gestionar usuarios

---

## 🔑 Usuarios de Prueba

Después de ejecutar `init_db.py`:

| Rol | Email | Password |
|-----|-------|----------|
| Admin | <admin@odontolab.com> | admin123 |
| Dentista | <dentista@odontolab.com> | dentista123 |
| Recepcionista | <recepcion@odontolab.com> | recepcion123 |

---

## 📦 Ejemplo de Flujo de Autenticación

```javascript
// 1. Login
const loginResponse = await fetch('https://tu-app.onrender.com/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    username: 'admin@odontolab.com',
    password: 'admin123'
  })
});

const { access_token, user } = await loginResponse.json();

// 2. Guardar token
localStorage.setItem('token', access_token);
localStorage.setItem('user', JSON.stringify(user));

// 3. Usar token en siguientes requests
const patientsResponse = await fetch('https://tu-app.onrender.com/api/v1/patients', {
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  }
});

const patients = await patientsResponse.json();
```

---

## 📦 Ejemplo de Creación de Paciente

```javascript
const createPatient = async (patientData) => {
  const token = localStorage.getItem('token');
  
  const response = await fetch('https://tu-app.onrender.com/api/v1/patients', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      full_name: patientData.fullName,
      email: patientData.email,
      phone: patientData.phone,
      date_of_birth: patientData.dateOfBirth,
      address: patientData.address,
      blood_type: patientData.bloodType,
      allergies: patientData.allergies || [],
      emergency_contact_name: patientData.emergencyName,
      emergency_contact_phone: patientData.emergencyPhone
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
};
```

---

## 📦 Ejemplo de Manejo de Errores

```javascript
const handleApiCall = async (apiCall) => {
  try {
    const response = await apiCall();
    
    if (response.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('token');
      window.location.href = '/login';
      return;
    }
    
    if (response.status === 403) {
      // Sin permisos
      alert('No tienes permisos para realizar esta acción');
      return;
    }
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Error en la petición');
    }
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};
```

---

## 🔄 Paginación

Todos los endpoints de listado soportan paginación:

```http
GET /api/v1/patients?skip=0&limit=10
GET /api/v1/users?skip=10&limit=10
GET /api/v1/medical-records?skip=20&limit=10
```

**Parámetros:**

- `skip`: Número de registros a saltar (default: 0)
- `limit`: Número de registros a retornar (default: 10, max: 100)

---

## 🔍 Búsqueda

El endpoint de búsqueda de pacientes:

```http
GET /api/v1/patients/search?q=juan
```

Busca en los siguientes campos:

- Nombre completo
- Email
- Teléfono
- Documento de identidad

---

## ⚠️ Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Petición exitosa |
| 201 | Created - Recurso creado exitosamente |
| 204 | No Content - Eliminación exitosa |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Token inválido o expirado |
| 403 | Forbidden - Sin permisos |
| 404 | Not Found - Recurso no encontrado |
| 409 | Conflict - Recurso duplicado |
| 422 | Unprocessable Entity - Error de validación |
| 500 | Internal Server Error - Error del servidor |

---

## 🚀 Listo para Conectar

**El backend ya está desplegado en Render** y listo para ser consumido por tu frontend.

### Checklist para tu agente de frontend

- [ ] Configurar URL base de la API
- [ ] Implementar flujo de login/logout
- [ ] Guardar token en localStorage/sessionStorage
- [ ] Implementar interceptor para agregar token a requests
- [ ] Manejar expiración de token (401)
- [ ] Implementar manejo de errores
- [ ] Crear servicios para cada módulo (users, patients, medical-records, dashboard, contact)
- [ ] Implementar guards de rutas por rol
- [ ] Mostrar UI según permisos del usuario

### Endpoints prioritarios para empezar

1. `/api/v1/auth/login` - Login
2. `/api/v1/auth/me` - Obtener usuario actual
3. `/api/v1/patients` - Listar pacientes
4. `/api/v1/dashboard/stats` - Dashboard básico
5. `/api/v1/contact` - Formulario público

---

## 📞 Soporte

- **Documentación completa**: `/docs` en tu servidor
- **Especificación OpenAPI**: `/openapi.json`
- **Repositorio**: <https://github.com/sebasjv534/odontolab-backend>
