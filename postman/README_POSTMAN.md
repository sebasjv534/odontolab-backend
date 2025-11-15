# 📮 Guía de Postman para OdontoLab API

## 🎯 ¿Qué incluye esta colección?

He creado una colección **completa y automatizada** de Postman con:

- ✅ **50+ requests** organizados por módulos
- ✅ **Autenticación automática** con JWT
- ✅ **Variables dinámicas** (IDs se guardan automáticamente)
- ✅ **Scripts de prueba** que guardan tokens y datos
- ✅ **Documentación detallada** en cada endpoint
- ✅ **Ambiente pre-configurado** con tu API en Render

---

## 📦 Archivos Incluidos

1. **`OdontoLab_API.postman_collection.json`** - Colección completa
2. **`OdontoLab_Environment.postman_environment.json`** - Ambiente de producción
3. **`README_POSTMAN.md`** - Esta guía

---

## 🚀 Paso 1: Importar en Postman

### Opción A: Importar Archivos JSON

1. **Abre Postman**
2. Click en **"Import"** (esquina superior izquierda)
3. **Arrastra los 2 archivos JSON** o click "Upload Files":
   - `OdontoLab_API.postman_collection.json`
   - `OdontoLab_Environment.postman_environment.json`
4. Click **"Import"**

### Opción B: Desde GitHub (si subes los archivos)

1. En Postman, click **"Import"**
2. Tab **"Link"**
3. Pega la URL raw de GitHub del JSON
4. Click **"Continue"** → **"Import"**

---

## ⚙️ Paso 2: Configurar el Ambiente

1. En Postman, esquina **superior derecha**
2. Selecciona **"OdontoLab - Production"** en el dropdown
3. Click en el ícono de **ojo** 👁️ para ver las variables
4. Verifica que `BASE_URL` sea: `https://odontolab-api.onrender.com`

---

## 🧪 Paso 3: Ejecutar las Pruebas (Orden Recomendado)

### 📋 Secuencia de Pruebas Básica

#### 1️⃣ **Setup & Health**

```
1. Health Check ✅
   → Verifica que la API esté funcionando

2. Check Setup Status ✅
   → Verifica si ya hay usuarios registrados

3. Register First Admin (opcional)
   → Solo si necesitas crear el admin nuevamente
```

#### 2️⃣ **Authentication**

```
1. Login (Admin) ✅ ← IMPORTANTE
   → Obtiene el token JWT
   → El token se guarda AUTOMÁTICAMENTE en ACCESS_TOKEN

2. Get Current User (Me) ✅
   → Verifica que el token funcione
   → Muestra tu información de usuario
```

#### 3️⃣ **Users (Admin Only)**

```
1. Create User (Dentist) ✅
   → Crea un dentista
   → El ID se guarda automáticamente en DENTIST_ID

2. Create User (Receptionist) ✅
   → Crea una recepcionista
   → El ID se guarda automáticamente

3. List All Users ✅
   → Muestra todos los usuarios del sistema

4. Get User by ID ✅
   → Obtiene el dentista creado

5. Update User (opcional)
   → Actualiza información del dentista

6. Deactivate User (opcional)
   → Desactiva temporalmente un usuario

7. Delete User (opcional)
   → Elimina permanentemente (¡cuidado!)
```

#### 4️⃣ **Patients**

```
1. Create Patient ✅
   → Crea un paciente
   → El ID se guarda automáticamente en PATIENT_ID

2. List All Patients ✅
   → Muestra todos los pacientes

3. Search Patients ✅
   → Busca por nombre: "Carlos"

4. Get Patient by ID ✅
   → Obtiene el paciente creado

5. Update Patient (opcional)
   → Actualiza información del paciente

6. Delete Patient (opcional)
   → Elimina el paciente (solo admin)
```

#### 5️⃣ **Medical Records**

```
1. Create Medical Record ✅
   → Crea una historia clínica para el paciente
   → Requiere PATIENT_ID (ya guardado)
   → El ID se guarda en MEDICAL_RECORD_ID

2. List All Medical Records ✅
   → Muestra todas las historias

3. Get Medical Records by Patient ✅
   → Historias del paciente específico

4. Get Upcoming Appointments ✅
   → Próximas citas programadas

5. Get Medical Record by ID ✅
   → Historia específica

6. Update Medical Record (opcional)
   → Actualiza la historia clínica

7. Delete Medical Record (opcional)
   → Elimina la historia (solo admin)
```

