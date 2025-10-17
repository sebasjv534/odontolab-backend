"""
Authentication endpoints for the odontology system.

This module provides JWT-based authentication endpoints including login,
logout, and token refresh functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import create_access_token, verify_access_token
from app.domain.schemas.auth_schemas import (
    LoginRequest,
    TokenResponse,
    UserResponse,
    ChangePasswordRequest
)
from app.application.services.auth_service import AuthService
from app.insfraestructure.repositories.user_repository import UserRepository
from app.application.exceptions import AuthenticationError, ValidationError
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency to get authentication service."""
    user_repository = UserRepository(db)
    return AuthService(user_repository)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get current authenticated user from token."""
    try:
        user = await auth_service.get_current_user(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/login", response_model=TokenResponse, summary="User login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login with username/email and password to get access token.
    
    - **username**: User's email or username
    - **password**: User's password
    
    Returns JWT access token for authenticated requests.
    """
    try:
        # Create login request from form data
        login_request = LoginRequest(
            email=form_data.username,  # OAuth2PasswordRequestForm uses 'username' field
            password=form_data.password
        )
        
        # Authenticate user and get token
        token_response = await auth_service.authenticate_user(login_request)
        return token_response
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login-json", response_model=TokenResponse, summary="User login with JSON")
async def login_json(
    login_request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login with JSON payload containing email and password.
    
    Alternative login endpoint that accepts JSON instead of form data.
    """
    try:
        token_response = await auth_service.authenticate_user(login_request)
        return token_response
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse, summary="Get current user")
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header.
    """
    return UserResponse.model_validate(current_user)


@router.post("/change-password", summary="Change user password")
async def change_password(
    change_password_request: ChangePasswordRequest,
    current_user = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Change the current user's password.
    
    Requires current password for verification.
    """
    try:
        await auth_service.change_password(
            user_id=current_user.id,
            current_password=change_password_request.current_password,
            new_password=change_password_request.new_password
        )
        
        return {"message": "Password changed successfully"}
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh_token(
    current_user = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh the access token for current user.
    
    Requires valid JWT token. Returns new token with extended expiration.
    """
    try:
        # Generate new token for current user
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(current_user.id)},
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=str(current_user.id),
            role=current_user.role.name
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not refresh token"
        )


@router.post("/logout", summary="User logout")
async def logout(current_user = Depends(get_current_user)):
    """
    Logout current user.
    
    Note: With JWT tokens, logout is handled client-side by discarding the token.
    This endpoint is provided for consistency and potential future token blacklisting.
    """
    return {
        "message": "Successfully logged out",
        "user_id": str(current_user.id)
    }