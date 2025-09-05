"""
CRUD operations for Parameter and ParameterVariant entities.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.crud.advanced_queries import AdvancedCRUDMixin
from app.crud.transaction_manager import TransactionalCRUDMixin
from app.models.parameter import Parameter, ParameterVariant
from app.models.category import ParameterCategory
from app.schemas.parameter import (
    ParameterCreate,
    ParameterUpdate,
    ParameterVariantCreate,
    ParameterVariantUpdate
)
from app.utils.exceptions import NotFoundError, ValidationError, ConflictError
import logging

logger = logging.getLogger(__name__)


class CRUDParameter(CRUDBase[Parameter, ParameterCreate, ParameterUpdate], AdvancedCRUDMixin, TransactionalCRUDMixin):
    """
    CRUD operations for Parameter entity.

    Extends BaseCRUD with parameter-specific operations.
    """

    async def get_by_name(
        self,
        db: AsyncSession,
        *,
        name: str
    ) -> Optional[Parameter]:
        """
        Get parameter by name.

        Args:
            db: Database session
            name: Parameter name to search for

        Returns:
            Parameter or None if not found
        """
        try:
            result = await db.execute(
                select(Parameter)
                .where(
                    and_(
                        Parameter.name == name,
                        Parameter.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting parameter by name '{name}': {str(e)}")
            raise

    async def get_by_category(
        self,
        db: AsyncSession,
        *,
        category_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Parameter]:
        """
        Get parameters by category ID.

        Args:
            db: Database session
            category_id: Category ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of parameters in the specified category
        """
        try:
            result = await db.execute(
                select(Parameter)
                .where(
                    and_(
                        Parameter.category_id == category_id,
                        Parameter.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(Parameter.name.asc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting parameters by category {category_id}: {str(e)}")
            raise

    async def get_variant_parameters(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Parameter]:
        """
        Get parameters that have variants.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of parameters with variants
        """
        try:
            result = await db.execute(
                select(Parameter)
                .where(
                    and_(
                        Parameter.has_variants == True,
                        Parameter.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(Parameter.name.asc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting variant parameters: {str(e)}")
            raise

    async def get_simple_parameters(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Parameter]:
        """
        Get parameters that don't have variants (simple parameters).

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of simple parameters
        """
        try:
            result = await db.execute(
                select(Parameter)
                .where(
                    and_(
                        Parameter.has_variants == False,
                        Parameter.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(Parameter.name.asc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting simple parameters: {str(e)}")
            raise

    async def search_by_name(
        self,
        db: AsyncSession,
        *,
        name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Parameter]:
        """
        Search parameters by name (case-insensitive partial match).

        Args:
            db: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching parameters
        """
        try:
            result = await db.execute(
                select(Parameter)
                .where(
                    and_(
                        Parameter.name.ilike(f"%{name}%"),
                        Parameter.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(Parameter.name.asc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching parameters by name '{name}': {str(e)}")
            raise

    async def get_with_variants(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[Parameter]:
        """
        Get parameter with variants relationship loaded.

        Args:
            db: Database session
            id: Parameter ID

        Returns:
            Parameter with variants loaded or None if not found
        """
        try:
            result = await db.execute(
                select(Parameter)
                .options(selectinload(Parameter.variants))
                .where(
                    and_(
                        Parameter.id == id,
                        Parameter.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting parameter with variants {id}: {str(e)}")
            raise

    async def get_with_category(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[Parameter]:
        """
        Get parameter with category relationship loaded.

        Args:
            db: Database session
            id: Parameter ID

        Returns:
            Parameter with category loaded or None if not found
        """
        try:
            result = await db.execute(
                select(Parameter)
                .options(selectinload(Parameter.category))
                .where(
                    and_(
                        Parameter.id == id,
                        Parameter.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting parameter with category {id}: {str(e)}")
            raise

    async def get_with_all_relationships(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[Parameter]:
        """
        Get parameter with all relationships loaded.

        Args:
            db: Database session
            id: Parameter ID

        Returns:
            Parameter with all relationships loaded or None if not found
        """
        try:
            result = await db.execute(
                select(Parameter)
                .options(
                    selectinload(Parameter.category),
                    selectinload(Parameter.variants)
                )
                .where(
                    and_(
                        Parameter.id == id,
                        Parameter.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting parameter with all relationships {id}: {str(e)}")
            raise

    async def count_by_category(
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
                select(func.count(Parameter.id))
                .where(
                    and_(
                        Parameter.category_id == category_id,
                        Parameter.is_active == True
                    )
                )
            )
            return result.scalar()
        except Exception as e:
            logger.error(f"Error counting parameters by category {category_id}: {str(e)}")
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
                select(func.count(ParameterCategory.id))
                .where(
                    and_(
                        ParameterCategory.id == category_id,
                        ParameterCategory.is_active == True
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
        obj_in: ParameterCreate
    ) -> Parameter:
        """
        Create a parameter with validation.

        Args:
            db: Database session
            obj_in: Parameter data to create

        Returns:
            Created parameter

        Raises:
            ValidationError: If validation fails
            ConflictError: If parameter name already exists
        """
        # Check if parameter name already exists
        existing = await self.get_by_name(db, name=obj_in.name)
        if existing:
            raise ConflictError(f"Parameter with name '{obj_in.name}' already exists")

        # Validate category exists
        if not await self.validate_category_exists(db, category_id=str(obj_in.category_id)):
            raise ValidationError(f"Category with ID {obj_in.category_id} does not exist")

        # Create the parameter
        return await self.create(db, obj_in=obj_in)

    async def update_with_validation(
        self,
        db: AsyncSession,
        *,
        db_obj: Parameter,
        obj_in: ParameterUpdate
    ) -> Parameter:
        """
        Update a parameter with validation.

        Args:
            db: Database session
            db_obj: Existing parameter
            obj_in: Update data

        Returns:
            Updated parameter

        Raises:
            ConflictError: If new parameter name already exists
            ValidationError: If validation fails
        """
        # Check if new name conflicts with existing parameter
        if obj_in.name and obj_in.name != db_obj.name:
            existing = await self.get_by_name(db, name=obj_in.name)
            if existing and existing.id != db_obj.id:
                raise ConflictError(f"Parameter with name '{obj_in.name}' already exists")

        # Validate category exists if being changed
        if obj_in.category_id and str(obj_in.category_id) != str(db_obj.category_id):
            if not await self.validate_category_exists(db, category_id=str(obj_in.category_id)):
                raise ValidationError(f"Category with ID {obj_in.category_id} does not exist")

        return await self.update(db, db_obj=db_obj, obj_in=obj_in)


class CRUDParameterVariant(CRUDBase[ParameterVariant, ParameterVariantCreate, ParameterVariantUpdate], AdvancedCRUDMixin, TransactionalCRUDMixin):
    """
    CRUD operations for ParameterVariant entity.

    Extends BaseCRUD with parameter variant-specific operations.
    """

    async def get_by_parameter(
        self,
        db: AsyncSession,
        *,
        parameter_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ParameterVariant]:
        """
        Get parameter variants by parameter ID.

        Args:
            db: Database session
            parameter_id: Parameter ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of variants for the specified parameter
        """
        try:
            result = await db.execute(
                select(ParameterVariant)
                .where(
                    and_(
                        ParameterVariant.parameter_id == parameter_id,
                        ParameterVariant.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(ParameterVariant.manufacturer.asc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting parameter variants by parameter {parameter_id}: {str(e)}")
            raise

    async def get_by_manufacturer(
        self,
        db: AsyncSession,
        *,
        manufacturer: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[ParameterVariant]:
        """
        Get parameter variants by manufacturer.

        Args:
            db: Database session
            manufacturer: Manufacturer to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of variants for the specified manufacturer
        """
        try:
            result = await db.execute(
                select(ParameterVariant)
                .where(
                    and_(
                        ParameterVariant.manufacturer == manufacturer,
                        ParameterVariant.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(ParameterVariant.parameter_id)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting parameter variants by manufacturer '{manufacturer}': {str(e)}")
            raise

    async def get_by_parameter_and_manufacturer(
        self,
        db: AsyncSession,
        *,
        parameter_id: str,
        manufacturer: str
    ) -> Optional[ParameterVariant]:
        """
        Get parameter variant by parameter ID and manufacturer.

        Args:
            db: Database session
            parameter_id: Parameter ID
            manufacturer: Manufacturer name

        Returns:
            Parameter variant or None if not found
        """
        try:
            result = await db.execute(
                select(ParameterVariant)
                .where(
                    and_(
                        ParameterVariant.parameter_id == parameter_id,
                        ParameterVariant.manufacturer == manufacturer,
                        ParameterVariant.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting parameter variant by parameter {parameter_id} and manufacturer '{manufacturer}': {str(e)}")
            raise

    async def get_with_parameter(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[ParameterVariant]:
        """
        Get parameter variant with parameter relationship loaded.

        Args:
            db: Database session
            id: Variant ID

        Returns:
            Parameter variant with parameter loaded or None if not found
        """
        try:
            result = await db.execute(
                select(ParameterVariant)
                .options(selectinload(ParameterVariant.parameter))
                .where(
                    and_(
                        ParameterVariant.id == id,
                        ParameterVariant.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting parameter variant with parameter {id}: {str(e)}")
            raise

    async def count_by_parameter(
        self,
        db: AsyncSession,
        *,
        parameter_id: str
    ) -> int:
        """
        Count parameter variants for a parameter.

        Args:
            db: Database session
            parameter_id: Parameter ID to count

        Returns:
            Number of variants for the parameter
        """
        try:
            result = await db.execute(
                select(func.count(ParameterVariant.id))
                .where(
                    and_(
                        ParameterVariant.parameter_id == parameter_id,
                        ParameterVariant.is_active == True
                    )
                )
            )
            return result.scalar()
        except Exception as e:
            logger.error(f"Error counting parameter variants for parameter {parameter_id}: {str(e)}")
            raise

    async def count_by_manufacturer(
        self,
        db: AsyncSession,
        *,
        manufacturer: str
    ) -> int:
        """
        Count parameter variants for a manufacturer.

        Args:
            db: Database session
            manufacturer: Manufacturer to count

        Returns:
            Number of variants for the manufacturer
        """
        try:
            result = await db.execute(
                select(func.count(ParameterVariant.id))
                .where(
                    and_(
                        ParameterVariant.manufacturer == manufacturer,
                        ParameterVariant.is_active == True
                    )
                )
            )
            return result.scalar()
        except Exception as e:
            logger.error(f"Error counting parameter variants for manufacturer '{manufacturer}': {str(e)}")
            raise

    async def get_available_manufacturers(
        self,
        db: AsyncSession
    ) -> List[str]:
        """
        Get list of all available manufacturers.

        Args:
            db: Database session

        Returns:
            List of unique manufacturer names
        """
        try:
            result = await db.execute(
                select(ParameterVariant.manufacturer)
                .where(ParameterVariant.is_active == True)
                .distinct()
                .order_by(ParameterVariant.manufacturer.asc())
            )
            return [row[0] for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error getting available manufacturers: {str(e)}")
            raise

    async def validate_parameter_exists(
        self,
        db: AsyncSession,
        *,
        parameter_id: str
    ) -> bool:
        """
        Validate that a parameter exists and is active.

        Args:
            db: Database session
            parameter_id: Parameter ID to validate

        Returns:
            True if parameter exists and is active, False otherwise
        """
        try:
            result = await db.execute(
                select(func.count(Parameter.id))
                .where(
                    and_(
                        Parameter.id == parameter_id,
                        Parameter.is_active == True
                    )
                )
            )
            return result.scalar() > 0
        except Exception as e:
            logger.error(f"Error validating parameter {parameter_id}: {str(e)}")
            raise

    async def create_with_validation(
        self,
        db: AsyncSession,
        *,
        obj_in: ParameterVariantCreate
    ) -> ParameterVariant:
        """
        Create a parameter variant with validation.

        Args:
            db: Database session
            obj_in: Parameter variant data to create

        Returns:
            Created parameter variant

        Raises:
            ValidationError: If validation fails
            ConflictError: If variant already exists for parameter and manufacturer
        """
        # Validate parameter exists
        if not await self.validate_parameter_exists(db, parameter_id=str(obj_in.parameter_id)):
            raise ValidationError(f"Parameter with ID {obj_in.parameter_id} does not exist")

        # Check if variant already exists for this parameter and manufacturer
        existing = await self.get_by_parameter_and_manufacturer(
            db,
            parameter_id=str(obj_in.parameter_id),
            manufacturer=obj_in.manufacturer
        )
        if existing:
            raise ConflictError(f"Parameter variant for parameter {obj_in.parameter_id} and manufacturer '{obj_in.manufacturer}' already exists")

        # Create the variant
        return await self.create(db, obj_in=obj_in)

    async def update_with_validation(
        self,
        db: AsyncSession,
        *,
        db_obj: ParameterVariant,
        obj_in: ParameterVariantUpdate
    ) -> ParameterVariant:
        """
        Update a parameter variant with validation.

        Args:
            db: Database session
            db_obj: Existing parameter variant
            obj_in: Update data

        Returns:
            Updated parameter variant

        Raises:
            ConflictError: If new manufacturer conflicts with existing variant
            ValidationError: If validation fails
        """
        # Check if new manufacturer conflicts with existing variant for the same parameter
        if (obj_in.manufacturer and obj_in.manufacturer != db_obj.manufacturer and
            obj_in.parameter_id and str(obj_in.parameter_id) == str(db_obj.parameter_id)):
            existing = await self.get_by_parameter_and_manufacturer(
                db,
                parameter_id=str(obj_in.parameter_id),
                manufacturer=obj_in.manufacturer
            )
            if existing and existing.id != db_obj.id:
                raise ConflictError(f"Parameter variant for parameter {obj_in.parameter_id} and manufacturer '{obj_in.manufacturer}' already exists")

        # Validate parameter exists if being changed
        if obj_in.parameter_id and str(obj_in.parameter_id) != str(db_obj.parameter_id):
            if not await self.validate_parameter_exists(db, parameter_id=str(obj_in.parameter_id)):
                raise ValidationError(f"Parameter with ID {obj_in.parameter_id} does not exist")

        return await self.update(db, db_obj=db_obj, obj_in=obj_in)


# Create instances
parameter = CRUDParameter(Parameter)
parameter_variant = CRUDParameterVariant(ParameterVariant)
