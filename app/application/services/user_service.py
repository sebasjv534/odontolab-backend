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
    
    async def deactivate_user(self, user_id: UUID, current_user: Optional[User] = None) -> User:
        """
        Deactivate a user (soft delete).
        
        Args:
            user_id: ID of user to deactivate
            current_user: Current authenticated user
            
        Returns:
            Deactivated user
            
        Raises:
            NotFoundError: User not found
            ValidationError: Cannot deactivate (last admin, self-deactivation)
        """
        # 1. Verificar que el usuario exista
        user_to_deactivate = await self.user_repository.get_by_id(user_id)
        if not user_to_deactivate:
            raise NotFoundError(f"User with ID {user_id} not found")
        
        # 2. VALIDACIÓN: No permitir auto-desactivación
        if current_user and current_user.id == user_id:
            raise ValidationError(
                "Cannot deactivate your own account. "
                "Ask another administrator to deactivate your account if needed."
            )
        
        # 3. VALIDACIÓN: Si es admin, verificar que no sea el último activo
        if user_to_deactivate.role == UserRole.ADMIN and user_to_deactivate.is_active:
            active_admins = await self.user_repository.get_by_role(UserRole.ADMIN)
            active_count = sum(1 for admin in active_admins if admin.is_active)
            
            if active_count <= 1:
                raise ValidationError(
                    "Cannot deactivate the last active administrator. "
                    "The system must have at least one active admin. "
                    "Create another administrator first, then deactivate this one."
                )
        
        # 4. Desactivar el usuario
        user = await self.user_repository.deactivate(user_id)
        if not user:
            raise NotFoundError("User not found")
        return user
    
    async def delete_user(self, user_id: UUID, current_user: Optional[User] = None) -> dict:
        """
        Delete a user (hard delete) with safety validations.
        
        Args:
            user_id: ID of user to delete
            current_user: Current authenticated user (to prevent self-deletion)
            
        Returns:
            dict with deletion details
            
        Raises:
            NotFoundError: User not found
            ValidationError: Cannot delete (last admin, self-deletion, etc.)
        """
        # 1. Verificar que el usuario a eliminar exista
        user_to_delete = await self.user_repository.get_by_id(user_id)
        if not user_to_delete:
            raise NotFoundError(f"User with ID {user_id} not found")
        
        # 2. VALIDACIÓN: No permitir auto-eliminación
        if current_user and current_user.id == user_id:
            raise ValidationError(
                "Cannot delete your own account. "
                "Ask another administrator to delete your account if needed."
            )
        
        # 3. VALIDACIÓN: Si es admin, verificar que no sea el último
        if user_to_delete.role == UserRole.ADMIN:
            active_admins_count = await self.user_repository.count_by_role(UserRole.ADMIN)
            
            # Contar solo los activos
            active_admins = await self.user_repository.get_by_role(UserRole.ADMIN)
            active_count = sum(1 for admin in active_admins if admin.is_active)
            
            if active_count <= 1:
                raise ValidationError(
                    "Cannot delete the last active administrator. "
                    "The system must have at least one active admin. "
                    "Create another administrator first, then delete this one."
                )
        
        # 4. Eliminar el usuario
        success = await self.user_repository.delete(user_id)
        
        if not success:
            raise NotFoundError("User not found or already deleted")
        
        # 5. Retornar detalles de la eliminación
        return {
            "success": True,
            "deleted_user": {
                "id": str(user_id),
                "email": user_to_delete.email,
                "full_name": user_to_delete.full_name,
                "role": user_to_delete.role.value
            },
            "message": f"User '{user_to_delete.full_name}' ({user_to_delete.role.value}) deleted successfully",
            "deleted_by": str(current_user.id) if current_user else "system"
        }
    
    async def count_users_by_role(self, role: UserRole) -> int:
        """Count users by role."""
        return await self.user_repository.count_by_role(role)
    
    async def count_active_users(self) -> int:
        """Count all active users."""
        return await self.user_repository.count_active_users()
