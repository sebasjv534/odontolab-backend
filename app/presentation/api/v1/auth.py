"""
Authentication endpoints for the OdontoLab system.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import get_settings
from app.domain.schemas.auth_schemas import Token, LoginResponse, UserMeResponse
from app.domain.models import User
from app.application.services import AuthService
from app.insfraestructure.repositories import UserRepository
from app.presentation.api.dependencies import get_current_user
from app.application.exceptions import AuthenticationError

settings = get_settings()
router = APIRouter()


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency to get authentication service."""
    user_repository = UserRepository(db)
    return AuthService(user_repository)


@router.post("/login", response_model=LoginResponse, summary="User login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """OAuth2 compatible token login."""
    try:
        result = await auth_service.login(form_data.username, form_data.password)
        return result
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.get("/me", response_model=UserMeResponse, summary="Get current user")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserMeResponse(
        id=current_user.id,
        nombre=current_user.nombre,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active
    )


@router.post("/refresh", response_model=Token, summary="Refresh access token")
async def refresh_token(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh the access token for current user."""
    try:
        token = await auth_service.create_user_token(current_user)
        return token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not refresh token"
        )


@router.post("/logout", summary="User logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout current user."""
    return {
        "success": True,
        "message": "Successfully logged out",
        "user_id": str(current_user.id)
    }
