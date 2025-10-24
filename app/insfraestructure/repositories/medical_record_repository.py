"""
Medical Record repository for database operations.

This module implements the data access layer for MedicalRecord entity operations following
the API_SUMMARY specifications.
"""

from typing import Optional, List
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timedelta

from app.domain.models import MedicalRecord


class MedicalRecordRepository:
    """Repository class for MedicalRecord CRUD operations."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize MedicalRecordRepository with database session.
        
        Args:
            db (AsyncSession): Database session
        """
        self.db = db
    
    async def create(self, record_data: dict, dentist_id: UUID) -> MedicalRecord:
        """
        Create a new medical record.
        
        Args:
            record_data (dict): Medical record data
            dentist_id (UUID): Dentist ID who created the record
            
        Returns:
            MedicalRecord: Created medical record instance
        """
        record_data['dentist_id'] = dentist_id
        record = MedicalRecord(**record_data)
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record
    
    async def get_by_id(self, record_id: UUID) -> Optional[MedicalRecord]:
        """
        Get medical record by ID.
        
        Args:
            record_id (UUID): Medical record's unique identifier
            
        Returns:
            Optional[MedicalRecord]: Medical record instance if found, None otherwise
        """
        result = await self.db.execute(
            select(MedicalRecord).where(MedicalRecord.id == record_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_patient(
        self,
        patient_id: UUID,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[MedicalRecord], int]:
        """
        Get all medical records for a specific patient.
        
        Args:
            patient_id (UUID): Patient's unique identifier
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            tuple[List[MedicalRecord], int]: List of medical records and total count
        """
        # Get total count
        count_result = await self.db.execute(
            select(func.count(MedicalRecord.id))
            .where(MedicalRecord.patient_id == patient_id)
        )
        total = count_result.scalar()
        
        # Get medical records
        query = (
            select(MedicalRecord)
            .where(MedicalRecord.patient_id == patient_id)
            .offset(skip)
            .limit(limit)
            .order_by(MedicalRecord.visit_date.desc())
        )
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        return records, total
    
    async def get_by_dentist(
        self,
        dentist_id: UUID,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[MedicalRecord], int]:
        """
        Get all medical records created by a specific dentist.
        
        Args:
            dentist_id (UUID): Dentist's unique identifier
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            tuple[List[MedicalRecord], int]: List of medical records and total count
        """
        # Get total count
        count_result = await self.db.execute(
            select(func.count(MedicalRecord.id))
            .where(MedicalRecord.dentist_id == dentist_id)
        )
        total = count_result.scalar()
        
        # Get medical records
        query = (
            select(MedicalRecord)
            .where(MedicalRecord.dentist_id == dentist_id)
            .offset(skip)
            .limit(limit)
            .order_by(MedicalRecord.visit_date.desc())
        )
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        return records, total
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[MedicalRecord], int]:
        """
        Get all medical records with pagination.
        
        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            tuple[List[MedicalRecord], int]: List of medical records and total count
        """
        # Get total count
        count_result = await self.db.execute(select(func.count(MedicalRecord.id)))
        total = count_result.scalar()
        
        # Get medical records
        query = (
            select(MedicalRecord)
            .offset(skip)
            .limit(limit)
            .order_by(MedicalRecord.visit_date.desc())
        )
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        return records, total
    
    async def update(self, record_id: UUID, record_data: dict) -> Optional[MedicalRecord]:
        """
        Update medical record information.
        
        Args:
            record_id (UUID): Medical record's unique identifier
            record_data (dict): Medical record data to update
            
        Returns:
            Optional[MedicalRecord]: Updated medical record instance if found, None otherwise
        """
        # Remove None values
        record_data = {k: v for k, v in record_data.items() if v is not None}
        
        if not record_data:
            return await self.get_by_id(record_id)
        
        await self.db.execute(
            update(MedicalRecord)
            .where(MedicalRecord.id == record_id)
            .values(**record_data)
        )
        await self.db.commit()
        
        return await self.get_by_id(record_id)
    
    async def delete(self, record_id: UUID) -> bool:
        """
        Delete a medical record (hard delete).
        
        Args:
            record_id (UUID): Medical record's unique identifier
            
        Returns:
            bool: True if record was deleted, False otherwise
        """
        result = await self.db.execute(
            delete(MedicalRecord).where(MedicalRecord.id == record_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def count_all(self) -> int:
        """
        Count all medical records.
        
        Returns:
            int: Total number of medical records
        """
        result = await self.db.execute(select(func.count(MedicalRecord.id)))
        return result.scalar()
    
    async def count_recent(self, days: int = 30) -> int:
        """
        Count medical records created in the last N days.
        
        Args:
            days (int): Number of days to look back
            
        Returns:
            int: Number of recent medical records
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(func.count(MedicalRecord.id))
            .where(MedicalRecord.created_at >= cutoff_date)
        )
        return result.scalar()
    
    async def count_by_dentist(self, dentist_id: UUID) -> int:
        """
        Count medical records created by a specific dentist.
        
        Args:
            dentist_id (UUID): Dentist's unique identifier
            
        Returns:
            int: Number of medical records created by the dentist
        """
        result = await self.db.execute(
            select(func.count(MedicalRecord.id))
            .where(MedicalRecord.dentist_id == dentist_id)
        )
        return result.scalar()
    
    async def count_recent_by_dentist(self, dentist_id: UUID, days: int = 30) -> int:
        """
        Count medical records created by a dentist in the last N days.
        
        Args:
            dentist_id (UUID): Dentist's unique identifier
            days (int): Number of days to look back
            
        Returns:
            int: Number of recent medical records by the dentist
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(func.count(MedicalRecord.id))
            .where(MedicalRecord.dentist_id == dentist_id)
            .where(MedicalRecord.created_at >= cutoff_date)
        )
        return result.scalar()
    
    async def count_unique_patients_by_dentist(self, dentist_id: UUID) -> int:
        """
        Count unique patients treated by a specific dentist.
        
        Args:
            dentist_id (UUID): Dentist's unique identifier
            
        Returns:
            int: Number of unique patients
        """
        result = await self.db.execute(
            select(func.count(func.distinct(MedicalRecord.patient_id)))
            .where(MedicalRecord.dentist_id == dentist_id)
        )
        return result.scalar()
    
    async def get_upcoming_appointments(
        self,
        limit: int = 10
    ) -> List[MedicalRecord]:
        """
        Get upcoming appointments (medical records with future next_appointment).
        
        Args:
            limit (int): Maximum number of records to return
            
        Returns:
            List[MedicalRecord]: List of medical records with upcoming appointments
        """
        now = datetime.utcnow()
        query = (
            select(MedicalRecord)
            .where(MedicalRecord.next_appointment >= now)
            .order_by(MedicalRecord.next_appointment)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def count_upcoming_appointments(self) -> int:
        """
        Count upcoming appointments.
        
        Returns:
            int: Number of upcoming appointments
        """
        now = datetime.utcnow()
        result = await self.db.execute(
            select(func.count(MedicalRecord.id))
            .where(MedicalRecord.next_appointment >= now)
        )
        return result.scalar()
