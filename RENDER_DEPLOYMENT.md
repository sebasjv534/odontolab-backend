# Despliegue en Render - OdontoLab Backend

## 🚀 Configuración Actual en Render

### Variables de Entorno Configuradas

Asegúrate de tener estas variables configuradas en Render Dashboard:

```bash
# Base de Datos (PostgreSQL de Render)
DATABASE_URL=postgresql+asyncpg://...  # Auto-generada por Render

# JWT Configuration
SECRET_KEY=tu-clave-secreta-segura-de-32-caracteres-minimo
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API Configuration
DEBUG=true  # IMPORTANTE: Mantener en true para ver /docs
ENVIRONMENT=production

# CORS Origins (dominios del frontend)
CORS_ORIGINS=https://tu-frontend.vercel.app,https://odontolab-frontend.com
```

---

## 📚 Documentación Swagger Habilitada

Con la configuración actual, la documentación de Swagger está **siempre disponible** en:

- **Swagger UI**: `https://tu-app.onrender.com/docs`
- **ReDoc**: `https://tu-app.onrender.com/redoc`
- **OpenAPI JSON**: `https://tu-app.onrender.com/openapi.json`

**Nota**: La documentación está habilitada incluso en producción para facilitar las pruebas y el desarrollo del frontend.

---

## 🔧 Endpoints Disponibles

### Raíz y Salud

- `GET /` - Información general de la API
- `GET /health` - Health check

### Autenticación (`/api/v1/auth`)

- `POST /login` - Login OAuth2
- `GET /me` - Usuario actual
- `POST /refresh` - Refrescar token
- `POST /logout` - Cerrar sesión

### Usuarios (`/api/v1/users`) - Admin only

- `POST /` - Crear usuario
- `GET /` - Listar usuarios
- `GET /{user_id}` - Obtener usuario
- `PUT /{user_id}` - Actualizar usuario
- `PATCH /{user_id}/deactivate` - Desactivar usuario
- `DELETE /{user_id}` - Eliminar usuario

### Pacientes (`/api/v1/patients`)

- `POST /` - Crear paciente
- `GET /` - Listar pacientes
- `GET /search?q=term` - Buscar pacientes
- `GET /{patient_id}` - Obtener paciente
- `PUT /{patient_id}` - Actualizar paciente
- `DELETE /{patient_id}` - Eliminar paciente (Admin)

### Historias Clínicas (`/api/v1/medical-records`)

- `POST /` - Crear historia (Dentist only)
- `GET /` - Listar historias
- `GET /patient/{patient_id}` - Historias por paciente
- `GET /upcoming` - Citas próximas
- `GET /{record_id}` - Obtener historia
- `PUT /{record_id}` - Actualizar historia
- `DELETE /{record_id}` - Eliminar historia (Admin)

### Dashboard (`/api/v1/dashboard`)

- `GET /stats` - Estadísticas por rol
- `GET /admin` - Dashboard administrador
- `GET /dentist` - Dashboard dentista
- `GET /receptionist` - Dashboard recepcionista

### Contacto (`/api/v1/contact`)

- `POST /` - Crear solicitud (PÚBLICO - sin auth)
- `GET /` - Listar solicitudes
- `GET /pending` - Solicitudes pendientes
- `GET /{contact_id}` - Obtener solicitud
- `PATCH /{contact_id}/status` - Actualizar estado
- `DELETE /{contact_id}` - Eliminar solicitud

---

## 🔐 Usuarios por Defecto

Después de ejecutar `init_db.py` en el servidor, tendrás estos usuarios:

| Rol | Email | Password |
|-----|-------|----------|
| Administrador | <admin@odontolab.com> | admin123 |
| Dentista | <dentista@odontolab.com> | dentista123 |
| Recepcionista | <recepcion@odontolab.com> | recepcion123 |

**⚠️ IMPORTANTE**: Cambiar estas contraseñas después del primer despliegue.

---

## 🔄 Actualizar el Despliegue

Para actualizar el backend en Render:

1. Hacer push a GitHub:

   ```bash
   git add .
   git commit -m "Update backend"
   git push origin main
   ```

2. Render detectará automáticamente los cambios y redesplegará

3. Verificar el deploy en: <https://dashboard.render.com>

---

## ✅ Verificar Despliegue

Después de desplegar, verifica:

1. **Health Check**: `GET https://tu-app.onrender.com/health`
   - Debe responder: `{"status": "healthy", "version": "1.0.0", ...}`

2. **Documentación**: `https://tu-app.onrender.com/docs`
   - Debe mostrar Swagger UI

3. **Login**: `POST https://tu-app.onrender.com/api/v1/auth/login`
   - Probar con credenciales por defecto

---

## 🐛 Troubleshooting

### Problema: "No se puede acceder a /docs"

**Solución**: Verificar que `DEBUG=true` en variables de entorno de Render

### Problema: "Database connection error"

**Solución**:

- Verificar que DATABASE_URL está configurada correctamente
- Asegurarse que PostgreSQL está iniciado en Render
- Ejecutar `init_db.py` si es el primer despliegue

### Problema: "CORS error desde frontend"

**Solución**:

- Agregar el dominio del frontend a `CORS_ORIGINS`
- Formato: `https://frontend.vercel.app,https://otro-dominio.com`

### Problema: "Invalid JWT token"

**Solución**:

- Verificar que `SECRET_KEY` sea la misma en todos los ambientes
- Asegurarse que el token no ha expirado (60 minutos por defecto)

---

## 📊 Monitoreo

En Render Dashboard puedes ver:

- Logs en tiempo real
- Métricas de uso (CPU, memoria)
- Estado del servicio
- Historial de deploys

---

## 🔒 Seguridad

✅ **Implementado:**

- JWT Authentication
- Password hashing con bcrypt
- CORS configurado
- Rate limiting (TODO: implementar con slowapi)
- HTTPS automático por Render

⚠️ **Pendiente:**

- Cambiar contraseñas por defecto
- Implementar rate limiting
- Configurar logs centralizados
- Backups automáticos de BD

---

## 📝 Notas Adicionales

- **Logs**: Ver en Render Dashboard > Logs
- **Base de Datos**: PostgreSQL gestionada por Render
- **Escalado**: Ajustar en Render Dashboard si es necesario
- **Dominio Custom**: Configurar en Render Settings

---

## 🎯 URL del Despliegue

- **Backend API**: https://[tu-app-name].onrender.com
- **Documentación**: https://[tu-app-name].onrender.com/docs
- **Health Check**: https://[tu-app-name].onrender.com/health
