"""
CRUD operations for Category entities.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.crud.advanced_queries import AdvancedCRUDMixin
from app.crud.transaction_manager import TransactionalCRUDMixin
from app.models.category import RequirementCategory, ParameterCategory, CommandCategory
from app.schemas.category import (
    RequirementCategoryCreate, RequirementCategoryUpdate,
    ParameterCategoryCreate, ParameterCategoryUpdate,
    CommandCategoryCreate, CommandCategoryUpdate
)
from app.utils.exceptions import NotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)


class CRUDRequirementCategory(CRUDBase[RequirementCategory, RequirementCategoryCreate, RequirementCategoryUpdate], AdvancedCRUDMixin, TransactionalCRUDMixin):
    """
    CRUD operations for RequirementCategory entity.
    """

    async def get_by_name(
        self,
        db: AsyncSession,
        *,
        name: str
    ) -> Optional[RequirementCategory]:
        """
        Get requirement category by name.

        Args:
            db: Database session
            name: Category name to search for

        Returns:
            Requirement category with the specified name or None if not found
        """
        try:
            result = await db.execute(
                select(RequirementCategory)
                .where(
                    and_(
                        RequirementCategory.name == name,
                        RequirementCategory.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting requirement category by name '{name}': {str(e)}")
            raise

    async def get_with_requirements_count(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[RequirementCategory]:
        """
        Get requirement categories with requirements count.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of requirement categories with requirements count
        """
        try:
            result = await db.execute(
                select(RequirementCategory)
                .where(RequirementCategory.is_active == True)
                .offset(skip)
                .limit(limit)
                .order_by(RequirementCategory.name)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting requirement categories with count: {str(e)}")
            raise

    async def search_by_name(
        self,
        db: AsyncSession,
        *,
        name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[RequirementCategory]:
        """
        Search requirement categories by name (case-insensitive partial match).

        Args:
            db: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching requirement categories
        """
        try:
            result = await db.execute(
                select(RequirementCategory)
                .where(
                    and_(
                        RequirementCategory.name.ilike(f"%{name}%"),
                        RequirementCategory.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(RequirementCategory.name)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching requirement categories by name '{name}': {str(e)}")
            raise

    async def validate_name_unique(
        self,
        db: AsyncSession,
        *,
        name: str,
        exclude_id: Optional[str] = None
    ) -> bool:
        """
        Validate that a category name is unique.

        Args:
            db: Database session
            name: Category name to validate
            exclude_id: ID to exclude from validation (for updates)

        Returns:
            True if name is unique, False otherwise
        """
        try:
            query = select(func.count(RequirementCategory.id)).where(
                and_(
                    RequirementCategory.name == name,
                    RequirementCategory.is_active == True
                )
            )

            if exclude_id:
                query = query.where(RequirementCategory.id != exclude_id)

            result = await db.execute(query)
            return result.scalar() == 0
        except Exception as e:
            logger.error(f"Error validating requirement category name uniqueness '{name}': {str(e)}")
            raise

    async def create_with_validation(
        self,
        db: AsyncSession,
        *,
        obj_in: RequirementCategoryCreate
    ) -> RequirementCategory:
        """
        Create a requirement category with validation.

        Args:
            db: Database session
            obj_in: Category data to create

        Returns:
            Created requirement category

        Raises:
            ValidationError: If validation fails
        """
        # Validate name uniqueness
        if not await self.validate_name_unique(db, name=obj_in.name):
            raise ValidationError(f"Requirement category with name '{obj_in.name}' already exists")

        # Create the category
        return await self.create(db, obj_in=obj_in)

    async def update_with_validation(
        self,
        db: AsyncSession,
        *,
        db_obj: RequirementCategory,
        obj_in: RequirementCategoryUpdate
    ) -> RequirementCategory:
        """
        Update a requirement category with validation.

        Args:
            db: Database session
            db_obj: Existing category object
            obj_in: Update data

        Returns:
            Updated requirement category

        Raises:
            ValidationError: If validation fails
        """
        # Validate name uniqueness if name is being updated
        if obj_in.name and obj_in.name != db_obj.name:
            if not await self.validate_name_unique(db, name=obj_in.name, exclude_id=str(db_obj.id)):
                raise ValidationError(f"Requirement category with name '{obj_in.name}' already exists")

        # Update the category
        return await self.update(db, db_obj=db_obj, obj_in=obj_in)


class CRUDParameterCategory(CRUDBase[ParameterCategory, ParameterCategoryCreate, ParameterCategoryUpdate], AdvancedCRUDMixin, TransactionalCRUDMixin):
    """
    CRUD operations for ParameterCategory entity.
    """

    async def get_by_name(
        self,
        db: AsyncSession,
        *,
        name: str
    ) -> Optional[ParameterCategory]:
        """
        Get parameter category by name.

        Args:
            db: Database session
            name: Category name to search for

        Returns:
            Parameter category with the specified name or None if not found
        """
        try:
            result = await db.execute(
                select(ParameterCategory)
                .where(
                    and_(
                        ParameterCategory.name == name,
                        ParameterCategory.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting parameter category by name '{name}': {str(e)}")
            raise

    async def get_with_parameters_count(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[ParameterCategory]:
        """
        Get parameter categories with parameters count.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of parameter categories with parameters count
        """
        try:
            result = await db.execute(
                select(ParameterCategory)
                .where(ParameterCategory.is_active == True)
                .offset(skip)
                .limit(limit)
                .order_by(ParameterCategory.name)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting parameter categories with count: {str(e)}")
            raise

    async def search_by_name(
        self,
        db: AsyncSession,
        *,
        name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ParameterCategory]:
        """
        Search parameter categories by name (case-insensitive partial match).

        Args:
            db: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching parameter categories
        """
        try:
            result = await db.execute(
                select(ParameterCategory)
                .where(
                    and_(
                        ParameterCategory.name.ilike(f"%{name}%"),
                        ParameterCategory.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(ParameterCategory.name)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching parameter categories by name '{name}': {str(e)}")
            raise

    async def validate_name_unique(
        self,
        db: AsyncSession,
        *,
        name: str,
        exclude_id: Optional[str] = None
    ) -> bool:
        """
        Validate that a category name is unique.

        Args:
            db: Database session
            name: Category name to validate
            exclude_id: ID to exclude from validation (for updates)

        Returns:
            True if name is unique, False otherwise
        """
        try:
            query = select(func.count(ParameterCategory.id)).where(
                and_(
                    ParameterCategory.name == name,
                    ParameterCategory.is_active == True
                )
            )

            if exclude_id:
                query = query.where(ParameterCategory.id != exclude_id)

            result = await db.execute(query)
            return result.scalar() == 0
        except Exception as e:
            logger.error(f"Error validating parameter category name uniqueness '{name}': {str(e)}")
            raise

    async def create_with_validation(
        self,
        db: AsyncSession,
        *,
        obj_in: ParameterCategoryCreate
    ) -> ParameterCategory:
        """
        Create a parameter category with validation.

        Args:
            db: Database session
            obj_in: Category data to create

        Returns:
            Created parameter category

        Raises:
            ValidationError: If validation fails
        """
        # Validate name uniqueness
        if not await self.validate_name_unique(db, name=obj_in.name):
            raise ValidationError(f"Parameter category with name '{obj_in.name}' already exists")

        # Create the category
        return await self.create(db, obj_in=obj_in)

    async def update_with_validation(
        self,
        db: AsyncSession,
        *,
        db_obj: ParameterCategory,
        obj_in: ParameterCategoryUpdate
    ) -> ParameterCategory:
        """
        Update a parameter category with validation.

        Args:
            db: Database session
            db_obj: Existing category object
            obj_in: Update data

        Returns:
            Updated parameter category

        Raises:
            ValidationError: If validation fails
        """
        # Validate name uniqueness if name is being updated
        if obj_in.name and obj_in.name != db_obj.name:
            if not await self.validate_name_unique(db, name=obj_in.name, exclude_id=str(db_obj.id)):
                raise ValidationError(f"Parameter category with name '{obj_in.name}' already exists")

        # Update the category
        return await self.update(db, db_obj=db_obj, obj_in=obj_in)


class CRUDCommandCategory(CRUDBase[CommandCategory, CommandCategoryCreate, CommandCategoryUpdate], AdvancedCRUDMixin, TransactionalCRUDMixin):
    """
    CRUD operations for CommandCategory entity.
    """

    async def get_by_name(
        self,
        db: AsyncSession,
        *,
        name: str
    ) -> Optional[CommandCategory]:
        """
        Get command category by name.

        Args:
            db: Database session
            name: Category name to search for

        Returns:
            Command category with the specified name or None if not found
        """
        try:
            result = await db.execute(
                select(CommandCategory)
                .where(
                    and_(
                        CommandCategory.name == name,
                        CommandCategory.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting command category by name '{name}': {str(e)}")
            raise

    async def get_with_commands_count(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[CommandCategory]:
        """
        Get command categories with commands count.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of command categories with commands count
        """
        try:
            result = await db.execute(
                select(CommandCategory)
                .where(CommandCategory.is_active == True)
                .offset(skip)
                .limit(limit)
                .order_by(CommandCategory.name)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting command categories with count: {str(e)}")
            raise

    async def search_by_name(
        self,
        db: AsyncSession,
        *,
        name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CommandCategory]:
        """
        Search command categories by name (case-insensitive partial match).

        Args:
            db: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching command categories
        """
        try:
            result = await db.execute(
                select(CommandCategory)
                .where(
                    and_(
                        CommandCategory.name.ilike(f"%{name}%"),
                        CommandCategory.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(CommandCategory.name)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching command categories by name '{name}': {str(e)}")
            raise

    async def validate_name_unique(
        self,
        db: AsyncSession,
        *,
        name: str,
        exclude_id: Optional[str] = None
    ) -> bool:
        """
        Validate that a category name is unique.

        Args:
            db: Database session
            name: Category name to validate
            exclude_id: ID to exclude from validation (for updates)

        Returns:
            True if name is unique, False otherwise
        """
        try:
            query = select(func.count(CommandCategory.id)).where(
                and_(
                    CommandCategory.name == name,
                    CommandCategory.is_active == True
                )
            )

            if exclude_id:
                query = query.where(CommandCategory.id != exclude_id)

            result = await db.execute(query)
            return result.scalar() == 0
        except Exception as e:
            logger.error(f"Error validating command category name uniqueness '{name}': {str(e)}")
            raise

    async def create_with_validation(
        self,
        db: AsyncSession,
        *,
        obj_in: CommandCategoryCreate
    ) -> CommandCategory:
        """
        Create a command category with validation.

        Args:
            db: Database session
            obj_in: Category data to create

        Returns:
            Created command category

        Raises:
            ValidationError: If validation fails
        """
        # Validate name uniqueness
        if not await self.validate_name_unique(db, name=obj_in.name):
            raise ValidationError(f"Command category with name '{obj_in.name}' already exists")

        # Create the category
        return await self.create(db, obj_in=obj_in)

    async def update_with_validation(
        self,
        db: AsyncSession,
        *,
        db_obj: CommandCategory,
        obj_in: CommandCategoryUpdate
    ) -> CommandCategory:
        """
        Update a command category with validation.

        Args:
            db: Database session
            db_obj: Existing category object
            obj_in: Update data

        Returns:
            Updated command category

        Raises:
            ValidationError: If validation fails
        """
        # Validate name uniqueness if name is being updated
        if obj_in.name and obj_in.name != db_obj.name:
            if not await self.validate_name_unique(db, name=obj_in.name, exclude_id=str(db_obj.id)):
                raise ValidationError(f"Command category with name '{obj_in.name}' already exists")

        # Update the category
        return await self.update(db, db_obj=db_obj, obj_in=obj_in)

    async def is_category_in_use(
        self,
        db: AsyncSession,
        *,
        category_id: str
    ) -> bool:
        """
        Check if a command category is in use by any commands.

        Args:
            db: Database session
            category_id: Category ID to check

        Returns:
            True if category is in use, False otherwise
        """
        try:
            from app.models.command import GenericCommand

            result = await db.execute(
                select(func.count(GenericCommand.id))
                .where(
                    and_(
                        GenericCommand.category_id == category_id,
                        GenericCommand.is_active == True
                    )
                )
            )
            return result.scalar() > 0
        except Exception as e:
            logger.error(f"Error checking if command category {category_id} is in use: {str(e)}")
            raise

    async def get_category_usage_count(
        self,
        db: AsyncSession,
        *,
        category_id: str
    ) -> int:
        """
        Get the number of commands using this category.

        Args:
            db: Database session
            category_id: Category ID to check

        Returns:
            Number of commands using this category
        """
        try:
            from app.models.command import GenericCommand

            result = await db.execute(
                select(func.count(GenericCommand.id))
                .where(
                    and_(
                        GenericCommand.category_id == category_id,
                        GenericCommand.is_active == True
                    )
                )
            )
            return result.scalar()
        except Exception as e:
            logger.error(f"Error getting usage count for command category {category_id}: {str(e)}")
            raise

    async def remove_with_validation(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> CommandCategory:
        """
        Remove a command category with validation to prevent deletion of categories with assigned commands.

        Args:
            db: Database session
            id: Category ID to remove

        Returns:
            Removed category

        Raises:
            NotFoundError: If category not found
            ConflictError: If category has assigned commands
        """
        try:
            # Check if category exists
            category = await self.get(db, id=id)
            if not category:
                raise NotFoundError(f"Command category with ID {id} not found")

            # Check if category is in use
            if await self.is_category_in_use(db, category_id=id):
                usage_count = await self.get_category_usage_count(db, category_id=id)
                raise ConflictError(
                    f"Cannot delete command category. It is currently used by {usage_count} command(s). "
                    f"Please reassign or delete the commands first."
                )

            # Remove the category
            return await self.remove(db, id=id)

        except (NotFoundError, ConflictError):
            raise
        except Exception as e:
            logger.error(f"Error removing command category {id}: {str(e)}")
            raise


# Create instances
requirement_category = CRUDRequirementCategory(RequirementCategory)
parameter_category = CRUDParameterCategory(ParameterCategory)
command_category = CRUDCommandCategory(CommandCategory)