#### 6️⃣ **Dashboard**

```
1. Get Dashboard Stats ✅
   → Estadísticas generales según tu rol

2. Get Admin Dashboard ✅
   → Vista completa del admin

3. Get Dentist Dashboard ✅
   → Vista del dentista (requiere login como dentista)

4. Get Receptionist Dashboard ✅
   → Vista de recepcionista
```

#### 7️⃣ **Contact (Public)**

```
1. Create Contact Request ✅
   → NO REQUIERE AUTH (público)
   → Simula una solicitud desde el sitio web

2. List Contact Requests ✅
   → Ver todas las solicitudes

3. Get Pending Contact Requests ✅
   → Solo las pendientes de atención
```

---

## 🤖 Características Automáticas

### 1. **Token JWT se Guarda Automáticamente**

Cuando haces login, el token se guarda automáticamente en `ACCESS_TOKEN`. Todos los demás requests lo usan automáticamente.

**Script en Login:**
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set('ACCESS_TOKEN', response.access_token);
    console.log('✅ Login exitoso. Token guardado.');
}
```

### 2. **IDs se Guardan Automáticamente**

Cuando creas un usuario, paciente o historia clínica, el ID se guarda automáticamente.

**Ejemplo en Create Patient:**
```javascript
if (pm.response.code === 201) {
    const response = pm.response.json();
    pm.environment.set('PATIENT_ID', response.id);
    console.log('✅ Paciente creado:', response.full_name);
}
```

### 3. **Variables Dinámicas**

Los endpoints usan variables automáticamente:
- `{{BASE_URL}}` → URL de tu API
- `{{ACCESS_TOKEN}}` → Token JWT actual
- `{{PATIENT_ID}}` → ID del último paciente creado
- `{{DENTIST_ID}}` → ID del último dentista creado
- etc.

---

## 🎯 Flujo de Prueba Completo (5 minutos)

### **Ejecución Rápida:**

```
1. Health Check
   ↓
2. Login (Admin)
   ↓ (token guardado automáticamente)
3. Create User (Dentist)
   ↓ (DENTIST_ID guardado)
4. Create User (Receptionist)
   ↓ (RECEPTIONIST_ID guardado)
5. Create Patient
   ↓ (PATIENT_ID guardado)
6. Create Medical Record
   ↓ (usa PATIENT_ID automáticamente)
7. Get Dashboard Stats
   ↓
8. List All Patients
   ↓
✅ ¡Listo! API completamente probada
```

---

## 📊 Ver Resultados

### Console de Postman

Los scripts imprimen logs útiles:

```
✅ Login exitoso. Token guardado.
Token expira en: 60 minutos

✅ Dentista creado: dentista@odontolab.com

✅ Paciente creado: Carlos Rodríguez

✅ Historia clínica creada: 123e4567-e89b-12d3-a456-426614174000
```

Para ver: **View → Show Postman Console** (Ctrl+Alt+C)

### Variables de Entorno

Para ver los valores guardados:
1. Click en el **ojo** 👁️ (esquina superior derecha)
2. Verás todas las variables y sus valores actuales

---

## 🔄 Probar con Diferentes Roles

### Como Dentista:

1. Primero crea el dentista (ya hecho arriba)
2. Haz logout del admin
3. En **Login**, cambia:
   ```
   username: {{DENTIST_EMAIL}}
   password: dentista123
   ```
4. Ahora puedes:
   - ✅ Crear historias clínicas
   - ✅ Ver pacientes
   - ❌ NO crear usuarios (solo admin)

### Como Recepcionista:

1. Haz logout
2. En **Login**, cambia:
   ```
   username: {{RECEPTIONIST_EMAIL}}
   password: recepcion123
   ```
3. Ahora puedes:
   - ✅ Crear pacientes
   - ✅ Ver historias clínicas
   - ❌ NO crear historias (solo dentistas)

---

## 🎨 Organización de la Colección

La colección está organizada en **7 carpetas**:

```
📁 OdontoLab API
├── 📂 1. Setup & Health (3 requests)
├── 📂 2. Authentication (3 requests)
├── 📂 3. Users (7 requests)
├── 📂 4. Patients (6 requests)
├── 📂 5. Medical Records (8 requests)
├── 📂 6. Dashboard (4 requests)
└── 📂 7. Contact (3 requests)
```

---

## 🔧 Personalizar para Ambiente Local

Si quieres probar localmente:

1. Crea un nuevo ambiente: **"OdontoLab - Local"**
2. Cambia `BASE_URL` a: `http://localhost:8000`
3. Selecciona este ambiente
4. Ejecuta las pruebas normalmente

