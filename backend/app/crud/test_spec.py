"""
CRUD operations for TestSpecification and TestStep entities.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, delete
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.crud.advanced_queries import AdvancedCRUDMixin
from app.crud.transaction_manager import TransactionalCRUDMixin
from app.models.test_spec import TestSpecification, TestStep, FunctionalArea
from app.models.requirement import Requirement
from app.schemas.test_spec import TestSpecificationCreate, TestSpecificationUpdate, TestStepCreate, TestStepUpdate
from app.utils.exceptions import NotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)


class CRUDTestSpecification(CRUDBase[TestSpecification, TestSpecificationCreate, TestSpecificationUpdate], AdvancedCRUDMixin, TransactionalCRUDMixin):
    """
    CRUD operations for TestSpecification entity.

    Extends BaseCRUD with test specification-specific operations.
    """

    async def get_by_functional_area(
        self,
        db: AsyncSession,
        *,
        functional_area: FunctionalArea,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestSpecification]:
        """
        Get test specifications by functional area.

        Args:
            db: Database session
            functional_area: Functional area to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of test specifications in the specified functional area
        """
        try:
            result = await db.execute(
                select(TestSpecification)
                .where(
                    and_(
                        TestSpecification.functional_area == functional_area,
                        TestSpecification.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(TestSpecification.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting test specifications by functional area {functional_area}: {str(e)}")
            raise

    async def search_by_name(
        self,
        db: AsyncSession,
        *,
        name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestSpecification]:
        """
        Search test specifications by name (case-insensitive partial match).

        Args:
            db: Database session
            name: Name to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching test specifications
        """
        try:
            result = await db.execute(
                select(TestSpecification)
                .where(
                    and_(
                        TestSpecification.name.ilike(f"%{name}%"),
                        TestSpecification.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(TestSpecification.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching test specifications by name '{name}': {str(e)}")
            raise

    async def get_with_requirements(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[TestSpecification]:
        """
        Get test specification with requirements relationship loaded.

        Args:
            db: Database session
            id: Test specification ID

        Returns:
            Test specification with requirements loaded or None if not found
        """
        try:
            result = await db.execute(
                select(TestSpecification)
                .options(selectinload(TestSpecification.requirements))
                .where(
                    and_(
                        TestSpecification.id == id,
                        TestSpecification.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting test specification with requirements {id}: {str(e)}")
            raise

    async def get_with_test_steps(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[TestSpecification]:
        """
        Get test specification with test steps relationship loaded.

        Args:
            db: Database session
            id: Test specification ID

        Returns:
            Test specification with test steps loaded or None if not found
        """
        try:
            result = await db.execute(
                select(TestSpecification)
                .options(selectinload(TestSpecification.test_steps))
                .where(
                    and_(
                        TestSpecification.id == id,
                        TestSpecification.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting test specification with test steps {id}: {str(e)}")
            raise

    async def get_with_all_relationships(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[TestSpecification]:
        """
        Get test specification with all relationships loaded.

        Args:
            db: Database session
            id: Test specification ID

        Returns:
            Test specification with all relationships loaded or None if not found
        """
        try:
            result = await db.execute(
                select(TestSpecification)
                .options(
                    selectinload(TestSpecification.requirements),
                    selectinload(TestSpecification.test_steps)
                )
                .where(
                    and_(
                        TestSpecification.id == id,
                        TestSpecification.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting test specification with all relationships {id}: {str(e)}")
            raise

    async def count_by_functional_area(
        self,
        db: AsyncSession,
        *,
        functional_area: FunctionalArea
    ) -> int:
        """
        Count test specifications by functional area.

        Args:
            db: Database session
            functional_area: Functional area to count

        Returns:
            Number of test specifications in the functional area
        """
        try:
            result = await db.execute(
                select(func.count(TestSpecification.id))
                .where(
                    and_(
                        TestSpecification.functional_area == functional_area,
                        TestSpecification.is_active == True
                    )
                )
            )
            return result.scalar()
        except Exception as e:
            logger.error(f"Error counting test specifications by functional area {functional_area}: {str(e)}")
            raise

    async def get_test_specifications_without_requirements(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestSpecification]:
        """
        Get test specifications that are not associated with any requirements.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of test specifications without requirements
        """
        try:
            # Subquery to find test specifications with requirements
            subquery = select(TestSpecification.id).join(
                TestSpecification.requirements
            ).where(TestSpecification.is_active == True).distinct()

            result = await db.execute(
                select(TestSpecification)
                .where(
                    and_(
                        TestSpecification.id.notin_(subquery),
                        TestSpecification.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(TestSpecification.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting test specifications without requirements: {str(e)}")
            raise

    async def get_test_specifications_without_test_steps(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestSpecification]:
        """
        Get test specifications that have no test steps.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of test specifications without test steps
        """
        try:
            # Subquery to find test specifications with test steps
            subquery = select(TestSpecification.id).join(
                TestSpecification.test_steps
            ).where(TestSpecification.is_active == True).distinct()

            result = await db.execute(
                select(TestSpecification)
                .where(
                    and_(
                        TestSpecification.id.notin_(subquery),
                        TestSpecification.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(TestSpecification.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting test specifications without test steps: {str(e)}")
            raise

    async def add_requirement(
        self,
        db: AsyncSession,
        *,
        test_spec_id: str,
        requirement_id: str
    ) -> TestSpecification:
        """
        Add a requirement to a test specification.

        Args:
            db: Database session
            test_spec_id: Test specification ID
            requirement_id: Requirement ID to add

        Returns:
            Updated test specification

        Raises:
            NotFoundError: If test specification or requirement not found
        """
        try:
            # Get test specification with requirements
            test_spec = await self.get_with_requirements(db, id=test_spec_id)
            if not test_spec:
                raise NotFoundError(f"Test specification with ID {test_spec_id} not found")

            # Get requirement
            requirement = await db.execute(
                select(Requirement).where(
                    and_(
                        Requirement.id == requirement_id,
                        Requirement.is_active == True
                    )
                )
            )
            requirement = requirement.scalar_one_or_none()
            if not requirement:
                raise NotFoundError(f"Requirement with ID {requirement_id} not found")

            # Add requirement if not already present
            if requirement not in test_spec.requirements:
                test_spec.requirements.append(requirement)
                db.add(test_spec)
                await db.commit()
                await db.refresh(test_spec)

            return test_spec
        except NotFoundError:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error adding requirement {requirement_id} to test spec {test_spec_id}: {str(e)}")
            raise

    async def remove_requirement(
        self,
        db: AsyncSession,
        *,
        test_spec_id: str,
        requirement_id: str
    ) -> TestSpecification:
        """
        Remove a requirement from a test specification.

        Args:
            db: Database session
            test_spec_id: Test specification ID
            requirement_id: Requirement ID to remove

        Returns:
            Updated test specification

        Raises:
            NotFoundError: If test specification not found
        """
        try:
            # Get test specification with requirements
            test_spec = await self.get_with_requirements(db, id=test_spec_id)
            if not test_spec:
                raise NotFoundError(f"Test specification with ID {test_spec_id} not found")

            # Remove requirement if present
            requirement_to_remove = None
            for req in test_spec.requirements:
                if str(req.id) == requirement_id:
                    requirement_to_remove = req
                    break

            if requirement_to_remove:
                test_spec.requirements.remove(requirement_to_remove)
                db.add(test_spec)
                await db.commit()
                await db.refresh(test_spec)

            return test_spec
        except NotFoundError:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error removing requirement {requirement_id} from test spec {test_spec_id}: {str(e)}")
            raise


class CRUDTestStep(CRUDBase[TestStep, TestStepCreate, TestStepUpdate], AdvancedCRUDMixin, TransactionalCRUDMixin):
    """
    CRUD operations for TestStep entity.

    Extends BaseCRUD with test step-specific operations.
    """

    async def get_by_test_specification(
        self,
        db: AsyncSession,
        *,
        test_specification_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[TestStep]:
        """
        Get test steps by test specification ID.

        Args:
            db: Database session
            test_specification_id: Test specification ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of test steps for the specified test specification
        """
        try:
            result = await db.execute(
                select(TestStep)
                .where(
                    and_(
                        TestStep.test_specification_id == test_specification_id,
                        TestStep.is_active == True
                    )
                )
                .order_by(TestStep.sequence_number.asc())
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting test steps by test specification {test_specification_id}: {str(e)}")
            raise

    async def get_by_sequence_range(
        self,
        db: AsyncSession,
        *,
        test_specification_id: str,
        start_sequence: int,
        end_sequence: int
    ) -> List[TestStep]:
        """
        Get test steps by sequence number range.

        Args:
            db: Database session
            test_specification_id: Test specification ID
            start_sequence: Start sequence number (inclusive)
            end_sequence: End sequence number (inclusive)

        Returns:
            List of test steps in the sequence range
        """
        try:
            result = await db.execute(
                select(TestStep)
                .where(
                    and_(
                        TestStep.test_specification_id == test_specification_id,
                        TestStep.sequence_number >= start_sequence,
                        TestStep.sequence_number <= end_sequence,
                        TestStep.is_active == True
                    )
                )
                .order_by(TestStep.sequence_number.asc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting test steps by sequence range {start_sequence}-{end_sequence}: {str(e)}")
            raise

    async def get_next_sequence_number(
        self,
        db: AsyncSession,
        *,
        test_specification_id: str
    ) -> int:
        """
        Get the next sequence number for a test step in a test specification.

        Args:
            db: Database session
            test_specification_id: Test specification ID

        Returns:
            Next sequence number
        """
        try:
            result = await db.execute(
                select(func.max(TestStep.sequence_number))
                .where(
                    and_(
                        TestStep.test_specification_id == test_specification_id,
                        TestStep.is_active == True
                    )
                )
            )
            max_sequence = result.scalar()
            return (max_sequence or 0) + 1
        except Exception as e:
            logger.error(f"Error getting next sequence number for test spec {test_specification_id}: {str(e)}")
            raise

    async def reorder_sequence_numbers(
        self,
        db: AsyncSession,
        *,
        test_specification_id: str
    ) -> List[TestStep]:
        """
        Reorder sequence numbers for test steps in a test specification.

        Args:
            db: Database session
            test_specification_id: Test specification ID

        Returns:
            List of updated test steps
        """
        try:
            # Get all test steps for the test specification
            test_steps = await self.get_by_test_specification(
                db,
                test_specification_id=test_specification_id,
                skip=0,
                limit=1000  # Large limit to get all steps
            )

            # Update sequence numbers
            for i, step in enumerate(test_steps, 1):
                step.sequence_number = i
                db.add(step)

            await db.commit()

            # Refresh all steps
            for step in test_steps:
                await db.refresh(step)

            return test_steps
        except Exception as e:
            await db.rollback()
            logger.error(f"Error reordering sequence numbers for test spec {test_specification_id}: {str(e)}")
            raise

    async def delete_by_test_specification(
        self,
        db: AsyncSession,
        *,
        test_specification_id: str
    ) -> int:
        """
        Delete all test steps for a test specification.

        Args:
            db: Database session
            test_specification_id: Test specification ID

        Returns:
            Number of deleted test steps
        """
        try:
            # Get count before deletion
            count_result = await db.execute(
                select(func.count(TestStep.id))
                .where(
                    and_(
                        TestStep.test_specification_id == test_specification_id,
                        TestStep.is_active == True
                    )
                )
            )
            count = count_result.scalar()

            # Soft delete all test steps
            await db.execute(
                update(TestStep)
                .where(
                    and_(
                        TestStep.test_specification_id == test_specification_id,
                        TestStep.is_active == True
                    )
                )
                .values(is_active=False)
            )

            await db.commit()
            logger.info(f"Deleted {count} test steps for test specification {test_specification_id}")
            return count
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting test steps for test spec {test_specification_id}: {str(e)}")
            raise


# Create instances
test_specification = CRUDTestSpecification(TestSpecification)
test_step = CRUDTestStep(TestStep)
