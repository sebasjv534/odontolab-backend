class AppError(Exception):
    """Excepción base de la aplicación."""
    def __init__(self, message: str, code: str = "app_error"):
        super().__init__(message)
        self.code = code
        self.message = message

class NotFoundError(AppError):
    """Recurso no encontrado (404)."""
    def __init__(self, message="Not found"):
        super().__init__(message, code="not_found")

class ConflictError(AppError):
    """Conflicto (409)."""
    def __init__(self, message="Conflict"):
        super().__init__(message, code="conflict")

class ValidationError(AppError):
    """Error de validación (400)."""
    def __init__(self, message="Validation error"):
        super().__init__(message, code="validation_error")

class AuthenticationError(AppError):
    """Error de autenticación (401)."""
    def __init__(self, message="Invalid credentials"):
        super().__init__(message, code="auth_error")

class UserNotFoundError(NotFoundError):
    """Usuario no encontrado."""
    def __init__(self, message="User not found"):
        super().__init__(message)

class PatientNotFoundError(NotFoundError):
    """Paciente no encontrado."""
    def __init__(self, message="Patient not found"):
        super().__init__(message)

class ClinicalRecordNotFoundError(NotFoundError):
    """Registro clínico no encontrado."""
    def __init__(self, message="Clinical record not found"):
        super().__init__(message)

class InterventionNotFoundError(NotFoundError):
    """Intervención no encontrada."""
    def __init__(self, message="Intervention not found"):
        super().__init__(message)

class RoleNotFoundError(NotFoundError):
    """Rol no encontrado."""
    def __init__(self, message="Role not found"):
        super().__init__(message)

class InvalidCredentialsError(AuthenticationError):
    """Credenciales inválidas."""
    def __init__(self, message="Invalid credentials"):
        super().__init__(message)

class InactiveUserError(AuthenticationError):
    """Usuario inactivo."""
    def __init__(self, message="User account is inactive"):
        super().__init__(message)

class UserAlreadyExistsError(ConflictError):
    """Usuario ya existe."""
    def __init__(self, message="User already exists"):
        super().__init__(message)

class PatientAlreadyExistsError(ConflictError):
    """Paciente ya existe."""
    def __init__(self, message="Patient already exists"):
        super().__init__(message)

class AuthorizationError(AppError):
    """Error de autorización (403)."""
    def __init__(self, message="Insufficient permissions"):
        super().__init__(message, code="authorization_error")

class DatabaseError(AppError):
    """Error de base de datos."""
    def __init__(self, message="Database error"):
        super().__init__(message, code="database_error")

class BusinessLogicError(AppError):
    """Error de lógica de negocio."""
    def __init__(self, message="Business logic error"):
        super().__init__(message, code="business_logic_error")

class AppointmentNotFoundError(NotFoundError):
    """Appointment not found."""
    def __init__(self, message="Appointment not found"):
        super().__init__(message)

class AppointmentConflictError(ConflictError):
    """Appointment scheduling conflict."""
    def __init__(self, message="Appointment scheduling conflict"):
        super().__init__(message)

# Alias for compatibility
PermissionError = AuthorizationError
