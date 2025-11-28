# 🔧 Solución Actualizada: Plan Gratuito de Render

## ❌ Problema Descubierto

El `preDeployCommand` **NO está disponible en el plan gratuito** de Render.

## ✅ Solución Implementada

Hemos movido la inicialización de la base de datos al **`buildCommand`**.

### Cambio en `render.yaml`:

**Antes (no funciona en plan gratuito):**
```yaml
buildCommand: pip install -r requirements.txt
preDeployCommand: python init_db_render.py  # ❌ Solo plan pagado
```

**Ahora (funciona en plan gratuito):**
```yaml
buildCommand: pip install -r requirements.txt && python init_db_render.py
# ✅ Se ejecuta durante el build
```

---

## 🚀 Cómo Funciona Ahora

1. **Build Phase**: 
   - `pip install -r requirements.txt` (instala dependencias)
   - `python init_db_render.py` (inicializa DB automáticamente)

2. **Start Phase**:
   - `gunicorn app.main:app ...` (inicia el servidor)

3. **Resultado**: Base de datos lista antes de que el servidor inicie ✅

---

## 📋 Qué Hacer Ahora

### Paso 1: Hacer Commit y Push

```bash
git add .
git commit -m "Fix: Move DB init to buildCommand for Render free tier"
git push origin main
```

### Paso 2: Render Redesplegará Automáticamente

Verás en los logs:

```
==> Building...
==> Running 'pip install -r requirements.txt && python init_db_render.py'
[logs de instalación de paquetes]

🚀 OdontoLab Database Initialization - Render Deployment
⏳ Waiting for database connection...
✓ Database connection established!
📋 Creating database tables...
✓ Tables created successfully!
👥 Creating default users...
✓ 3 users created successfully!
...
✅ Database initialized successfully!

==> Build succeeded 🎉

==> Deploying...
==> Running 'gunicorn app.main:app ...'
[2025-11-14 XX:XX:XX] [INFO] Application startup complete.
```

### Paso 3: Verificar

```bash
# Check de estado
curl https://odontolab-api.onrender.com/api/v1/check-init-status

# Debe responder:
{
  "initialized": true,
  "users_count": 3
}
```

---

## 🆘 Si el Build es Muy Lento

Si el build tarda mucho o falla por timeout:

### Opción A: Usar el Endpoint HTTP (Recomendado)

1. **Remover la inicialización del buildCommand temporalmente:**

   ```yaml
   buildCommand: pip install -r requirements.txt
   # Removido: && python init_db_render.py
   ```

2. **Después del despliegue, ejecutar manualmente:**

   Primero, configura en Render → Environment:
   ```
   INIT_DB_TOKEN=<generar-token-random-32-chars>
   ```

   Luego, desde tu terminal:
   ```bash
   curl -X POST https://odontolab-api.onrender.com/api/v1/init-database \
        -H "X-Init-Token: tu-token-secreto"
   ```

   O desde Swagger UI:
   - Ve a: https://odontolab-api.onrender.com/docs
   - Endpoint: `POST /api/v1/init-database`
   - Agrega header `X-Init-Token`

### Opción B: Inicialización Lazy (en el primer request)

Si prefieres que la DB se inicialice con el primer request en lugar del build.

---

## 🐛 Troubleshooting

### ❌ "Build timed out"

**Causa**: La conexión a la DB es muy lenta durante el build.

**Solución**: Usar el endpoint HTTP (Opción A arriba).

### ❌ "Worker was sent SIGTERM!"

**Causa**: Esto es normal. Render reinicia el worker después del health check.

**No es un error**: Si luego ves "Application startup complete", todo está bien.

### ❌ "Database connection failed during build"

**Causa**: La base de datos PostgreSQL aún no está lista cuando corre el build.

**Solución**: 

1. Espera 2-3 minutos después de crear la DB
2. O usa el endpoint HTTP para inicializar después

---

## ✅ Ventajas de Este Método

- ✅ **Compatible con plan gratuito**: No usa features de pago
- ✅ **Automático**: Se ejecuta en cada build
- ✅ **Idempotente**: No falla si ya está inicializado
- ✅ **Fallback disponible**: Endpoint HTTP si falla

---

## 🎯 Próximos Pasos

1. Hacer push (Paso 1 arriba)
2. Esperar el redespliegue
3. Verificar con `/api/v1/check-init-status`
4. Si no funcionó: Usar endpoint HTTP (Opción A)

---

## 📚 Endpoints Disponibles

### Verificar Estado (Público)
```bash
GET https://odontolab-api.onrender.com/api/v1/check-init-status
```

### Inicializar Manualmente (Protegido)
```bash
POST https://odontolab-api.onrender.com/api/v1/init-database
Header: X-Init-Token: <tu-token>
```

### Health Check
```bash
GET https://odontolab-api.onrender.com/health
```

### Swagger UI
```
https://odontolab-api.onrender.com/docs
```

---

## 🎉 ¡Listo!

Ahora la inicialización funciona en el plan gratuito moviendo el script al `buildCommand`.
