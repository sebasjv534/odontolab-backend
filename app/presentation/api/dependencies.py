"""
API dependencies for authentication and authorization.

This module provides dependency functions for FastAPI endpoints.
"""

from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.domain.models import User, UserRole
from app.insfraestructure.repositories import UserRepository

settings = get_settings()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Convert to UUID
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_uuid)
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin role.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required"
        )
    return current_user


async def require_dentist(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require dentist role.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is not dentist
    """
    if current_user.role != UserRole.DENTIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dentist privileges required"
        )
    return current_user


async def require_receptionist(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require receptionist role.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is not receptionist
    """
    if current_user.role != UserRole.RECEPTIONIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Receptionist privileges required"
        )
    return current_user


async def require_admin_or_dentist(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin or dentist role.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is not admin or dentist
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.DENTIST]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator or Dentist privileges required"
        )
    return current_user


async def require_admin_or_receptionist(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin or receptionist role.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is not admin or receptionist
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.RECEPTIONIST]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator or Receptionist privileges required"
        )
    return current_user
