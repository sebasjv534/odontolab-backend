"""
User repository interface for the odontology system.

This module defines the abstract interface for user data access operations,
following the repository pattern for clean architecture.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID
from app.domain.models.user_model import User
from app.domain.models.role_model import Role


class IUserRepository(ABC):
    """
    Abstract interface for user data access operations.
    
    This interface defines the contract for user repository implementations,
    enabling dependency inversion and testability.
    """

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by username.
        
        Args:
            username (str): The username to search for
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by email address.
        
        Args:
            email (str): The email address to search for
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Retrieve a user by ID.
        
        Args:
            user_id (UUID): The user ID to search for
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Create a new user.
        
        Args:
            user (User): The user entity to create
            
        Returns:
            User: The created user with assigned ID
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> User:
        """
        Update an existing user.
        
        Args:
            user (User): The user entity to update
            
        Returns:
            User: The updated user
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """
        Delete a user by ID.
        
        Args:
            user_id (UUID): The ID of the user to delete
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        raise NotImplementedError

    @abstractmethod
    async def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        List users with pagination.
        
        Args:
            skip (int): Number of users to skip
            limit (int): Maximum number of users to return
            
        Returns:
            List[User]: List of users
        """
        raise NotImplementedError

    @abstractmethod
    async def get_users_by_role(self, role_name: str) -> List[User]:
        """
        Get all users with a specific role.
        
        Args:
            role_name (str): The role name to filter by
            
        Returns:
            List[User]: List of users with the specified role
        """
        raise NotImplementedError


class IRoleRepository(ABC):
    """
    Abstract interface for role data access operations.
    """

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Role]:
        """
        Retrieve a role by name.
        
        Args:
            name (str): The role name to search for
            
        Returns:
            Optional[Role]: The role if found, None otherwise
        """
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, role_id: UUID) -> Optional[Role]:
        """
        Retrieve a role by ID.
        
        Args:
            role_id (UUID): The role ID to search for
            
        Returns:
            Optional[Role]: The role if found, None otherwise
        """
        raise NotImplementedError

    @abstractmethod
    async def create(self, role: Role) -> Role:
        """
        Create a new role.
        
        Args:
            role (Role): The role entity to create
            
        Returns:
            Role: The created role with assigned ID
        """
        raise NotImplementedError

    @abstractmethod
    async def list_roles(self) -> List[Role]:
        """
        List all available roles.
        
        Returns:
            List[Role]: List of all roles
        """
        raise NotImplementedError