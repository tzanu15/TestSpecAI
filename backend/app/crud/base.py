"""
Base CRUD operations for all entities.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.base import BaseModel as SQLAlchemyBaseModel
from app.utils.exceptions import TestSpecAIException, ValidationError, NotFoundError, ConflictError
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=SQLAlchemyBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base CRUD class with common operations for all entities.

    Provides async methods for create, read, update, delete, list, and count operations.
    Includes support for filtering, sorting, and pagination.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD operations for a specific model.

        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Get a single record by ID.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Model instance or None if not found
        """
        try:
            result = await db.execute(
                select(self.model).where(
                    and_(self.model.id == id, self.model.is_active == True)
                )
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} with id {id}: {str(e)}")
            raise TestSpecAIException(f"Failed to retrieve {self.model.__name__}")

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_direction: str = "asc"
    ) -> List[ModelType]:
        """
        Get multiple records with pagination, filtering, and sorting.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field filters
            order_by: Field to order by
            order_direction: Order direction (asc/desc)

        Returns:
            List of model instances
        """
        try:
            query = select(self.model).where(self.model.is_active == True)

            # Apply filters
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        if isinstance(value, list):
                            query = query.where(getattr(self.model, field).in_(value))
                        elif isinstance(value, str) and "%" in value:
                            query = query.where(getattr(self.model, field).ilike(value))
                        else:
                            query = query.where(getattr(self.model, field) == value)

            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                if order_direction.lower() == "desc":
                    query = query.order_by(desc(getattr(self.model, order_by)))
                else:
                    query = query.order_by(asc(getattr(self.model, order_by)))
            else:
                query = query.order_by(desc(self.model.created_at))

            # Apply pagination
            query = query.offset(skip).limit(limit)

            result = await db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting multiple {self.model.__name__}: {str(e)}")
            raise TestSpecAIException(f"Failed to retrieve {self.model.__name__} records")

    async def count(
        self,
        db: AsyncSession,
        *,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count records with optional filtering.

        Args:
            db: Database session
            filters: Dictionary of field filters

        Returns:
            Number of matching records
        """
        try:
            query = select(func.count(self.model.id)).where(self.model.is_active == True)

            # Apply filters
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        if isinstance(value, list):
                            query = query.where(getattr(self.model, field).in_(value))
                        elif isinstance(value, str) and "%" in value:
                            query = query.where(getattr(self.model, field).ilike(value))
                        else:
                            query = query.where(getattr(self.model, field) == value)

            result = await db.execute(query)
            return result.scalar()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            raise TestSpecAIException(f"Failed to count {self.model.__name__} records")

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.

        Args:
            db: Database session
            obj_in: Pydantic model with data to create

        Returns:
            Created model instance
        """
        try:
            obj_in_data = jsonable_encoder(obj_in)
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            logger.info(f"Created {self.model.__name__} with id {db_obj.id}")
            return db_obj
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error creating {self.model.__name__}: {str(e)}")
            raise ConflictError(f"Failed to create {self.model.__name__}: constraint violation")
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise TestSpecAIException(f"Failed to create {self.model.__name__}")

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record.

        Args:
            db: Database session
            db_obj: Existing model instance
            obj_in: Pydantic model or dict with update data

        Returns:
            Updated model instance
        """
        try:
            obj_data = jsonable_encoder(db_obj)
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.dict(exclude_unset=True)

            for field in obj_data:
                if field in update_data:
                    setattr(db_obj, field, update_data[field])

            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            logger.info(f"Updated {self.model.__name__} with id {db_obj.id}")
            return db_obj
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error updating {self.model.__name__}: {str(e)}")
            raise ConflictError(f"Failed to update {self.model.__name__}: constraint violation")
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {str(e)}")
            raise TestSpecAIException(f"Failed to update {self.model.__name__}")

    async def remove(self, db: AsyncSession, *, id: Any) -> ModelType:
        """
        Soft delete a record by setting is_active to False.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Deleted model instance
        """
        try:
            result = await db.execute(
                select(self.model).where(
                    and_(self.model.id == id, self.model.is_active == True)
                )
            )
            obj = result.scalar_one_or_none()
            if not obj:
                raise NotFoundError(f"{self.model.__name__} not found")

            obj.is_active = False
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
            logger.info(f"Soft deleted {self.model.__name__} with id {id}")
            return obj
        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Error deleting {self.model.__name__}: {str(e)}")
            raise TestSpecAIException(f"Failed to delete {self.model.__name__}")

    async def hard_delete(self, db: AsyncSession, *, id: Any) -> ModelType:
        """
        Permanently delete a record from the database.

        Args:
            db: Database session
            id: Record ID

        Returns:
            Deleted model instance
        """
        try:
            result = await db.execute(
                select(self.model).where(self.model.id == id)
            )
            obj = result.scalar_one_or_none()
            if not obj:
                raise NotFoundError(f"{self.model.__name__} not found")

            await db.delete(obj)
            await db.commit()
            logger.info(f"Hard deleted {self.model.__name__} with id {id}")
            return obj
        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Error hard deleting {self.model.__name__}: {str(e)}")
            raise TestSpecAIException(f"Failed to permanently delete {self.model.__name__}")

    async def search(
        self,
        db: AsyncSession,
        *,
        search_term: str,
        search_fields: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Search records across multiple fields.

        Args:
            db: Database session
            search_term: Term to search for
            search_fields: List of field names to search in
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching model instances
        """
        try:
            if not search_fields:
                raise ValidationError("At least one search field must be specified")

            query = select(self.model).where(self.model.is_active == True)

            # Build search conditions
            search_conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    search_conditions.append(
                        getattr(self.model, field).ilike(f"%{search_term}%")
                    )

            if search_conditions:
                query = query.where(or_(*search_conditions))
            else:
                return []

            query = query.offset(skip).limit(limit)
            result = await db.execute(query)
            return result.scalars().all()
        except ValidationError:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error searching {self.model.__name__}: {str(e)}")
            raise TestSpecAIException(f"Failed to search {self.model.__name__} records")

    async def exists(self, db: AsyncSession, *, id: Any) -> bool:
        """
        Check if a record exists.

        Args:
            db: Database session
            id: Record ID

        Returns:
            True if record exists and is active, False otherwise
        """
        try:
            result = await db.execute(
                select(func.count(self.model.id)).where(
                    and_(self.model.id == id, self.model.is_active == True)
                )
            )
            return result.scalar() > 0
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__}: {str(e)}")
            raise TestSpecAIException(f"Failed to check existence of {self.model.__name__}")

    async def get_with_relationships(
        self,
        db: AsyncSession,
        *,
        id: Any,
        relationships: List[str]
    ) -> Optional[ModelType]:
        """
        Get a record with specified relationships loaded.

        Args:
            db: Database session
            id: Record ID
            relationships: List of relationship names to load

        Returns:
            Model instance with relationships loaded or None if not found
        """
        try:
            query = select(self.model).where(
                and_(self.model.id == id, self.model.is_active == True)
            )

            # Load relationships
            for rel in relationships:
                if hasattr(self.model, rel):
                    query = query.options(selectinload(getattr(self.model, rel)))

            result = await db.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} with relationships: {str(e)}")
            raise TestSpecAIException(f"Failed to retrieve {self.model.__name__} with relationships")
