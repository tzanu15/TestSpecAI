"""
Transaction management utilities for CRUD operations.
"""
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession, AsyncTransaction
from sqlalchemy import select, update, delete, text
from sqlalchemy.orm import with_for_update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from contextlib import asynccontextmanager
import asyncio
import logging
from datetime import datetime
from app.utils.exceptions import DatabaseError, ValidationError, ConflictError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TransactionManager:
    """
    Manager for database transactions with support for nested transactions,
    locking, and bulk operations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._transaction_stack: List[AsyncTransaction] = []
        self._savepoint_stack: List[str] = []

    @asynccontextmanager
    async def transaction(self, nested: bool = False):
        """
        Context manager for database transactions.

        Args:
            nested: Whether this is a nested transaction (savepoint)

        Yields:
            TransactionManager instance for the transaction
        """
        if nested and self._transaction_stack:
            # Create a savepoint for nested transaction
            savepoint_name = f"savepoint_{len(self._savepoint_stack)}_{datetime.utcnow().timestamp()}"
            savepoint = await self.db.begin_nested()
            self._savepoint_stack.append(savepoint_name)
            self._transaction_stack.append(savepoint)

            try:
                yield self
                await savepoint.commit()
            except Exception as e:
                await savepoint.rollback()
                raise e
            finally:
                self._savepoint_stack.pop()
                self._transaction_stack.pop()
        else:
            # Create a new transaction
            transaction = await self.db.begin()
            self._transaction_stack.append(transaction)

            try:
                yield self
                await transaction.commit()
            except Exception as e:
                await transaction.rollback()
                raise e
            finally:
                self._transaction_stack.pop()

    async def rollback(self):
        """Rollback the current transaction."""
        if self._transaction_stack:
            transaction = self._transaction_stack[-1]
            await transaction.rollback()

    async def commit(self):
        """Commit the current transaction."""
        if self._transaction_stack:
            transaction = self._transaction_stack[-1]
            await transaction.commit()

    def is_in_transaction(self) -> bool:
        """Check if currently in a transaction."""
        return len(self._transaction_stack) > 0

    def get_transaction_depth(self) -> int:
        """Get the current transaction nesting depth."""
        return len(self._transaction_stack)


class LockManager:
    """
    Manager for database row locking to prevent race conditions.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def lock_for_update(
        self,
        model_class,
        id: Any,
        skip_locked: bool = False,
        nowait: bool = False
    ):
        """
        Lock a row for update to prevent race conditions.

        Args:
            model_class: SQLAlchemy model class
            id: ID of the row to lock
            skip_locked: Skip rows that are already locked
            nowait: Don't wait for lock, raise exception if locked

        Returns:
            Locked model instance or None if not found
        """
        try:
            query = select(model_class).where(model_class.id == id)

            if skip_locked:
                query = query.with_for_update(skip_locked=True)
            elif nowait:
                query = query.with_for_update(nowait=True)
            else:
                query = query.with_for_update()

            result = await self.db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error locking {model_class.__name__} with id {id}: {str(e)}")
            raise DatabaseError(f"Failed to lock {model_class.__name__}: {str(e)}")

    async def lock_multiple_for_update(
        self,
        model_class,
        ids: List[Any],
        skip_locked: bool = False,
        nowait: bool = False
    ):
        """
        Lock multiple rows for update.

        Args:
            model_class: SQLAlchemy model class
            ids: List of IDs to lock
            skip_locked: Skip rows that are already locked
            nowait: Don't wait for lock, raise exception if locked

        Returns:
            List of locked model instances
        """
        try:
            query = select(model_class).where(model_class.id.in_(ids))

            if skip_locked:
                query = query.with_for_update(skip_locked=True)
            elif nowait:
                query = query.with_for_update(nowait=True)
            else:
                query = query.with_for_update()

            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error locking multiple {model_class.__name__} with ids {ids}: {str(e)}")
            raise DatabaseError(f"Failed to lock multiple {model_class.__name__}: {str(e)}")


