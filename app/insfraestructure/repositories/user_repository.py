"""
User repository for database operations.

This module implements the data access layer for User entity operations.
"""

from typing import Optional, List
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.domain.models import User, UserRole
from app.core.security import hash_password


class UserRepository:
    """Repository for User entity database operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize the user repository."""
        self.db = db
    
    async def create(self, user_data: dict) -> User:
        """Create a new user."""
        if "password" in user_data:
            user_data["hashed_password"] = hash_password(user_data.pop("password"))
        
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[User], int]:
        """Get all users with pagination and filters."""
        query = select(User)
        
        if role is not None:
            query = query.where(User.role == role)
        
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        count_query = select(func.count()).select_from(User)
        if role is not None:
            count_query = count_query.where(User.role == role)
        if is_active is not None:
            count_query = count_query.where(User.is_active == is_active)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        return list(users), total
    
    async def get_by_role(self, role: UserRole) -> List[User]:
        """Get all users with a specific role."""
        result = await self.db.execute(
            select(User).where(User.role == role)
        )
        return list(result.scalars().all())
    
    async def update(self, user_id: UUID, user_data: dict) -> Optional[User]:
        """Update user information."""
        if "password" in user_data:
            user_data["hashed_password"] = hash_password(user_data.pop("password"))
        
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**user_data)
            .returning(User)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one_or_none()
    
    async def deactivate(self, user_id: UUID) -> Optional[User]:
        """Deactivate a user."""
        return await self.update(user_id, {"is_active": False})
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete a user."""
        stmt = delete(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def count_by_role(self, role: UserRole) -> int:
        """Count users by role."""
        result = await self.db.execute(
            select(func.count()).select_from(User).where(User.role == role)
        )
        return result.scalar()
    
    async def count_active_users(self) -> int:
        """Count all active users."""
        result = await self.db.execute(
            select(func.count()).select_from(User).where(User.is_active == True)
        )
        return result.scalar()
    
    async def count(self) -> int:
        """Count all users."""
        result = await self.db.execute(
            select(func.count()).select_from(User)
        )
        return result.scalar()
