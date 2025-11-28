# 🚀 Resumen: Despliegue Rápido en Render

## ✅ Archivos Creados/Actualizados

1. **`render.yaml`** - Configuración automática para Render (actualizado)
2. **`init_db_render.py`** - Script optimizado para inicializar DB en Render
3. **`build.sh`** - Script de build para Render
4. **`RENDER_SETUP_GUIDE.md`** - Guía completa paso a paso
5. **`app/core/database.py`** - Optimizado para plan gratuito de Render
6. **`app/main.py`** - Health check mejorado con verificación de DB

---

## 🎯 Pasos Rápidos para Desplegar

### 1. Preparar el Repositorio

```bash
# Asegúrate de que todos los cambios estén en GitHub
git add .
git commit -m "Configure Render deployment with free tier optimizations"
git push origin main
```

### 2. Crear Servicios en Render

#### Opción A: Automático (Recomendado) ⭐

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Conecta tu repositorio GitHub
4. Render detectará `render.yaml` y creará:
   - ✅ Base de datos PostgreSQL (gratuita)
   - ✅ Web Service (gratuito)
   - ✅ Todas las variables de entorno

#### Opción B: Manual

**Paso 2.1 - Crear PostgreSQL:**

1. New + → PostgreSQL
2. Name: `odontolab-db`
3. Plan: **Free**
4. Click "Create Database"

**Paso 2.2 - Crear Web Service:**

1. New + → Web Service
2. Conecta tu repositorio
3. Configuración:
   - **Name**: `odontolab-api`
   - **Plan**: Free
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**:

     ```
     gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 300 --log-level info
     ```

**Paso 2.3 - Variables de Entorno:**

En el Web Service → Environment, agregar:

```bash
DATABASE_URL=<copiar-desde-postgresql-internal-url>
SECRET_KEY=<generar-string-random-32-chars>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEBUG=true
ENVIRONMENT=production
CORS_ORIGINS=http://localhost:3000
PYTHON_VERSION=3.11.9
```

🔑 **Generar SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Esperar el Despliegue

- ⏱️ Primer deploy: 5-10 minutos
- 📊 Ver progreso en "Logs"
- ✅ Cuando veas: "Application startup complete" → listo!

### 4. Inicializar Base de Datos

**Desde el Shell de Render:**

1. En tu Web Service → **"Shell"** (menú izquierdo)
2. Ejecutar:

   ```bash
   python init_db_render.py
   ```

3. Esperar a que termine (verás credenciales al final)

### 5. Verificar

Visita estas URLs (reemplaza `tu-app` con tu nombre real):

✅ **Health Check**: `https://tu-app.onrender.com/health`

```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

✅ **Docs**: `https://tu-app.onrender.com/docs`

✅ **Login**: En Swagger UI, prueba:

```json
{
  "username": "admin@odontolab.com",
  "password": "admin123"
}
```

---

## 🔑 Credenciales por Defecto

| Rol | Email | Password |
|-----|-------|----------|
| Admin | `admin@odontolab.com` | `admin123` |
| Dentista | `dentista@odontolab.com` | `dentista123` |
| Recepcionista | `recepcion@odontolab.com` | `recepcion123` |

⚠️ **CAMBIAR ESTAS CONTRASEÑAS** después del primer deploy!

---

## 🎨 Conectar con Frontend

En tu frontend (.env):

```bash
# Next.js
NEXT_PUBLIC_API_URL=https://tu-app.onrender.com

# Vite/React
VITE_API_URL=https://tu-app.onrender.com
```

Ejemplo de llamada:

```typescript
const response = await fetch(
  `${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/login`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      username: 'admin@odontolab.com',
      password: 'admin123',
    }),
  }
);
```

Actualizar CORS:

```bash
# En Render → Environment
CORS_ORIGINS=https://tu-frontend.vercel.app,https://otro-dominio.com
```

---

## ⚠️ Limitaciones Plan Gratuito

- 🕐 **Sleep después de 15 min** de inactividad
  - Primera request tras sleep: ~30 segundos
  - Solución: Usar servicio de ping (UptimeRobot)

- 💾 **PostgreSQL**:
  - 256 MB de almacenamiento
  - Expira en 90 días
  - Suficiente para desarrollo/demos

- ⚡ **Rendimiento**:
  - 512 MB RAM
  - 0.1 CPU
  - 1 worker (configurado en start command)

---

## 🐛 Problemas Comunes

### ❌ "Application failed to respond"

```bash
# Solución: Verificar DATABASE_URL
# En Render Shell:
echo $DATABASE_URL

# Debe empezar con: postgresql:// o postgresql+asyncpg://
```

### ❌ "Database connection error"

```bash
# Esperar a que la DB esté "Available" (no "Creating")
# Ver en: Dashboard → odontolab-db → Status
```

### ❌ Primera petición muy lenta

```
Es normal en plan gratuito (cold start)
Toma ~30 segundos después de inactividad
```

---

## 🔄 Actualizar el Deployment

Simplemente haz push a GitHub:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render redesplegará automáticamente en ~3-5 minutos.

---

## 📚 Documentación Completa

Ver `RENDER_SETUP_GUIDE.md` para:

- Troubleshooting detallado
- Configuración avanzada
- Seguridad post-deployment
- Monitoreo y logs

---

## ✅ Checklist Final

- [ ] Repositorio en GitHub actualizado
- [ ] Servicios creados en Render (DB + Web)
- [ ] Variables de entorno configuradas
- [ ] Primer deploy completado exitosamente
- [ ] `init_db_render.py` ejecutado sin errores
- [ ] Health check responde `"database": "connected"`
- [ ] Swagger UI accesible en `/docs`
- [ ] Login funciona con credenciales por defecto
- [ ] CORS configurado con dominio del frontend
- [ ] Frontend puede conectarse exitosamente

---

**¡Listo! 🎉** Tu API está en producción en Render.

**URLs importantes:**

- 🌐 API: `https://[tu-app].onrender.com`
- 📖 Docs: `https://[tu-app].onrender.com/docs`
- 💚 Health: `https://[tu-app].onrender.com/health`

Para soporte: Ver logs en Render Dashboard → Logs
