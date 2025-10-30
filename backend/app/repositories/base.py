"""Base repository for data access operations."""
from abc import ABC
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(ABC, Generic[ModelType]):
    """Abstract base repository for data access operations."""

    def __init__(self, db: AsyncSession, model: type[ModelType]):
        """
        Initialize repository with database session and model.

        Args:
            db: Async database session
            model: SQLAlchemy model class
        """
        self.db = db
        self.model = model

    async def get_by_id(self, id: UUID) -> ModelType | None:
        """
        Retrieve a record by ID.

        Args:
            id: UUID of the record

        Returns:
            Model instance if found, None otherwise
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def create(self, obj: ModelType) -> ModelType:
        """
        Create a new record.

        Args:
            obj: Model instance to create

        Returns:
            Created model instance with populated fields
        """
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def delete(self, id: UUID) -> bool:
        """
        Delete a record by ID.

        Args:
            id: UUID of the record to delete

        Returns:
            True if deleted, False if not found
        """
        obj = await self.get_by_id(id)
        if obj:
            await self.db.delete(obj)
            return True
        return False
