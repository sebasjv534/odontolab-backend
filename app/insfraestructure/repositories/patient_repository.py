"""
Patient repository for database operations.

This module implements the data access layer for Patient entity operations following
the API_SUMMARY specifications.
"""

from typing import Optional, List
from sqlalchemy import select, update, delete, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timedelta

from app.domain.models import Patient


class PatientRepository:
    """Repository class for Patient CRUD operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize PatientRepository with database session.
        
        Args:
            db (AsyncSession): Database session
        """
        self.db = db
    
    async def create(self, patient_data: dict, created_by: UUID) -> Patient:
        """
        Create a new patient.
        
        Args:
            patient_data (dict): Patient data
            created_by (UUID): User ID who created the patient
            
        Returns:
            Patient: Created patient instance
        """
        patient_data['created_by'] = created_by
        patient = Patient(**patient_data)
        self.db.add(patient)
        await self.db.commit()
        await self.db.refresh(patient)
        return patient
    
    async def get_by_id(self, patient_id: UUID) -> Optional[Patient]:
        """
        Get patient by ID.
        
        Args:
            patient_id (UUID): Patient's unique identifier
            
        Returns:
            Optional[Patient]: Patient instance if found, None otherwise
        """
        result = await self.db.execute(
            select(Patient).where(Patient.id == patient_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[Patient]:
        """
        Get patient by email.
        
        Args:
            email (str): Patient's email address
            
        Returns:
            Optional[Patient]: Patient instance if found, None otherwise
        """
        result = await self.db.execute(
            select(Patient).where(Patient.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[Patient], int]:
        """
        Get all patients with pagination.
        
        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            tuple[List[Patient], int]: List of patients and total count
        """
        # Get total count
        count_result = await self.db.execute(select(func.count(Patient.id)))
        total = count_result.scalar()
        
        # Get patients
        query = select(Patient).offset(skip).limit(limit).order_by(Patient.created_at.desc())
        result = await self.db.execute(query)
        patients = result.scalars().all()
        
        return patients, total
    
    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[Patient], int]:
        """
        Search patients by name, email, or phone.
        
        Args:
            query (str): Search query
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            tuple[List[Patient], int]: List of matching patients and total count
        """
        search_pattern = f"%{query}%"
        
        # Build search filter
        search_filter = or_(
            Patient.first_name.ilike(search_pattern),
            Patient.last_name.ilike(search_pattern),
            Patient.email.ilike(search_pattern),
            Patient.phone.ilike(search_pattern)
        )
        
        # Get total count
        count_result = await self.db.execute(
            select(func.count(Patient.id)).where(search_filter)
        )
        total = count_result.scalar()
        
        # Get patients
        query_stmt = (
            select(Patient)
            .where(search_filter)
            .offset(skip)
            .limit(limit)
            .order_by(Patient.first_name, Patient.last_name)
        )
        result = await self.db.execute(query_stmt)
        patients = result.scalars().all()
        
        return patients, total
    
    async def update(self, patient_id: UUID, patient_data: dict) -> Optional[Patient]:
        """
        Update patient information.
        
        Args:
            patient_id (UUID): Patient's unique identifier
            patient_data (dict): Patient data to update
            
        Returns:
            Optional[Patient]: Updated patient instance if found, None otherwise
        """
        # Remove None values
        patient_data = {k: v for k, v in patient_data.items() if v is not None}
        
        if not patient_data:
            return await self.get_by_id(patient_id)
        
        await self.db.execute(
            update(Patient)
            .where(Patient.id == patient_id)
            .values(**patient_data)
        )
        await self.db.commit()
        
        return await self.get_by_id(patient_id)
    
    async def delete(self, patient_id: UUID) -> bool:
        """
        Delete a patient (hard delete, will cascade to medical records).
        
        Args:
            patient_id (UUID): Patient's unique identifier
            
        Returns:
            bool: True if patient was deleted, False otherwise
        """
        result = await self.db.execute(
            delete(Patient).where(Patient.id == patient_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def count_all(self) -> int:
        """
        Count all patients.
        
        Returns:
            int: Total number of patients
        """
        result = await self.db.execute(select(func.count(Patient.id)))
        return result.scalar()
    
    async def count_recent(self, days: int = 30) -> int:
        """
        Count patients created in the last N days.
        
        Args:
            days (int): Number of days to look back
            
        Returns:
            int: Number of recent patients
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(func.count(Patient.id))
            .where(Patient.created_at >= cutoff_date)
        )
        return result.scalar()
    
    async def get_by_creator(self, creator_id: UUID) -> List[Patient]:
        """
        Get all patients created by a specific user.
        
        Args:
            creator_id (UUID): User ID who created the patients
            
        Returns:
            List[Patient]: List of patients created by the user
        """
        result = await self.db.execute(
            select(Patient)
            .where(Patient.created_by == creator_id)
            .order_by(Patient.created_at.desc())
        )
        return result.scalars().all()
    
    async def count_by_creator(self, creator_id: UUID) -> int:
        """
        Count patients created by a specific user.
        
        Args:
            creator_id (UUID): User ID who created the patients
            
        Returns:
            int: Number of patients created by the user
        """
        result = await self.db.execute(
            select(func.count(Patient.id))
            .where(Patient.created_by == creator_id)
        )
        return result.scalar()
