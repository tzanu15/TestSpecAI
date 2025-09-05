"""
CRUD operations for Requirement entity.
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.crud.advanced_queries import AdvancedCRUDMixin
from app.crud.transaction_manager import TransactionalCRUDMixin
from app.models.requirement import Requirement
from app.models.category import RequirementCategory
from app.schemas.requirement import RequirementCreate, RequirementUpdate
from app.utils.exceptions import NotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)


class CRUDRequirement(CRUDBase[Requirement, RequirementCreate, RequirementUpdate], AdvancedCRUDMixin, TransactionalCRUDMixin):
    """
    CRUD operations for Requirement entity.

    Extends BaseCRUD with requirement-specific operations.
    """

    async def get_by_category(
        self,
        db: AsyncSession,
        *,
        category_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Requirement]:
        """
        Get requirements by category ID.

        Args:
            db: Database session
            category_id: Category ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of requirements in the specified category
        """
        try:
            result = await db.execute(
                select(Requirement)
                .where(
                    and_(
                        Requirement.category_id == category_id,
                        Requirement.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(Requirement.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting requirements by category {category_id}: {str(e)}")
            raise

    async def search_by_title(
        self,
        db: AsyncSession,
        *,
        title: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Requirement]:
        """
        Search requirements by title (case-insensitive partial match).

        Args:
            db: Database session
            title: Title to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching requirements
        """
        try:
            result = await db.execute(
                select(Requirement)
                .where(
                    and_(
                        Requirement.title.ilike(f"%{title}%"),
                        Requirement.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(Requirement.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching requirements by title '{title}': {str(e)}")
            raise

    async def search_by_description(
        self,
        db: AsyncSession,
        *,
        description: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Requirement]:
        """
        Search requirements by description (case-insensitive partial match).

        Args:
            db: Database session
            description: Description to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching requirements
        """
        try:
            result = await db.execute(
                select(Requirement)
                .where(
                    and_(
                        Requirement.description.ilike(f"%{description}%"),
                        Requirement.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(Requirement.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching requirements by description: {str(e)}")
            raise

    async def get_by_source(
        self,
        db: AsyncSession,
        *,
        source: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Requirement]:
        """
        Get requirements by source.

        Args:
            db: Database session
            source: Source to filter by (e.g., 'manual', 'document')
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of requirements from the specified source
        """
        try:
            result = await db.execute(
                select(Requirement)
                .where(
                    and_(
                        Requirement.source == source,
                        Requirement.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(Requirement.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting requirements by source '{source}': {str(e)}")
            raise

    async def get_with_category(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[Requirement]:
        """
        Get requirement with category relationship loaded.

        Args:
            db: Database session
            id: Requirement ID

        Returns:
            Requirement with category loaded or None if not found
        """
        try:
            result = await db.execute(
                select(Requirement)
                .options(selectinload(Requirement.category))
                .where(
                    and_(
                        Requirement.id == id,
                        Requirement.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting requirement with category {id}: {str(e)}")
            raise

    async def get_with_test_specifications(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[Requirement]:
        """
        Get requirement with test specifications relationship loaded.

        Args:
            db: Database session
            id: Requirement ID

        Returns:
            Requirement with test specifications loaded or None if not found
        """
        try:
            result = await db.execute(
                select(Requirement)
                .options(selectinload(Requirement.test_specifications))
                .where(
                    and_(
                        Requirement.id == id,
                        Requirement.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting requirement with test specifications {id}: {str(e)}")
            raise

    async def get_with_all_relationships(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[Requirement]:
        """
        Get requirement with all relationships loaded.

        Args:
            db: Database session
            id: Requirement ID

        Returns:
            Requirement with all relationships loaded or None if not found
        """
        try:
            result = await db.execute(
                select(Requirement)
                .options(
                    selectinload(Requirement.category),
                    selectinload(Requirement.test_specifications)
                )
                .where(
                    and_(
                        Requirement.id == id,
                        Requirement.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting requirement with all relationships {id}: {str(e)}")
            raise

    async def count_by_category(
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
                select(func.count(Requirement.id))
                .where(
                    and_(
                        Requirement.category_id == category_id,
                        Requirement.is_active == True
                    )
                )
            )
            return result.scalar()
        except Exception as e:
            logger.error(f"Error counting requirements by category {category_id}: {str(e)}")
            raise

    async def count_by_source(
        self,
        db: AsyncSession,
        *,
        source: str
    ) -> int:
        """
        Count requirements by source.

        Args:
            db: Database session
            source: Source to count

        Returns:
            Number of requirements from the source
        """
        try:
            result = await db.execute(
                select(func.count(Requirement.id))
                .where(
                    and_(
                        Requirement.source == source,
                        Requirement.is_active == True
                    )
                )
            )
            return result.scalar()
        except Exception as e:
            logger.error(f"Error counting requirements by source '{source}': {str(e)}")
            raise

    async def get_requirements_without_test_specs(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Requirement]:
        """
        Get requirements that are not associated with any test specifications.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of requirements without test specifications
        """
        try:
            # Subquery to find requirements with test specifications
            subquery = select(Requirement.id).join(
                Requirement.test_specifications
            ).where(Requirement.is_active == True).distinct()

            result = await db.execute(
                select(Requirement)
                .where(
                    and_(
                        Requirement.id.notin_(subquery),
                        Requirement.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(Requirement.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting requirements without test specs: {str(e)}")
            raise

    async def validate_category_exists(
        self,
        db: AsyncSession,
        *,
        category_id: str
    ) -> bool:
        """
        Validate that a category exists and is active.

        Args:
            db: Database session
            category_id: Category ID to validate

        Returns:
            True if category exists and is active, False otherwise
        """
        try:
            result = await db.execute(
                select(func.count(RequirementCategory.id))
                .where(
                    and_(
                        RequirementCategory.id == category_id,
                        RequirementCategory.is_active == True
                    )
                )
            )
            return result.scalar() > 0
        except Exception as e:
            logger.error(f"Error validating category {category_id}: {str(e)}")
            raise

    async def create_with_validation(
        self,
        db: AsyncSession,
        *,
        obj_in: RequirementCreate
    ) -> Requirement:
        """
        Create a requirement with validation.

        Args:
            db: Database session
            obj_in: Requirement data to create

        Returns:
            Created requirement

        Raises:
            ValidationError: If validation fails
        """
        # Validate category exists
        if not await self.validate_category_exists(db, category_id=str(obj_in.category_id)):
            raise ValidationError(f"Category with ID {obj_in.category_id} does not exist")

        # Create the requirement
        return await self.create(db, obj_in=obj_in)


# Create instance
requirement = CRUDRequirement(Requirement)
