"""
CRUD operations for Category entities (RequirementCategory, ParameterCategory, CommandCategory).
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
    RequirementCategoryCreate,
    RequirementCategoryUpdate,
    ParameterCategoryCreate,
    ParameterCategoryUpdate,
    CommandCategoryCreate,
    CommandCategoryUpdate
)
from app.utils.exceptions import NotFoundError, ValidationError, ConflictError
import logging

logger = logging.getLogger(__name__)


class CRUDRequirementCategory(CRUDBase[RequirementCategory, RequirementCategoryCreate, RequirementCategoryUpdate], AdvancedCRUDMixin, TransactionalCRUDMixin):
    """
    CRUD operations for RequirementCategory entity.

    Extends BaseCRUD with requirement category-specific operations.
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
            Requirement category or None if not found
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
                .order_by(RequirementCategory.name.asc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching requirement categories by name '{name}': {str(e)}")
            raise

    async def get_with_requirements(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[RequirementCategory]:
        """
        Get requirement category with requirements relationship loaded.

        Args:
            db: Database session
            id: Category ID

        Returns:
            Requirement category with requirements loaded or None if not found
        """
        try:
            result = await db.execute(
                select(RequirementCategory)
                .options(selectinload(RequirementCategory.requirements))
                .where(
                    and_(
                        RequirementCategory.id == id,
                        RequirementCategory.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting requirement category with requirements {id}: {str(e)}")
            raise

    async def count_requirements(
        self,
        db: AsyncSession,
        *,
        category_id: str
    ) -> int:
        """
        Count requirements in a category.

        Args:
            db: Database session
            category_id: Category ID to count

        Returns:
            Number of requirements in the category
        """
        try:
            result = await db.execute(
                select(func.count(RequirementCategory.requirements))
                .where(
                    and_(
                        RequirementCategory.id == category_id,
                        RequirementCategory.is_active == True
                    )
                )
            )
            return result.scalar()
        except Exception as e:
            logger.error(f"Error counting requirements for category {category_id}: {str(e)}")
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
            ConflictError: If category name already exists
        """
        # Check if category name already exists
        existing = await self.get_by_name(db, name=obj_in.name)
        if existing:
            raise ConflictError(f"Requirement category with name '{obj_in.name}' already exists")

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
            db_obj: Existing category
            obj_in: Update data

        Returns:
            Updated requirement category

        Raises:
            ConflictError: If new category name already exists
        """
        # Check if new name conflicts with existing category
        if obj_in.name and obj_in.name != db_obj.name:
            existing = await self.get_by_name(db, name=obj_in.name)
            if existing and existing.id != db_obj.id:
                raise ConflictError(f"Requirement category with name '{obj_in.name}' already exists")

        return await self.update(db, db_obj=db_obj, obj_in=obj_in)


class CRUDParameterCategory(CRUDBase[ParameterCategory, ParameterCategoryCreate, ParameterCategoryUpdate], AdvancedCRUDMixin, TransactionalCRUDMixin):
    """
    CRUD operations for ParameterCategory entity.

    Extends BaseCRUD with parameter category-specific operations.
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
            Parameter category or None if not found
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
                .order_by(ParameterCategory.name.asc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching parameter categories by name '{name}': {str(e)}")
            raise

    async def get_with_parameters(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[ParameterCategory]:
        """
        Get parameter category with parameters relationship loaded.

        Args:
            db: Database session
            id: Category ID

        Returns:
            Parameter category with parameters loaded or None if not found
        """
        try:
            result = await db.execute(
                select(ParameterCategory)
                .options(selectinload(ParameterCategory.parameters))
                .where(
                    and_(
                        ParameterCategory.id == id,
                        ParameterCategory.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting parameter category with parameters {id}: {str(e)}")
            raise

    async def count_parameters(
        self,
        db: AsyncSession,
        *,
        category_id: str
    ) -> int:
        """
        Count parameters in a category.

        Args:
            db: Database session
            category_id: Category ID to count

        Returns:
            Number of parameters in the category
        """
        try:
            result = await db.execute(
                select(func.count(ParameterCategory.parameters))
                .where(
                    and_(
                        ParameterCategory.id == category_id,
                        ParameterCategory.is_active == True
                    )
                )
            )
            return result.scalar()
        except Exception as e:
            logger.error(f"Error counting parameters for category {category_id}: {str(e)}")
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
            ConflictError: If category name already exists
        """
        # Check if category name already exists
        existing = await self.get_by_name(db, name=obj_in.name)
        if existing:
            raise ConflictError(f"Parameter category with name '{obj_in.name}' already exists")

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
            db_obj: Existing category
            obj_in: Update data

        Returns:
            Updated parameter category

        Raises:
            ConflictError: If new category name already exists
        """
        # Check if new name conflicts with existing category
        if obj_in.name and obj_in.name != db_obj.name:
            existing = await self.get_by_name(db, name=obj_in.name)
            if existing and existing.id != db_obj.id:
                raise ConflictError(f"Parameter category with name '{obj_in.name}' already exists")

        return await self.update(db, db_obj=db_obj, obj_in=obj_in)


class CRUDCommandCategory(CRUDBase[CommandCategory, CommandCategoryCreate, CommandCategoryUpdate], AdvancedCRUDMixin, TransactionalCRUDMixin):
    """
    CRUD operations for CommandCategory entity.

    Extends BaseCRUD with command category-specific operations.
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
            Command category or None if not found
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
                .order_by(CommandCategory.name.asc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching command categories by name '{name}': {str(e)}")
            raise

    async def get_with_commands(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[CommandCategory]:
        """
        Get command category with commands relationship loaded.

        Args:
            db: Database session
            id: Category ID

        Returns:
            Command category with commands loaded or None if not found
        """
        try:
            result = await db.execute(
                select(CommandCategory)
                .options(selectinload(CommandCategory.commands))
                .where(
                    and_(
                        CommandCategory.id == id,
                        CommandCategory.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting command category with commands {id}: {str(e)}")
            raise

    async def count_commands(
        self,
        db: AsyncSession,
        *,
        category_id: str
    ) -> int:
        """
        Count commands in a category.

        Args:
            db: Database session
            category_id: Category ID to count

        Returns:
            Number of commands in the category
        """
        try:
            result = await db.execute(
                select(func.count(CommandCategory.commands))
                .where(
                    and_(
                        CommandCategory.id == category_id,
                        CommandCategory.is_active == True
                    )
                )
            )
            return result.scalar()
        except Exception as e:
            logger.error(f"Error counting commands for category {category_id}: {str(e)}")
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
            ConflictError: If category name already exists
        """
        # Check if category name already exists
        existing = await self.get_by_name(db, name=obj_in.name)
        if existing:
            raise ConflictError(f"Command category with name '{obj_in.name}' already exists")

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
            db_obj: Existing category
            obj_in: Update data

        Returns:
            Updated command category

        Raises:
            ConflictError: If new category name already exists
        """
        # Check if new name conflicts with existing category
        if obj_in.name and obj_in.name != db_obj.name:
            existing = await self.get_by_name(db, name=obj_in.name)
            if existing and existing.id != db_obj.id:
                raise ConflictError(f"Command category with name '{obj_in.name}' already exists")

        return await self.update(db, db_obj=db_obj, obj_in=obj_in)


# Create instances
requirement_category = CRUDRequirementCategory(RequirementCategory)
parameter_category = CRUDParameterCategory(ParameterCategory)
command_category = CRUDCommandCategory(CommandCategory)
