# 🚀 Guía de Despliegue en Render (Plan Gratuito)

Esta guía te ayudará a desplegar OdontoLab Backend en Render utilizando el plan gratuito.

## 📋 Pre-requisitos

- Cuenta en [Render](https://render.com) (gratuita)
- Repositorio en GitHub con tu código
- Archivo `render.yaml` configurado (ya incluido)

---

## 🎯 Paso 1: Crear Cuenta en Render

1. Ve a [https://render.com](https://render.com)
2. Crea una cuenta (puedes usar GitHub para login rápido)
3. Verifica tu email

---

## 🗄️ Paso 2: Crear Base de Datos PostgreSQL

### Opción A: Usar render.yaml (Recomendado)

El archivo `render.yaml` ya está configurado para crear automáticamente la base de datos.

### Opción B: Crear Manualmente

1. En el Dashboard de Render, click en **"New +"**
2. Selecciona **"PostgreSQL"**
3. Configura:
   - **Name**: `odontolab-db`
   - **Database**: `odontolab`
   - **User**: `odontolab`
   - **Region**: Selecciona la más cercana (ej: Oregon)
   - **Plan**: **Free** (importante)
4. Click **"Create Database"**
5. **Espera** 2-3 minutos a que se cree

> ⚠️ **Nota**: La base de datos gratuita de Render:
>
> - Expira después de 90 días
> - 256 MB de almacenamiento
> - Conexiones limitadas
> - Suficiente para desarrollo y demos

---

## 🌐 Paso 3: Desplegar el Web Service

### Opción A: Usando render.yaml (Automático)

1. En Dashboard, click **"New +"** → **"Blueprint"**
2. Conecta tu repositorio de GitHub
3. Render detectará el `render.yaml`
4. Click **"Apply"**
5. Render creará automáticamente:
   - La base de datos PostgreSQL
   - El web service
   - Todas las variables de entorno

### Opción B: Manual

1. En Dashboard, click **"New +"** → **"Web Service"**
2. Conecta tu repositorio de GitHub
3. Configura:
   - **Name**: `odontolab-api`
   - **Region**: Misma que la base de datos
   - **Branch**: `main`
   - **Root Directory**: (dejar vacío)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**:
     ```bash
     gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 300 --log-level info
     ```
   - **Plan**: **Free**
4. Click **"Create Web Service"**

---

## ⚙️ Paso 4: Configurar Variables de Entorno

Si usaste render.yaml, las variables ya están configuradas. Si no:

1. En tu Web Service, ve a **"Environment"**
2. Agrega estas variables:

```bash
# Python
PYTHON_VERSION=3.11.9

# Database (copiar desde la base de datos PostgreSQL)
DATABASE_URL=postgresql://user:password@host/database

# JWT (generar un string aleatorio de 32+ caracteres)
SECRET_KEY=tu-clave-super-secreta-de-al-menos-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API
DEBUG=true
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:3000,https://tu-frontend.vercel.app

# Port (automático)
PORT=10000
```

### 🔑 Generar SECRET_KEY

Opción 1 - Python:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Opción 2 - Online:
```bash
https://randomkeygen.com/
```

### 📊 Obtener DATABASE_URL

1. Ve a tu base de datos PostgreSQL en Render
2. En la pestaña **"Info"**, busca **"Internal Database URL"**
3. Copia la URL completa
4. **IMPORTANTE**: Si la URL empieza con `postgres://`, cámbiala a `postgresql://`

---

## 🗃️ Paso 5: Inicializar la Base de Datos

Después del primer despliegue exitoso:

### Método 1: Desde el Shell de Render (Recomendado)

1. Ve a tu Web Service en Render
2. En el menú izquierdo, click **"Shell"**
3. Ejecuta:
   ```bash
   python init_db_render.py
   ```
4. Verifica que se ejecute sin errores

### Método 2: Manualmente con Python local

```bash
# Configurar DATABASE_URL en tu terminal
export DATABASE_URL="postgresql://..."

# Ejecutar script
python init_db_render.py
```

> 💡 **Tip**: El script `init_db_render.py` está optimizado para Render free tier con:
>
> - Timeouts largos (60 segundos)
> - Pool de conexiones pequeño (2 conexiones)
> - Manejo de errores mejorado
> - Verificación de datos existentes

---

## ✅ Paso 6: Verificar el Despliegue

### 1. Health Check

Visita: `https://tu-app.onrender.com/health`

Deberías ver:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "timestamp": "2024-11-13T..."
}
```

### 2. Documentación API

Visita: `https://tu-app.onrender.com/docs`

Deberías ver la interfaz de Swagger UI.

### 3. Probar Login

En Swagger UI:

1. Expande `POST /api/v1/auth/login`
2. Click **"Try it out"**
3. Usa estas credenciales:
   ```json
   {
     "username": "admin@odontolab.com",
     "password": "admin123"
   }
   ```
4. Deberías recibir un token JWT

---

## 🔄 Paso 7: Configurar Auto-Deploy

1. En tu Web Service, ve a **"Settings"**
2. En **"Build & Deploy"**, verifica que esté habilitado:
   - ✅ **Auto-Deploy**: Yes

Ahora cada push a `main` desplegará automáticamente.

---

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real

1. Ve a tu Web Service
2. Click en **"Logs"** (menú izquierdo)
3. Verás los logs del servidor

### Comandos útiles en el Shell

```bash
# Ver procesos
ps aux

# Ver uso de memoria
free -h

# Verificar conexión a DB
python -c "from app.core.config import get_settings; print(get_settings().DATABASE_URL)"

# Verificar tablas
python -c "from app.core.database import engine; import asyncio; asyncio.run(engine.connect())"
```

---

## 🐛 Solución de Problemas

### ❌ Error: "Application failed to respond"

**Causa**: Timeout durante el inicio

**Solución**:

1. Verifica que `DATABASE_URL` esté correcta
2. Aumenta el timeout en el start command: `--timeout 300`
3. Reduce workers a 1: `-w 1`

### ❌ Error: "Database connection failed"

**Causa**: DATABASE_URL incorrecta o DB no iniciada

**Solución**:

1. Verifica que la base de datos esté "Available" (no "Creating")
2. Copia nuevamente la DATABASE_URL desde Render
3. Asegúrate que empiece con `postgresql://` (no `postgres://`)

### ❌ Error: "Port already in use"

**Causa**: Variable PORT incorrecta

**Solución**:

- Asegúrate que el start command use `$PORT` (no hardcodeado)
- Render asigna automáticamente el puerto

### ❌ Error: "SECRET_KEY validation error"

**Causa**: SECRET_KEY muy corta

**Solución**:

- Genera una nueva de al menos 32 caracteres
- Ejemplo: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### ⚠️ El servicio se duerme (Render Free Tier)

**Comportamiento**: Después de 15 minutos de inactividad, el servicio se suspende.

**Solución temporal**:

- Primera petición tomará ~30 segundos (cold start)
- Para mantenerlo activo, usa un servicio de ping (ej: UptimeRobot)

**Solución permanente**:

- Upgrade a plan pagado ($7/mes)

### 🐌 La API es lenta

**Causa**: Plan gratuito tiene recursos limitados

**Optimizaciones aplicadas**:

- ✅ Solo 1 worker (`-w 1`)
- ✅ Timeout largo (300s)
- ✅ Pool pequeño de DB (2 conexiones)
- ✅ Sin pre-loading

---

## 🔐 Seguridad Post-Despliegue

### 1. Cambiar Contraseñas por Defecto

Desde Swagger UI o tu frontend:

```bash
# Login como admin
POST /api/v1/auth/login
{
  "username": "admin@odontolab.com",
  "password": "admin123"
}

# Cambiar password (próxima implementación)
PUT /api/v1/users/me/password
```

### 2. Configurar CORS

Actualiza `CORS_ORIGINS` con tu dominio de frontend:

```bash
CORS_ORIGINS=https://tu-frontend.vercel.app,https://odontolab.com
```

### 3. Rotar SECRET_KEY

Si sospechas que fue comprometida:

1. Genera una nueva
2. Actualiza en Render Environment
3. Todos los usuarios deberán hacer login nuevamente

---

## 📱 Conectar con Frontend

En tu frontend, usa esta URL base:

```typescript
// .env.production
VITE_API_URL=https://tu-app.onrender.com
NEXT_PUBLIC_API_URL=https://tu-app.onrender.com
```

Ejemplo de login:

```typescript
const response = await fetch('https://tu-app.onrender.com/api/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    username: 'admin@odontolab.com',
    password: 'admin123',
  }),
});

const data = await response.json();
console.log(data.access_token); // Token JWT
```

---

## 🎯 URLs Importantes

Después del despliegue:

- **API Base**: `https://[your-app].onrender.com`
- **Health Check**: `https://[your-app].onrender.com/health`
- **Swagger Docs**: `https://[your-app].onrender.com/docs`
- **ReDoc**: `https://[your-app].onrender.com/redoc`
- **OpenAPI JSON**: `https://[your-app].onrender.com/openapi.json`

---

## 📚 Recursos Adicionales

- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Render Community Forum](https://community.render.com/)

---

## 🆘 ¿Necesitas Ayuda?

Si encuentras problemas:

1. **Revisa los logs** en Render Dashboard
2. **Verifica variables** de entorno
3. **Prueba localmente** primero con Docker
4. **Consulta** la documentación de Render

---

## ✅ Checklist Final

Antes de dar por completado el despliegue:

- [ ] Base de datos PostgreSQL creada y disponible
- [ ] Web Service desplegado sin errores
- [ ] Variables de entorno configuradas
- [ ] Script `init_db_render.py` ejecutado exitosamente
- [ ] Health check responde correctamente
- [ ] Swagger UI accesible en `/docs`
- [ ] Login funciona con credenciales por defecto
- [ ] CORS configurado con dominio del frontend
- [ ] Contraseñas por defecto cambiadas (IMPORTANTE)

---

**¡Listo! 🎉** Tu backend está desplegado en Render.

Para actualizaciones futuras, simplemente haz push a GitHub y Render redesplegará automáticamente.
