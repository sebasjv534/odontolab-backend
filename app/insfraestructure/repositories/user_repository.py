"""
SQLAlchemy implementation of user repository interface.

This module provides the concrete implementation of the user repository
using SQLAlchemy for database operations with PostgreSQL.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.domain.models.user_model import User
from app.domain.models.role_model import Role
from app.domain.models.profile_models import DentistProfile, ReceptionistProfile, AdministratorProfile
from app.application.interfaces.user_repository import IUserRepository, IRoleRepository
from app.application.exceptions import ValidationError, UserAlreadyExistsError


class UserRepository(IUserRepository):
    """
    SQLAlchemy implementation of the user repository interface.
    
    This repository handles all database operations related to users,
    including CRUD operations and role-based queries.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the user repository.
        
        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        self.session = session
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by username (email in this case).
        
        Args:
            username (str): The username to search for
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.email == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email address.
        
        Args:
            email (str): The email address to search for
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Retrieve a user by ID.
        
        Args:
            user_id (UUID): The user ID to search for
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.role))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user: User) -> User:
        """
        Create a new user.
        
        Args:
            user (User): The user entity to create
            
        Returns:
            User: The created user with assigned ID
            
        Raises:
            UserAlreadyExistsError: If user with email already exists
        """
        try:
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except IntegrityError as e:
            await self.session.rollback()
            if "unique constraint" in str(e).lower():
                raise UserAlreadyExistsError("User with this email already exists")
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def update(self, user: User) -> User:
        """
        Update an existing user.
        
        Args:
            user (User): The user entity to update
            
        Returns:
            User: The updated user
        """
        try:
            await self.session.merge(user)
            await self.session.commit()
            await self.session.refresh(user)
            return user
        except IntegrityError as e:
            await self.session.rollback()
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def delete(self, user_id: UUID) -> bool:
        """
        Delete a user by ID.
        
        Args:
            user_id (UUID): The ID of the user to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            await self.session.delete(user)
            await self.session.commit()
            return True
        return False
    
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        List users with pagination.
        
        Args:
            skip (int): Number of users to skip
            limit (int): Maximum number of users to return
            
        Returns:
            List[User]: List of users
        """
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.role))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_users_by_role(self, role_name: str) -> List[User]:
        """
        Get all users with a specific role.
        
        Args:
            role_name (str): The role name to filter by
            
        Returns:
            List[User]: List of users with the specified role
        """
        result = await self.session.execute(
            select(User)
            .join(Role)
            .options(selectinload(User.role))
            .where(Role.name == role_name)
        )
        return result.scalars().all()
    
    async def create_dentist_profile(self, profile: DentistProfile) -> DentistProfile:
        """
        Create a dentist profile.
        
        Args:
            profile (DentistProfile): Dentist profile to create
            
        Returns:
            DentistProfile: Created profile instance
        """
        try:
            self.session.add(profile)
            await self.session.commit()
            await self.session.refresh(profile)
            return profile
        except IntegrityError as e:
            await self.session.rollback()
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def create_receptionist_profile(self, profile: ReceptionistProfile) -> ReceptionistProfile:
        """
        Create a receptionist profile.
        
        Args:
            profile (ReceptionistProfile): Receptionist profile to create
            
        Returns:
            ReceptionistProfile: Created profile instance
        """
        try:
            self.session.add(profile)
            await self.session.commit()
            await self.session.refresh(profile)
            return profile
        except IntegrityError as e:
            await self.session.rollback()
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def create_administrator_profile(self, profile: AdministratorProfile) -> AdministratorProfile:
        """
        Create an administrator profile.
        
        Args:
            profile (AdministratorProfile): Administrator profile to create
            
        Returns:
            AdministratorProfile: Created profile instance
        """
        try:
            self.session.add(profile)
            await self.session.commit()
            await self.session.refresh(profile)
            return profile
        except IntegrityError as e:
            await self.session.rollback()
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def get_dentist_profile_by_user_id(self, user_id: UUID) -> Optional[DentistProfile]:
        """
        Get dentist profile by user ID.
        
        Args:
            user_id (UUID): User's unique identifier
            
        Returns:
            Optional[DentistProfile]: Dentist profile if found
        """
        result = await self.session.execute(
            select(DentistProfile).where(DentistProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_receptionist_profile_by_user_id(self, user_id: UUID) -> Optional[ReceptionistProfile]:
        """
        Get receptionist profile by user ID.
        
        Args:
            user_id (UUID): User's unique identifier
            
        Returns:
            Optional[ReceptionistProfile]: Receptionist profile if found
        """
        result = await self.session.execute(
            select(ReceptionistProfile).where(ReceptionistProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_administrator_profile_by_user_id(self, user_id: UUID) -> Optional[AdministratorProfile]:
        """
        Get administrator profile by user ID.
        
        Args:
            user_id (UUID): User's unique identifier
            
        Returns:
            Optional[AdministratorProfile]: Administrator profile if found
        """
        result = await self.session.execute(
            select(AdministratorProfile).where(AdministratorProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()


class RoleRepository(IRoleRepository):
    """
    SQLAlchemy implementation of the role repository interface.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize the role repository.
        
        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        self.session = session
    
    async def get_by_name(self, name: str) -> Optional[Role]:
        """
        Retrieve a role by name.
        
        Args:
            name (str): The role name to search for
            
        Returns:
            Optional[Role]: The role if found, None otherwise
        """
        result = await self.session.execute(
            select(Role).where(Role.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, role_id: UUID) -> Optional[Role]:
        """
        Retrieve a role by ID.
        
        Args:
            role_id (UUID): The role ID to search for
            
        Returns:
            Optional[Role]: The role if found, None otherwise
        """
        result = await self.session.execute(
            select(Role).where(Role.id == role_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, role: Role) -> Role:
        """
        Create a new role.
        
        Args:
            role (Role): The role entity to create
            
        Returns:
            Role: The created role with assigned ID
        """
        try:
            self.session.add(role)
            await self.session.commit()
            await self.session.refresh(role)
            return role
        except IntegrityError as e:
            await self.session.rollback()
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def list_roles(self) -> List[Role]:
        """
        List all available roles.
        
        Returns:
            List[Role]: List of all roles
        """
        result = await self.session.execute(select(Role))
        return result.scalars().all()