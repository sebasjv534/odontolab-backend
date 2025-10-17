"""
Authentication service for the odontology system.

This module provides authentication and authorization services,
including user login, token generation, and role-based access control.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.domain.models.user_model import User
from app.domain.models.role_model import RoleType
from app.domain.schemas.auth_schemas import TokenData, TokenResponse
from app.application.interfaces.user_repository import IUserRepository, IRoleRepository
from app.application.exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    UserNotFoundError,
    InactiveUserError
)


class AuthService:
    """
    Authentication service for handling user authentication and authorization.
    
    This service manages user login, token generation, password hashing,
    and role-based access control.
    """
    
    def __init__(
        self,
        user_repository: IUserRepository,
        role_repository: IRoleRepository
    ):
        """
        Initialize the authentication service.
        
        Args:
            user_repository (IUserRepository): User repository implementation
            role_repository (IRoleRepository): Role repository implementation
        """
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.settings = get_settings()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against its hash.
        
        Args:
            plain_password (str): Plain text password
            hashed_password (str): Hashed password from database
            
        Returns:
            bool: True if password is correct, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        Generate a hash for a plain password.
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Hashed password
        """
        return self.pwd_context.hash(password)
    
    async def authenticate_user(self, email: str, password: str) -> User:
        """
        Authenticate a user with email and password.
        
        Args:
            email (str): User's email address
            password (str): User's plain text password
            
        Returns:
            User: Authenticated user
            
        Raises:
            InvalidCredentialsError: If credentials are invalid
            UserNotFoundError: If user doesn't exist
            InactiveUserError: If user account is inactive
        """
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise UserNotFoundError("User not found")
        
        if not user.is_active:
            raise InactiveUserError("User account is inactive")
        
        if not self.verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid credentials")
        
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data (dict): Data to encode in the token
            expires_delta (timedelta, optional): Token expiration time
            
        Returns:
            str: JWT access token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.SECRET_KEY,
            algorithm=self.settings.ALGORITHM
        )
        return encoded_jwt
    
    def decode_token(self, token: str) -> TokenData:
        """
        Decode and validate a JWT token.
        
        Args:
            token (str): JWT token to decode
            
        Returns:
            TokenData: Decoded token data
            
        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.SECRET_KEY,
                algorithms=[self.settings.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            role: str = payload.get("role")
            
            if user_id is None or email is None:
                raise AuthenticationError("Invalid token payload")
            
            token_data = TokenData(
                user_id=UUID(user_id),
                email=email,
                role=role
            )
            return token_data
        except JWTError:
            raise AuthenticationError("Could not validate credentials")
    
    async def login(self, email: str, password: str) -> TokenResponse:
        """
        Login a user and return an access token.
        
        Args:
            email (str): User's email address
            password (str): User's plain text password
            
        Returns:
            Token: Access token response
            
        Raises:
            InvalidCredentialsError: If credentials are invalid
            UserNotFoundError: If user doesn't exist
            InactiveUserError: If user account is inactive
        """
        user = await self.authenticate_user(email, password)
        
        access_token_expires = timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.name if user.role else None
            },
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def get_current_user(self, token: str) -> User:
        """
        Get the current user from a JWT token.
        
        Args:
            token (str): JWT access token
            
        Returns:
            User: Current authenticated user
            
        Raises:
            AuthenticationError: If token is invalid
            UserNotFoundError: If user doesn't exist
        """
        token_data = self.decode_token(token)
        user = await self.user_repository.get_by_id(token_data.user_id)
        
        if user is None:
            raise UserNotFoundError("User not found")
        
        return user
    
    def check_role_permission(self, user: User, required_roles: list[RoleType]) -> bool:
        """
        Check if a user has one of the required roles.
        
        Args:
            user (User): User to check
            required_roles (list[RoleType]): List of allowed roles
            
        Returns:
            bool: True if user has required permission, False otherwise
        """
        if not user.role:
            return False
        
        return user.role.name in [role.value for role in required_roles]
    
    async def verify_admin_access(self, user: User) -> bool:
        """
        Verify if a user has administrator access.
        
        Args:
            user (User): User to verify
            
        Returns:
            bool: True if user is an administrator
        """
        return self.check_role_permission(user, [RoleType.ADMINISTRATOR])
    
    async def verify_dentist_access(self, user: User) -> bool:
        """
        Verify if a user has dentist access.
        
        Args:
            user (User): User to verify
            
        Returns:
            bool: True if user is a dentist
        """
        return self.check_role_permission(user, [RoleType.DENTIST])
    
    async def verify_receptionist_access(self, user: User) -> bool:
        """
        Verify if a user has receptionist access.
        
        Args:
            user (User): User to verify
            
        Returns:
            bool: True if user is a receptionist
        """
        return self.check_role_permission(user, [RoleType.RECEPTIONIST])