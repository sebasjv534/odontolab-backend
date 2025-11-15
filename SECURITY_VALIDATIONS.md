# 🔒 Validaciones de Seguridad - OdontoLab API

## 📋 Gestión de Usuarios

### 🗑️ DELETE /api/v1/users/{user_id}

**Validaciones Implementadas:**

#### ✅ 1. Verificación de Existencia
- El usuario debe existir en la base de datos
- Error 404 si no se encuentra

#### ✅ 2. Prevención de Auto-Eliminación
```
❌ NO puedes eliminar tu propia cuenta
```
**Motivo**: Evita que un admin se elimine accidentalmente y pierda acceso al sistema.

**Error**:
```json
{
  "detail": "Cannot delete your own account. Ask another administrator to delete your account if needed."
}
```

#### ✅ 3. Protección del Último Admin
```
❌ NO puedes eliminar al último administrador activo
```
**Motivo**: El sistema DEBE tener al menos 1 admin activo para gestión.

**Error**:
```json
{
  "detail": "Cannot delete the last active administrator. The system must have at least one active admin. Create another administrator first, then delete this one."
}
```

#### ✅ 4. Respuesta Detallada
```json
{
  "success": true,
  "deleted_user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "full_name": "Juan Pérez",
    "role": "dentist"
  },
  "message": "User 'Juan Pérez' (dentist) deleted successfully",
  "deleted_by": "admin-uuid"
}
```

---

### 🔒 PATCH /api/v1/users/{user_id}/deactivate

**Validaciones Implementadas:**

#### ✅ 1. Verificación de Existencia
- El usuario debe existir en la base de datos
- Error 404 si no se encuentra

#### ✅ 2. Prevención de Auto-Desactivación
```
❌ NO puedes desactivar tu propia cuenta
```
**Motivo**: Evita que un admin se desactive accidentalmente.

**Error**:
```json
{
  "detail": "Cannot deactivate your own account. Ask another administrator to deactivate your account if needed."
}
```

#### ✅ 3. Protección del Último Admin Activo
```
❌ NO puedes desactivar al último administrador activo
```
**Motivo**: El sistema DEBE tener al menos 1 admin activo.

**Error**:
```json
{
  "detail": "Cannot deactivate the last active administrator. The system must have at least one active admin. Create another administrator first, then deactivate this one."
}
```

---

## 🔐 Recuperación de Admin (Setup)

### POST /api/v1/setup/register-admin

**Validaciones Implementadas:**

#### ✅ 1. Registro Solo Sin Admin Activo
```
✅ Permite registro si NO hay ningún admin activo
❌ Bloquea registro si YA hay un admin activo
```

**Casos de Uso**:
1. **Primera vez**: No hay usuarios → Permitir
2. **Emergencia**: Hay usuarios pero NO hay admin activo → Permitir
3. **Normal**: Ya hay admin activo → Bloquear

#### ✅ 2. Status Endpoint
```
GET /api/v1/setup/status
```

Responde con:
```json
{
  "initialized": true,
  "users_count": 5,
  "active_admins": 2,
  "can_register_admin": false,
  "message": "✅ Sistema inicializado correctamente"
}
```

O en caso de emergencia:
```json
{
  "initialized": true,
  "users_count": 3,
  "active_admins": 0,
  "can_register_admin": true,
  "message": "🚨 EMERGENCIA: Sistema sin administrador activo"
}
```

---

## 🛡️ Flujos de Seguridad

### Escenario 1: Eliminar un Dentista

```
✅ PERMITIDO (si eres admin y no eres tú mismo)

1. Admin A hace login
2. Admin A lista usuarios
3. Admin A ve dentista con ID: abc-123
4. Admin A: DELETE /users/abc-123
5. ✅ Dentista eliminado exitosamente
```

### Escenario 2: Intentar Eliminar al Último Admin

```
❌ BLOQUEADO

1. Admin A hace login (único admin activo)
2. Admin A intenta: DELETE /users/{su_propio_id}
3. ❌ Error 400: Cannot delete your own account

O:

1. Admin A hace login (único admin activo)
2. Admin B (otro admin) intenta: DELETE /users/{admin_A_id}
3. ❌ Error 400: Cannot delete the last active administrator
```

### Escenario 3: Proceso Seguro para Eliminar Admin

```
✅ CORRECTO

1. Admin A hace login
2. Admin A crea Admin B: POST /users (role: admin)
3. Ahora hay 2 admins activos
4. Admin B hace login
5. Admin B: DELETE /users/{admin_A_id}
6. ✅ Admin A eliminado exitosamente
```

### Escenario 4: Recuperación de Emergencia

```
✅ RECUPERACIÓN

1. Alguien eliminó al último admin por error
2. GET /setup/status → can_register_admin: true
3. POST /setup/register-admin con nuevos datos
4. ✅ Nuevo admin creado
5. Sistema recuperado
```

---

## 📊 Tabla de Validaciones

| Acción | Auto-acción | Último Admin | Usuario Existe | Resultado |
|--------|-------------|--------------|----------------|-----------|
| DELETE | ✅ Sí | N/A | ✅ Sí | ❌ Error: No puedes eliminarte |
| DELETE | ❌ No | ✅ Sí (es último) | ✅ Sí | ❌ Error: Es último admin |
| DELETE | ❌ No | ❌ No | ✅ Sí | ✅ Eliminado exitosamente |
| DELETE | ❌ No | ❌ No | ❌ No | ❌ Error: Usuario no encontrado |
| DEACTIVATE | ✅ Sí | N/A | ✅ Sí | ❌ Error: No puedes desactivarte |
| DEACTIVATE | ❌ No | ✅ Sí (es último) | ✅ Sí | ❌ Error: Es último admin activo |
| DEACTIVATE | ❌ No | ❌ No | ✅ Sí | ✅ Desactivado exitosamente |

---

## 🔧 Recomendaciones

### Para Desarrollo/Testing:

1. **Crea múltiples admins** antes de probar eliminaciones
2. **Usa DEACTIVATE** en lugar de DELETE (más seguro)
3. **Verifica el status** antes de eliminar: `GET /setup/status`
4. **Guarda las credenciales** del admin principal en lugar seguro

### Para Producción:

1. **NUNCA elimines usuarios** → Usa DEACTIVATE
2. **Mantén al menos 2 admins activos** (redundancia)
3. **Implementa roles de auditoría** para revisar eliminaciones
4. **Haz backups regulares** de la base de datos

### Mejores Prácticas:

```
✅ RECOMENDADO: PATCH /users/{id}/deactivate
❌ EVITAR: DELETE /users/{id}
```

**Motivo**: 
- Deactivate preserva datos y relaciones
- Delete es irreversible
- Deactivate permite reactivar si fue error

---

## 🚨 Logs de Auditoría

Cada eliminación registra:
```python
{
  "deleted_user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "Nombre Completo",
    "role": "dentist"
  },
  "deleted_by": "admin-uuid",
  "timestamp": "2025-11-15T12:00:00Z"
}
```

---

## 📞 Soporte

Si necesitas eliminar al último admin (emergencia):
1. Contacta al equipo de desarrollo
2. Acceso directo a la base de datos
3. O usa el endpoint `/setup/register-admin` si está habilitado

---

**Última actualización**: 15 de Noviembre de 2025
**Versión**: 1.0.0
