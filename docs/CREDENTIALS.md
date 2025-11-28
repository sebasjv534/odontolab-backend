# Credenciales de Acceso - OdontoLab Backend

## URLs del Sistema

### Backend API

```
https://odontolab-backend.onrender.com
```

### Documentación Swagger

```
https://odontolab-backend.onrender.com/docs
```

### Documentación ReDoc

```
https://odontolab-backend.onrender.com/redoc
```

---

## Usuarios de Prueba

Una vez que la base de datos esté inicializada (después del primer deploy), tendrás estos usuarios:

###  Administrador

```
Email:    admin@odontolab.com
Password: admin123
Rol:      ADMIN
```

**Permisos:**

- Acceso completo a todos los módulos
- Gestión de usuarios (crear, editar, eliminar)
- Ver todos los pacientes e historias clínicas
- Dashboard completo del sistema
- Gestión de solicitudes de contacto

---

### Dentista

```
Email:    dentista@odontolab.com
Password: dentista123
Rol:      DENTIST
```

**Permisos:**

- Crear y editar historias clínicas propias
- Ver y gestionar pacientes
- Dashboard de dentista (estadísticas personales)
- Ver solicitudes de contacto
- No puede gestionar usuarios
- No puede eliminar registros

---

### Recepcionista

```
Email:    recepcion@odontolab.com
Password: recepcion123
Rol:      RECEPTIONIST
```

**Permisos:**

- Crear y gestionar pacientes propios
- Ver solicitudes de contacto
- Dashboard de recepcionista
- No puede crear historias clínicas
- No puede gestionar usuarios
- No puede eliminar registros

---

## Datos de Prueba Incluidos

### Pacientes (3)

1. **Carlos Rodríguez** - O+ - Sin alergias
2. **Laura Martínez** - A+ - Alérgica a Penicilina, Hipertensión
3. **Roberto Sánchez** - B+ - Sin condiciones

### Solicitudes de Contacto (2)

1. **Patricia López** - Consulta sobre ortodoncia
2. **Miguel Torres** - Información sobre implantes

---

## Próximos Pasos para Desplegar

### 1. Configurar Variables de Entorno en Render

Ve al Dashboard de Render → Tu servicio → Environment:

```bash
DATABASE_URL=postgresql+asyncpg://odontolab_user:AbBdsCGMPSY56GfV30scM8xas0oQDjup@dpg-d3opjmvdiees73c57tr0-a.oregon-postgres.render.com/odontolab_hxfc

SECRET_KEY=odontolab-super-secret-key-2025-production-jwt-token-signing

DEBUG=true

ENVIRONMENT=production

CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://tu-frontend.vercel.app
```

### 2. Hacer Commit y Push

```bash
git add .
git commit -m "Update configuration for free tier"
git push origin main
```

### 3. Esperar Deploy de Render

Render detectará los cambios y desplegará (2-3 minutos)
El servidor arrancará sin inicializar la BD primero

### 4. Inicializar Base de Datos MANUALMENTE desde Render Shell

Esto es necesario en el plan gratuito por los timeouts:

1. Ve a Render Dashboard → Tu servicio web
2. Click en "Shell" en el menú superior
3. Ejecuta uno de estos comandos:

```bash
# Opción 1: Con reintentos automáticos (recomendado)
python init_db_retry.py

# Opción 2: Script simple
python init_db.py
```

4. Espera a que termine (puede tardar 1-2 minutos)
5. Verás el mensaje: "✓ Database initialized successfully!"

### 5. Verificar el Deploy

Después de inicializar la BD:

```bash
# 1. Health Check
curl https://odontolab-backend.onrender.com/health

# 2. Probar Login
curl -X POST https://odontolab-backend.onrender.com/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@odontolab.com&password=admin123"

# 3. Abrir Swagger
https://odontolab-backend.onrender.com/docs
```

---

## Solución de Problemas

### Si el deploy falla

1. Ver logs en Render Dashboard → Logs
2. Verificar que DATABASE_URL esté configurada correctamente
3. Asegurarse que la base de datos PostgreSQL esté activa

### Si init_db.py falla

Puedes ejecutarlo manualmente desde Render Shell:

```bash
# En Render Dashboard → Shell
python init_db.py
```

### Si no puedes conectarte desde tu máquina local

La base de datos de Render solo acepta conexiones desde servicios de Render por defecto. Para conectarte desde afuera:

1. Ve a tu PostgreSQL en Render Dashboard
2. Ve a "Settings" → "Connections"
3. Habilita "External Connections"

---

## Conectar Frontend

Una vez verificado que el backend funciona, usa estas URLs en tu frontend:

```javascript
const API_BASE_URL = 'https://odontolab-backend.onrender.com';
const API_VERSION = '/api/v1';

// Endpoints
const AUTH_URL = `${API_BASE_URL}${API_VERSION}/auth`;
const USERS_URL = `${API_BASE_URL}${API_VERSION}/users`;
const PATIENTS_URL = `${API_BASE_URL}${API_VERSION}/patients`;
const MEDICAL_RECORDS_URL = `${API_BASE_URL}${API_VERSION}/medical-records`;
const DASHBOARD_URL = `${API_BASE_URL}${API_VERSION}/dashboard`;
const CONTACT_URL = `${API_BASE_URL}${API_VERSION}/contact`;
```

---

## Importante

CAMBIAR CONTRASEÑAS DESPUÉS DEL PRIMER LOGIN

Las contraseñas de prueba son conocidas públicamente. Después de verificar que todo funciona:

1. Login como admin
2. Ir a gestión de usuarios
3. Cambiar las contraseñas de todos los usuarios
4. O usar el endpoint:

   ```
   PUT /api/v1/users/{user_id}
   { "password": "nueva-contraseña-segura" }
   ```

---

## Soporte

- Documentación API: [FRONTEND_API_GUIDE.md](./FRONTEND_API_GUIDE.md)
- Implementación: [IMPLEMENTATION_COMPLETE.md](./IMPLEMENTATION_COMPLETE.md)
- Deploy: [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)

---

## Checklist Final

- [ ] Variables de entorno configuradas en Render
- [ ] Push realizado a GitHub
- [ ] Deploy completado exitosamente
- [ ] Base de datos inicializada (tablas creadas)
- [ ] Health check funciona
- [ ] Login con admin funciona
- [ ] Swagger accesible en /docs
- [ ] Frontend conectado y funcionando
- [ ] Contraseñas cambiadas (producción)

---

¡Tu backend está listo para usarse!
