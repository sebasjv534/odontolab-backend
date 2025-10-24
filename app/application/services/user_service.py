"""
User service for the OdontoLab system.

This module provides business logic for user management operations.
"""

from typing import Optional
from uuid import UUID

from app.domain.models import User, UserRole
from app.domain.schemas.user_schemas import UserCreate, UserUpdate
from app.insfraestructure.repositories import UserRepository
from app.application.exceptions import NotFoundError, ValidationError


class UserService:
    """Service for user management operations."""
    
    def __init__(self, user_repository: UserRepository):
        """Initialize the user service."""
        self.user_repository = user_repository
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user (Admin only)."""
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise ValidationError("Email already registered")
        
        user_dict = user_data.model_dump()
        user = await self.user_repository.create(user_dict)
        return user
    
    async def get_user_by_id(self, user_id: UUID) -> User:
        """Get user by ID."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user
    
    async def get_all_users(
        self,
        page: int = 1,
        per_page: int = 10,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> tuple[list[User], int]:
        """Get all users with pagination and filters."""
        skip = (page - 1) * per_page
        users, total = await self.user_repository.get_all(
            skip=skip,
            limit=per_page,
            role=role,
            is_active=is_active
        )
        return users, total
    
    async def get_users_by_role(self, role: UserRole) -> list[User]:
        """Get all users with a specific role."""
        return await self.user_repository.get_by_role(role)
    
    async def update_user(self, user_id: UUID, user_data: UserUpdate) -> User:
        """Update user information."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        if user_data.email and user_data.email != user.email:
            existing_user = await self.user_repository.get_by_email(user_data.email)
            if existing_user:
                raise ValidationError("Email already registered")
        
        user_dict = user_data.model_dump(exclude_unset=True)
        updated_user = await self.user_repository.update(user_id, user_dict)
        return updated_user
    
    async def deactivate_user(self, user_id: UUID) -> User:
        """Deactivate a user."""
        user = await self.user_repository.deactivate(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user (hard delete)."""
        success = await self.user_repository.delete(user_id)
        if not success:
            raise NotFoundError("User not found")
        return success
    
    async def count_users_by_role(self, role: UserRole) -> int:
        """Count users by role."""
        return await self.user_repository.count_by_role(role)
    
    async def count_active_users(self) -> int:
        """Count all active users."""
        return await self.user_repository.count_active_users()
