"""
Authentication service for the OdontoLab system.
"""

from datetime import timedelta
from typing import Optional
from uuid import UUID

from app.domain.models import User, UserRole
from app.domain.schemas.auth_schemas import Token, LoginResponse, UserMeResponse
from app.insfraestructure.repositories import UserRepository
from app.application.exceptions import AuthenticationError, AuthorizationError
from app.core.security import verify_password, create_access_token
from app.core.config import get_settings

settings = get_settings()


class AuthService:
    """Authentication service for handling user authentication and authorization."""
    
    def __init__(self, user_repository: UserRepository):
        """Initialize the authentication service."""
        self.user_repository = user_repository
    
    async def authenticate_user(self, email: str, password: str) -> User:
        """Authenticate a user with email and password."""
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        if not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        
        if not user.is_active:
            raise AuthenticationError("User account is inactive")
        
        return user
    
    async def create_user_token(self, user: User) -> Token:
        """Create a JWT access token for a user."""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value
            },
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer"
        )
    
    async def login(self, email: str, password: str) -> LoginResponse:
        """Login a user and return token with user information."""
        user = await self.authenticate_user(email, password)
        token = await self.create_user_token(user)
        
        return LoginResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            user={
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat()
            }
        )
    
    async def require_admin(self, user: User) -> bool:
        """Check if user has admin role."""
        if user.role != UserRole.ADMIN:
            raise AuthorizationError("Administrator privileges required")
        return True
    
    async def require_dentist(self, user: User) -> bool:
        """Check if user has dentist role."""
        if user.role != UserRole.DENTIST:
            raise AuthorizationError("Dentist privileges required")
        return True
    
    async def require_receptionist(self, user: User) -> bool:
        """Check if user has receptionist role."""
        if user.role != UserRole.RECEPTIONIST:
            raise AuthorizationError("Receptionist privileges required")
        return True