class BulkOperationManager:
    """
    Manager for bulk database operations within transactions.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def bulk_create(
        self,
        model_class,
        objects: List[Dict[str, Any]],
        batch_size: int = 1000
    ) -> List[Any]:
        """
        Bulk create objects in batches.

        Args:
            model_class: SQLAlchemy model class
            objects: List of object data dictionaries
            batch_size: Number of objects to process per batch

        Returns:
            List of created objects
        """
        try:
            created_objects = []

            for i in range(0, len(objects), batch_size):
                batch = objects[i:i + batch_size]
                batch_objects = [model_class(**obj_data) for obj_data in batch]

                self.db.add_all(batch_objects)
                await self.db.flush()  # Flush to get IDs
                created_objects.extend(batch_objects)

            return created_objects
        except IntegrityError as e:
            await self.db.rollback()
            raise ConflictError(f"Bulk create failed due to constraint violation: {str(e)}")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error in bulk create: {str(e)}")
            raise DatabaseError(f"Bulk create failed: {str(e)}")

    async def bulk_update(
        self,
        model_class,
        updates: List[Dict[str, Any]],
        batch_size: int = 1000
    ) -> int:
        """
        Bulk update objects.

        Args:
            model_class: SQLAlchemy model class
            updates: List of update dictionaries with 'id' and update fields
            batch_size: Number of updates to process per batch

        Returns:
            Number of updated objects
        """
        try:
            updated_count = 0

            for i in range(0, len(updates), batch_size):
                batch = updates[i:i + batch_size]

                for update_data in batch:
                    obj_id = update_data.pop('id')
                    update_fields = update_data

                    stmt = update(model_class).where(
                        model_class.id == obj_id
                    ).values(**update_fields)

                    result = await self.db.execute(stmt)
                    updated_count += result.rowcount

            return updated_count
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error in bulk update: {str(e)}")
            raise DatabaseError(f"Bulk update failed: {str(e)}")

    async def bulk_delete(
        self,
        model_class,
        ids: List[Any],
        batch_size: int = 1000
    ) -> int:
        """
        Bulk delete objects.

        Args:
            model_class: SQLAlchemy model class
            ids: List of IDs to delete
            batch_size: Number of IDs to process per batch

        Returns:
            Number of deleted objects
        """
        try:
            deleted_count = 0

            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i + batch_size]

                stmt = delete(model_class).where(model_class.id.in_(batch_ids))
                result = await self.db.execute(stmt)
                deleted_count += result.rowcount

            return deleted_count
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error in bulk delete: {str(e)}")
            raise DatabaseError(f"Bulk delete failed: {str(e)}")


class TransactionalCRUDMixin:
    """
    Mixin class that adds transaction management capabilities to CRUD classes.
    """

    async def create_with_transaction(
        self,
        db: AsyncSession,
        *,
        obj_in: Any,
        created_by: str = "system"
    ) -> Any:
        """
        Create an object within a transaction.

        Args:
            db: Database session
            obj_in: Object data to create
            created_by: User creating the object

        Returns:
            Created object
        """
        async with TransactionManager(db).transaction():
            return await self.create(db, obj_in=obj_in, created_by=created_by)

    async def update_with_transaction(
        self,
        db: AsyncSession,
        *,
        db_obj: Any,
        obj_in: Any
    ) -> Any:
        """
        Update an object within a transaction.

        Args:
            db: Database session
            db_obj: Existing object to update
            obj_in: Update data

        Returns:
            Updated object
        """
        async with TransactionManager(db).transaction():
            return await self.update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete_with_transaction(
        self,
        db: AsyncSession,
        *,
        id: Any
    ) -> Any:
        """
        Delete an object within a transaction.

        Args:
            db: Database session
            id: ID of object to delete

        Returns:
            Deleted object
        """
        async with TransactionManager(db).transaction():
            return await self.remove(db, id=id)

    async def create_multiple_with_transaction(
        self,
        db: AsyncSession,
        *,
        objects: List[Any],
        created_by: str = "system"
    ) -> List[Any]:
        """
        Create multiple objects within a single transaction.

        Args:
            db: Database session
            objects: List of object data to create
            created_by: User creating the objects

        Returns:
            List of created objects
        """
        async with TransactionManager(db).transaction():
            created_objects = []
            for obj_in in objects:
                obj = await self.create(db, obj_in=obj_in, created_by=created_by)
                created_objects.append(obj)
            return created_objects

    async def update_multiple_with_transaction(
        self,
        db: AsyncSession,
        *,
        updates: List[Dict[str, Any]]
    ) -> List[Any]:
        """
        Update multiple objects within a single transaction.

        Args:
            db: Database session
            updates: List of update dictionaries with 'id' and update fields

        Returns:
            List of updated objects
        """
        async with TransactionManager(db).transaction():
            updated_objects = []
            for update_data in updates:
                obj_id = update_data.pop('id')
                db_obj = await self.get(db, id=obj_id)
                if db_obj:
                    updated_obj = await self.update(db, db_obj=db_obj, obj_in=update_data)
                    updated_objects.append(updated_obj)
            return updated_objects

    async def delete_multiple_with_transaction(
        self,
        db: AsyncSession,
        *,
        ids: List[Any]
    ) -> List[Any]:
        """
        Delete multiple objects within a single transaction.

        Args:
            db: Database session
            ids: List of IDs to delete

        Returns:
            List of deleted objects
        """
        async with TransactionManager(db).transaction():
            deleted_objects = []
            for obj_id in ids:
                deleted_obj = await self.remove(db, id=obj_id)
                deleted_objects.append(deleted_obj)
            return deleted_objects

    async def execute_with_retry(
        self,
        operation: Callable,
        max_retries: int = 3,
        retry_delay: float = 0.1
    ) -> Any:
        """
        Execute an operation with retry logic for transient failures.

        Args:
            operation: Async function to execute
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Returns:
            Result of the operation
        """
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return await operation()
            except (IntegrityError, SQLAlchemyError) as e:
                last_exception = e
                if attempt < max_retries:
                    logger.warning(f"Operation failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"Operation failed after {max_retries + 1} attempts: {str(e)}")
                    raise DatabaseError(f"Operation failed after {max_retries + 1} attempts: {str(e)}")
            except Exception as e:
                # Non-retryable exception
                raise e

        raise last_exception


# Utility functions for common transaction patterns
async def execute_in_transaction(
    db: AsyncSession,
    operation: Callable,
    nested: bool = False
) -> Any:
    """
    Execute an operation within a transaction.

    Args:
        db: Database session
        operation: Async function to execute
        nested: Whether to use nested transaction

    Returns:
        Result of the operation
    """
    async with TransactionManager(db).transaction(nested=nested):
        return await operation()


async def execute_with_lock(
    db: AsyncSession,
    model_class,
    id: Any,
    operation: Callable,
    skip_locked: bool = False,
    nowait: bool = False
) -> Any:
    """
    Execute an operation with row locking.

    Args:
        db: Database session
        model_class: SQLAlchemy model class
        id: ID of the row to lock
        operation: Async function to execute
        skip_locked: Skip rows that are already locked
        nowait: Don't wait for lock

    Returns:
        Result of the operation
    """
    lock_manager = LockManager(db)
    locked_obj = await lock_manager.lock_for_update(
        model_class, id, skip_locked=skip_locked, nowait=nowait
    )

    if locked_obj is None:
        raise DatabaseError(f"Could not lock {model_class.__name__} with id {id}")

    return await operation(locked_obj)


async def bulk_operation_in_transaction(
    db: AsyncSession,
    operation: Callable,
    batch_size: int = 1000
) -> Any:
    """
    Execute a bulk operation within a transaction.

    Args:
        db: Database session
        operation: Async function that performs bulk operation
        batch_size: Batch size for the operation

    Returns:
        Result of the operation
    """
    async with TransactionManager(db).transaction():
        bulk_manager = BulkOperationManager(db)
        return await operation(bulk_manager)


# Context managers for common patterns
@asynccontextmanager
async def transaction_context(db: AsyncSession, nested: bool = False):
    """Context manager for database transactions."""
    async with TransactionManager(db).transaction(nested=nested) as tm:
        yield tm


@asynccontextmanager
async def lock_context(
    db: AsyncSession,
    model_class,
    id: Any,
    skip_locked: bool = False,
    nowait: bool = False
):
    """Context manager for row locking."""
    lock_manager = LockManager(db)
    locked_obj = await lock_manager.lock_for_update(
        model_class, id, skip_locked=skip_locked, nowait=nowait
    )

    if locked_obj is None:
        raise DatabaseError(f"Could not lock {model_class.__name__} with id {id}")

    try:
        yield locked_obj
    finally:
        # Lock is automatically released when transaction ends
        pass
