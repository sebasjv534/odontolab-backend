"""
User management endpoints for the OdontoLab system.

This module provides CRUD operations for user management (Admin only).
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.schemas.user_schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse
)
from app.domain.models import User, UserRole
from app.application.services import UserService
from app.insfraestructure.repositories import UserRepository
from app.presentation.api.dependencies import require_admin, get_current_user
from app.application.exceptions import NotFoundError, ValidationError

router = APIRouter()


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Dependency to get user service."""
    user_repository = UserRepository(db)
    return UserService(user_repository)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user"
)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin)
):
    """
    Create a new user (Admin only).
    
    Args:
        user_data: User creation data
        
    Returns:
        Created user information
    """
    try:
        user = await user_service.create_user(user_data)
        
        # Convert User model to UserResponse schema
        return UserResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the actual error for debugging
        import traceback
        print(f"Error creating user: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.get(
    "/",
    response_model=UserListResponse,
    summary="Get all users"
)
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin)
):
    """
    Get all users with pagination and filters (Admin only).
    
    Args:
        page: Page number
        per_page: Items per page
        role: Optional role filter
        is_active: Optional active status filter
        
    Returns:
        Paginated list of users
    """
    try:
        users, total = await user_service.get_all_users(
            page=page,
            per_page=per_page,
            role=role,
            is_active=is_active
        )
        
        # Calculate total pages
        total_pages = (total + per_page - 1) // per_page
        
        # Convert User models to UserResponse schemas
        user_responses = [
            UserResponse(
                id=str(user.id),
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role.value,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in users
        ]
        
        return UserListResponse(
            success=True,
            data=user_responses,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        # Log the actual error for debugging
        import traceback
        print(f"Error retrieving users: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID"
)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin)
):
    """
    Get user by ID (Admin only).
    
    Args:
        user_id: User ID
        
    Returns:
        User information
    """
    try:
        user = await user_service.get_user_by_id(user_id)
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        print(f"Error retrieving user: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}"
        )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user"
)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin)
):
    """
    Update user information (Admin only).
    
    Args:
        user_id: User ID
        user_data: User update data
        
    Returns:
        Updated user information
    """
    try:
        user = await user_service.update_user(user_id, user_data)
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        print(f"Error updating user: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.patch(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    summary="Deactivate user"
)
async def deactivate_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin)
):
    """
    Deactivate a user (Admin only).
    
    Args:
        user_id: User ID
        
    Returns:
        Updated user information
    """
    try:
        user = await user_service.deactivate_user(user_id)
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        print(f"Error deactivating user: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate user: {str(e)}"
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user"
)
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_admin)
):
    """
    Delete a user permanently (Admin only).
    
    Args:
        user_id: User ID
        
    Returns:
        No content
    """
    try:
        await user_service.delete_user(user_id)
        return None
        
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
