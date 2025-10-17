"""
User management service for the odontology system.

This module provides user management services including user creation,
profile management, and role-specific operations for administrators,
dentists, and receptionists.
"""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.exc import IntegrityError

from app.domain.models.user_model import User
from app.domain.models.role_model import Role, RoleType
from app.domain.models.profile_models import DentistProfile, ReceptionistProfile, AdministratorProfile
from app.domain.schemas.user_schemas import (
    AdministratorCreateRequest,
    DentistCreateRequest, 
    ReceptionistCreateRequest,
    UserUpdateRequest,
    UserDetailResponse
)
from app.application.interfaces.user_repository import IUserRepository, IRoleRepository
from app.application.services.auth_service import AuthService
from app.application.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    RoleNotFoundError,
    ValidationError
)


class UserService:
    """
    User management service for handling user operations.
    
    This service manages user creation, updates, and profile management
    for different roles in the dental clinic system.
    """
    
    def __init__(
        self,
        user_repository: IUserRepository,
        role_repository: IRoleRepository,
        auth_service: AuthService
    ):
        """
        Initialize the user service.
        
        Args:
            user_repository (IUserRepository): User repository implementation
            role_repository (IRoleRepository): Role repository implementation
            auth_service (AuthService): Authentication service
        """
        self.user_repository = user_repository
        self.role_repository = role_repository
        self.auth_service = auth_service
    
    async def create_administrator(self, request: AdministratorCreateRequest) -> UserDetailResponse:
        """
        Create a new administrator user with profile.
        
        Args:
            request (AdministratorCreateRequest): Administrator creation request
            
        Returns:
            UserDetailResponse: Created administrator details
            
        Raises:
            UserAlreadyExistsError: If user with email already exists
            RoleNotFoundError: If administrator role doesn't exist
            ValidationError: If request data is invalid
        """
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(request.user.email)
        if existing_user:
            raise UserAlreadyExistsError(f"User with email {request.user.email} already exists")
        
        # Get administrator role
        admin_role = await self.role_repository.get_by_name(RoleType.ADMINISTRATOR.value)
        if not admin_role:
            raise RoleNotFoundError("Administrator role not found")
        
        try:
            # Create user
            user = User(
                email=request.user.email,
                password_hash=self.auth_service.get_password_hash(request.user.password),
                first_name=request.user.first_name,
                last_name=request.user.last_name,
                is_active=True,
                is_verified=True,
                role_id=admin_role.id
            )
            
            created_user = await self.user_repository.create(user)
            
            # Create administrator profile
            admin_profile = AdministratorProfile(
                user_id=created_user.id,
                department=request.profile.department,
                permissions_level=request.profile.permissions_level
            )
            
            await self.user_repository.create_administrator_profile(admin_profile)
            
            return UserDetailResponse(
                id=str(created_user.id),
                username=created_user.email,  # Using email as username
                email=created_user.email,
                first_name=created_user.first_name,
                last_name=created_user.last_name,
                is_active=created_user.is_active,
                role=admin_role.name,
                created_at=created_user.created_at,
                phone=None  # Add phone field if needed
            )
            
        except IntegrityError as e:
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def create_dentist(self, request: DentistCreateRequest) -> UserDetailResponse:
        """
        Create a new dentist user with profile.
        
        Args:
            request (DentistCreateRequest): Dentist creation request
            
        Returns:
            UserDetailResponse: Created dentist details
            
        Raises:
            UserAlreadyExistsError: If user with email already exists
            RoleNotFoundError: If dentist role doesn't exist
            ValidationError: If request data is invalid
        """
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(request.user.email)
        if existing_user:
            raise UserAlreadyExistsError(f"User with email {request.user.email} already exists")
        
        # Get dentist role
        dentist_role = await self.role_repository.get_by_name(RoleType.DENTIST.value)
        if not dentist_role:
            raise RoleNotFoundError("Dentist role not found")
        
        try:
            # Create user
            user = User(
                email=request.user.email,
                password_hash=self.auth_service.get_password_hash(request.user.password),
                first_name=request.user.first_name,
                last_name=request.user.last_name,
                is_active=True,
                is_verified=True,
                role_id=dentist_role.id
            )
            
            created_user = await self.user_repository.create(user)
            
            # Create dentist profile
            dentist_profile = DentistProfile(
                user_id=created_user.id,
                license_number=request.profile.license_number,
                specialization=request.profile.specialization,
                years_experience=request.profile.years_experience,
                education=request.profile.education,
                phone=request.profile.phone
            )
            
            created_profile = await self.user_repository.create_dentist_profile(dentist_profile)
            
            return UserDetailResponse(
                id=str(created_user.id),
                username=created_user.email,
                email=created_user.email,
                first_name=created_user.first_name,
                last_name=created_user.last_name,
                is_active=created_user.is_active,
                role=dentist_role.name,
                created_at=created_user.created_at,
                dentist_profile={
                    "id": str(created_profile.id),
                    "license_number": created_profile.license_number,
                    "specialization": created_profile.specialization,
                    "years_experience": created_profile.years_experience,
                    "education": created_profile.education,
                    "created_at": created_profile.created_at
                }
            )
            
        except IntegrityError as e:
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def create_receptionist(self, request: ReceptionistCreateRequest) -> UserDetailResponse:
        """
        Create a new receptionist user with profile.
        
        Args:
            request (ReceptionistCreateRequest): Receptionist creation request
            
        Returns:
            UserDetailResponse: Created receptionist details
            
        Raises:
            UserAlreadyExistsError: If user with email already exists
            RoleNotFoundError: If receptionist role doesn't exist
            ValidationError: If request data is invalid
        """
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(request.user.email)
        if existing_user:
            raise UserAlreadyExistsError(f"User with email {request.user.email} already exists")
        
        # Get receptionist role
        receptionist_role = await self.role_repository.get_by_name(RoleType.RECEPTIONIST.value)
        if not receptionist_role:
            raise RoleNotFoundError("Receptionist role not found")
        
        try:
            # Create user
            user = User(
                email=request.user.email,
                password_hash=self.auth_service.get_password_hash(request.user.password),
                first_name=request.user.first_name,
                last_name=request.user.last_name,
                is_active=True,
                is_verified=True,
                role_id=receptionist_role.id
            )
            
            created_user = await self.user_repository.create(user)
            
            # Create receptionist profile
            receptionist_profile = ReceptionistProfile(
                user_id=created_user.id,
                employee_id=request.profile.employee_id,
                shift_schedule=request.profile.shift_schedule,
                phone=request.profile.phone,
                emergency_contact=request.profile.emergency_contact,
                hire_date=request.profile.hire_date
            )
            
            created_profile = await self.user_repository.create_receptionist_profile(receptionist_profile)
            
            return UserDetailResponse(
                id=str(created_user.id),
                username=created_user.email,
                email=created_user.email,
                first_name=created_user.first_name,
                last_name=created_user.last_name,
                is_active=created_user.is_active,
                role=receptionist_role.name,
                created_at=created_user.created_at,
                receptionist_profile={
                    "id": str(created_profile.id),
                    "employee_id": created_profile.employee_id,
                    "shift_schedule": created_profile.shift_schedule,
                    "phone": created_profile.phone,
                    "emergency_contact": created_profile.emergency_contact,
                    "hire_date": created_profile.hire_date,
                    "created_at": created_profile.created_at
                }
            )
            
        except IntegrityError as e:
            raise ValidationError(f"Database integrity error: {str(e)}")
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[UserDetailResponse]:
        """
        Get a user by their ID with profile information.
        
        Args:
            user_id (UUID): User's unique identifier
            
        Returns:
            Optional[UserDetailResponse]: User details if found, None otherwise
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        response = UserDetailResponse(
            id=str(user.id),
            username=user.email,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            role=user.role.name if user.role else None,
            created_at=user.created_at
        )
        
        # Add profile information based on role
        if user.role and user.role.name == RoleType.DENTIST.value:
            dentist_profile = await self.user_repository.get_dentist_profile_by_user_id(user.id)
            if dentist_profile:
                response.dentist_profile = {
                    "id": str(dentist_profile.id),
                    "license_number": dentist_profile.license_number,
                    "specialization": dentist_profile.specialization,
                    "years_experience": dentist_profile.years_experience,
                    "education": dentist_profile.education,
                    "created_at": dentist_profile.created_at
                }
        
        elif user.role and user.role.name == RoleType.RECEPTIONIST.value:
            receptionist_profile = await self.user_repository.get_receptionist_profile_by_user_id(user.id)
            if receptionist_profile:
                response.receptionist_profile = {
                    "id": str(receptionist_profile.id),
                    "employee_id": receptionist_profile.employee_id,
                    "shift_schedule": receptionist_profile.shift_schedule,
                    "phone": receptionist_profile.phone,
                    "emergency_contact": receptionist_profile.emergency_contact,
                    "hire_date": receptionist_profile.hire_date,
                    "created_at": receptionist_profile.created_at
                }
        
        return response
    
    async def update_user(self, user_id: UUID, request: UserUpdateRequest) -> Optional[UserDetailResponse]:
        """
        Update user information.
        
        Args:
            user_id (UUID): User's unique identifier
            request (UserUpdateRequest): Update request data
            
        Returns:
            Optional[UserDetailResponse]: Updated user details if found, None otherwise
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        
        # Update user fields
        update_data = {}
        if request.first_name is not None:
            update_data["first_name"] = request.first_name
        if request.last_name is not None:
            update_data["last_name"] = request.last_name
        if request.email is not None:
            update_data["email"] = request.email
        
        if update_data:
            updated_user = await self.user_repository.update(user_id, update_data)
            return await self.get_user_by_id(user_id)
        
        return await self.get_user_by_id(user_id)
    
    async def get_users_by_role(self, role_name: str) -> List[UserDetailResponse]:
        """
        Get all users with a specific role.
        
        Args:
            role_name (str): Role name to filter by
            
        Returns:
            List[UserDetailResponse]: List of users with the specified role
        """
        users = await self.user_repository.get_users_by_role(role_name)
        user_responses = []
        
        for user in users:
            user_detail = await self.get_user_by_id(user.id)
            if user_detail:
                user_responses.append(user_detail)
        
        return user_responses
    
    async def list_all_users(self, skip: int = 0, limit: int = 100) -> List[UserDetailResponse]:
        """
        List all users with pagination.
        
        Args:
            skip (int): Number of users to skip
            limit (int): Maximum number of users to return
            
        Returns:
            List[UserDetailResponse]: List of users
        """
        users = await self.user_repository.list_users(skip=skip, limit=limit)
        user_responses = []
        
        for user in users:
            user_detail = await self.get_user_by_id(user.id)
            if user_detail:
                user_responses.append(user_detail)
        
        return user_responses
    
    async def deactivate_user(self, user_id: UUID) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id (UUID): User's unique identifier
            
        Returns:
            bool: True if user was deactivated, False if not found
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        await self.user_repository.update(user_id, {"is_active": False})
        return True
    
    async def activate_user(self, user_id: UUID) -> bool:
        """
        Activate a user account.
        
        Args:
            user_id (UUID): User's unique identifier
            
        Returns:
            bool: True if user was activated, False if not found
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            return False
        
        await self.user_repository.update(user_id, {"is_active": True})
        return True