---

## 📝 Ejemplos de Uso

### Ejemplo 1: Crear un Paciente Completo

```json
POST {{BASE_URL}}/api/v1/patients
Authorization: Bearer {{ACCESS_TOKEN}}

{
  "first_name": "Carlos",
  "last_name": "Rodríguez",
  "email": "carlos@example.com",
  "phone": "0987654321",
  "date_of_birth": "1985-03-15",
  "address": "Calle Principal 123",
  "blood_type": "O+",
  "allergies": ["Penicilina"],
  "medical_conditions": ["Diabetes tipo 2"],
  "emergency_contact_name": "Ana Rodríguez",
  "emergency_contact_phone": "0987654322"
}
```

### Ejemplo 2: Búsqueda de Pacientes

```
GET {{BASE_URL}}/api/v1/patients/search?q=Carlos
Authorization: Bearer {{ACCESS_TOKEN}}
```

### Ejemplo 3: Dashboard de Admin

```
GET {{BASE_URL}}/api/v1/dashboard/admin
Authorization: Bearer {{ACCESS_TOKEN}}
```

---

## ✅ Checklist de Verificación

Después de ejecutar las pruebas, verifica:

- [ ] Health check responde "healthy"
- [ ] Login obtiene token JWT
- [ ] Token se guarda automáticamente
- [ ] Puedes crear usuarios (dentista, recepcionista)
- [ ] Puedes crear pacientes
- [ ] Puedes crear historias clínicas
- [ ] Dashboard muestra estadísticas
- [ ] Búsqueda de pacientes funciona
- [ ] Próximas citas se listan correctamente
- [ ] Endpoint de contacto público funciona sin auth

---

## 🐛 Troubleshooting

### ❌ Error: "Unauthorized"

**Solución**:
1. Verifica que hiciste login primero
2. Verifica que el token esté en `ACCESS_TOKEN` (ojo 👁️)
3. El token expira en 60 minutos → haz login nuevamente

### ❌ Error: "Variable PATIENT_ID is not defined"

**Solución**:
1. Primero ejecuta "Create Patient"
2. El ID se guardará automáticamente
3. Luego ejecuta los endpoints que usan ese ID

### ❌ Error: "Forbidden - Insufficient permissions"

**Solución**:
- Verifica tu rol actual (GET /auth/me)
- Algunos endpoints son solo para admin
- Otros solo para dentistas

---

## 🎯 Próximos Pasos

1. **Ejecuta la secuencia básica** (pasos 1-8 arriba)
2. **Explora cada carpeta** de la colección
3. **Modifica los datos** según tus necesidades
4. **Crea tus propios tests** en la pestaña "Tests"
5. **Exporta resultados** para documentación

---

## 📚 Recursos Adicionales

- **Swagger UI**: https://odontolab-api.onrender.com/docs
- **ReDoc**: https://odontolab-api.onrender.com/redoc
- **Postman Learning Center**: https://learning.postman.com

---

## 🎉 ¡Listo!

Ahora tienes una colección **completa y profesional** de Postman para probar toda tu API.

**Características principales:**
- ✅ 50+ requests organizados
- ✅ Autenticación automática
- ✅ Variables dinámicas
- ✅ Scripts de prueba
- ✅ Documentación completa
- ✅ Flujos de trabajo optimizados

**Siguiente paso**: Importa la colección y empieza a probar. 🚀
