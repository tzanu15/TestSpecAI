"""
CRUD operations for GenericCommand entity.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from app.crud.base import CRUDBase
from app.crud.advanced_queries import AdvancedCRUDMixin
from app.crud.transaction_manager import TransactionalCRUDMixin
from app.models.command import GenericCommand
from app.models.category import CommandCategory
from app.models.parameter import Parameter
from app.schemas.command import GenericCommandCreate, GenericCommandUpdate
from app.utils.exceptions import NotFoundError, ValidationError, ConflictError
from app.services.command_validation import command_template_validator
import logging
import re

logger = logging.getLogger(__name__)


class CRUDGenericCommand(CRUDBase[GenericCommand, GenericCommandCreate, GenericCommandUpdate], AdvancedCRUDMixin, TransactionalCRUDMixin):
    """
    CRUD operations for GenericCommand entity.

    Extends BaseCRUD with generic command-specific operations.
    """

    async def get_by_category(
        self,
        db: AsyncSession,
        *,
        category_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[GenericCommand]:
        """
        Get generic commands by category ID.

        Args:
            db: Database session
            category_id: Category ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of commands in the specified category
        """
        try:
            result = await db.execute(
                select(GenericCommand)
                .where(
                    and_(
                        GenericCommand.category_id == category_id,
                        GenericCommand.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(GenericCommand.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting commands by category {category_id}: {str(e)}")
            raise

    async def search_by_template(
        self,
        db: AsyncSession,
        *,
        template: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[GenericCommand]:
        """
        Search generic commands by template content (case-insensitive partial match).

        Args:
            db: Database session
            template: Template content to search for
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching commands
        """
        try:
            result = await db.execute(
                select(GenericCommand)
                .where(
                    and_(
                        GenericCommand.template.ilike(f"%{template}%"),
                        GenericCommand.is_active == True
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(GenericCommand.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching commands by template '{template}': {str(e)}")
            raise

    async def get_simple_commands(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[GenericCommand]:
        """
        Get commands that have no parameters (simple commands).

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of simple commands
        """
        try:
            result = await db.execute(
                select(GenericCommand)
                .where(
                    and_(
                        GenericCommand.is_active == True,
                        ~GenericCommand.template.contains('{')
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(GenericCommand.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting simple commands: {str(e)}")
            raise

    async def get_parameterized_commands(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[GenericCommand]:
        """
        Get commands that have parameters.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of parameterized commands
        """
        try:
            result = await db.execute(
                select(GenericCommand)
                .where(
                    and_(
                        GenericCommand.is_active == True,
                        GenericCommand.template.contains('{')
                    )
                )
                .offset(skip)
                .limit(limit)
                .order_by(GenericCommand.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting parameterized commands: {str(e)}")
            raise

    async def get_with_category(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[GenericCommand]:
        """
        Get command with category relationship loaded.

        Args:
            db: Database session
            id: Command ID

        Returns:
            Command with category loaded or None if not found
        """
        try:
            result = await db.execute(
                select(GenericCommand)
                .options(selectinload(GenericCommand.category))
                .where(
                    and_(
                        GenericCommand.id == id,
                        GenericCommand.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting command with category {id}: {str(e)}")
            raise

    async def get_with_required_parameters(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[GenericCommand]:
        """
        Get command with required parameters relationship loaded.

        Args:
            db: Database session
            id: Command ID

        Returns:
            Command with required parameters loaded or None if not found
        """
        try:
            result = await db.execute(
                select(GenericCommand)
                .options(selectinload(GenericCommand.required_parameters))
                .where(
                    and_(
                        GenericCommand.id == id,
                        GenericCommand.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting command with required parameters {id}: {str(e)}")
            raise

    async def get_with_all_relationships(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> Optional[GenericCommand]:
        """
        Get command with all relationships loaded.

        Args:
            db: Database session
            id: Command ID

        Returns:
            Command with all relationships loaded or None if not found
        """
        try:
            result = await db.execute(
                select(GenericCommand)
                .options(
                    selectinload(GenericCommand.category),
                    selectinload(GenericCommand.required_parameters)
                )
                .where(
                    and_(
                        GenericCommand.id == id,
                        GenericCommand.is_active == True
                    )
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting command with all relationships {id}: {str(e)}")
            raise

    async def count_by_category(
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
            logger.error(f"Error counting commands by category {category_id}: {str(e)}")
            raise

    async def get_commands_by_parameter_count(
        self,
        db: AsyncSession,
        *,
        min_params: int = 0,
        max_params: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[GenericCommand]:
        """
        Get commands by parameter count range.

        Args:
            db: Database session
            min_params: Minimum number of parameters
            max_params: Maximum number of parameters (None for no limit)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of commands matching the parameter count criteria
        """
        try:
            # Get all commands and filter by parameter count
            all_commands = await self.get_multi(db, skip=0, limit=1000)  # Get all for filtering

            filtered_commands = []
            for command in all_commands:
                param_count = self._count_template_parameters(command.template)
                if param_count >= min_params:
                    if max_params is None or param_count <= max_params:
                        filtered_commands.append(command)

            # Apply pagination
            return filtered_commands[skip:skip + limit]
        except Exception as e:
            logger.error(f"Error getting commands by parameter count {min_params}-{max_params}: {str(e)}")
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
                select(func.count(CommandCategory.id))
                .where(
                    and_(
                        CommandCategory.id == category_id,
                        CommandCategory.is_active == True
                    )
                )
            )
            return result.scalar() > 0
        except Exception as e:
            logger.error(f"Error validating category {category_id}: {str(e)}")
            raise

    async def validate_template_parameters(
        self,
        db: AsyncSession,
        *,
        template: str,
        required_parameter_ids: List[str]
    ) -> bool:
        """
        Validate that all parameters referenced in template exist.

        Args:
            db: Database session
            template: Command template
            required_parameter_ids: List of parameter IDs that should be required

        Returns:
            True if all parameters exist, False otherwise
        """
        try:
            # Extract parameter names from template
            param_names = re.findall(r'\{([^}]+)\}', template)

            # Check if all required parameters exist
            for param_id in required_parameter_ids:
                result = await db.execute(
                    select(func.count(Parameter.id))
                    .where(
                        and_(
                            Parameter.id == param_id,
                            Parameter.is_active == True
                        )
                    )
                )
                if result.scalar() == 0:
                    return False

            return True
        except Exception as e:
            logger.error(f"Error validating template parameters: {str(e)}")
            raise

    async def add_required_parameter(
        self,
        db: AsyncSession,
        *,
        command_id: str,
        parameter_id: str
    ) -> GenericCommand:
        """
        Add a required parameter to a command.

        Args:
            db: Database session
            command_id: Command ID
            parameter_id: Parameter ID to add

        Returns:
            Updated command

        Raises:
            NotFoundError: If command or parameter not found
        """
        try:
            # Get command with required parameters
            command = await self.get_with_required_parameters(db, id=command_id)
            if not command:
                raise NotFoundError(f"Command with ID {command_id} not found")

            # Get parameter
            parameter = await db.execute(
                select(Parameter).where(
                    and_(
                        Parameter.id == parameter_id,
                        Parameter.is_active == True
                    )
                )
            )
            parameter = parameter.scalar_one_or_none()
            if not parameter:
                raise NotFoundError(f"Parameter with ID {parameter_id} not found")

            # Add parameter if not already present
            if parameter not in command.required_parameters:
                command.required_parameters.append(parameter)
                db.add(command)
                await db.commit()
                await db.refresh(command)

            return command
        except NotFoundError:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error adding parameter {parameter_id} to command {command_id}: {str(e)}")
            raise

    async def remove_required_parameter(
        self,
        db: AsyncSession,
        *,
        command_id: str,
        parameter_id: str
    ) -> GenericCommand:
        """
        Remove a required parameter from a command.

        Args:
            db: Database session
            command_id: Command ID
            parameter_id: Parameter ID to remove

        Returns:
            Updated command

        Raises:
            NotFoundError: If command not found
        """
        try:
            # Get command with required parameters
            command = await self.get_with_required_parameters(db, id=command_id)
            if not command:
                raise NotFoundError(f"Command with ID {command_id} not found")

            # Remove parameter if present
            parameter_to_remove = None
            for param in command.required_parameters:
                if str(param.id) == parameter_id:
                    parameter_to_remove = param
                    break

            if parameter_to_remove:
                command.required_parameters.remove(parameter_to_remove)
                db.add(command)
                await db.commit()
                await db.refresh(command)

            return command
        except NotFoundError:
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Error removing parameter {parameter_id} from command {command_id}: {str(e)}")
            raise

    async def create_with_validation(
        self,
        db: AsyncSession,
        *,
        obj_in: GenericCommandCreate
    ) -> GenericCommand:
        """
        Create a command with validation.

        Args:
            db: Database session
            obj_in: Command data to create

        Returns:
            Created command

        Raises:
            ValidationError: If validation fails
        """
        # Validate command data using the validation service
        is_valid, errors = await command_template_validator.validate_command_data(
            db,
            template=obj_in.template,
            required_parameters=obj_in.required_parameters,
            category_id=str(obj_in.category_id)
        )

        if not is_valid:
            raise ValidationError(f"Command validation failed: {'; '.join(errors)}")

        # Validate category exists
        if not await self.validate_category_exists(db, category_id=str(obj_in.category_id)):
            raise ValidationError(f"Category with ID {obj_in.category_id} does not exist")

        # Create the command
        command = await self.create(db, obj_in=obj_in)

        # Add required parameters if specified
        if hasattr(obj_in, 'required_parameter_ids') and obj_in.required_parameter_ids:
            for param_id in obj_in.required_parameter_ids:
                await self.add_required_parameter(db, command_id=str(command.id), parameter_id=param_id)

        return command

    async def update_with_validation(
        self,
        db: AsyncSession,
        *,
        db_obj: GenericCommand,
        obj_in: GenericCommandUpdate
    ) -> GenericCommand:
        """
        Update a command with validation.

        Args:
            db: Database session
            db_obj: Existing command
            obj_in: Update data

        Returns:
            Updated command

        Raises:
            ValidationError: If validation fails
        """
        # Validate category exists if being changed
        if obj_in.category_id and str(obj_in.category_id) != str(db_obj.category_id):
            if not await self.validate_category_exists(db, category_id=str(obj_in.category_id)):
                raise ValidationError(f"Category with ID {obj_in.category_id} does not exist")

        # Validate template and parameters if being changed
        if obj_in.template and obj_in.template != db_obj.template:
            # Use the validation service for comprehensive validation
            is_valid, errors = await command_template_validator.validate_command_template(
                db,
                template=obj_in.template,
                required_parameters=obj_in.required_parameters or db_obj.required_parameters,
                command_id=str(db_obj.id)
            )

            if not is_valid:
                raise ValidationError(f"Command validation failed: {'; '.join(errors)}")

        return await self.update(db, db_obj=db_obj, obj_in=obj_in)

    def _count_template_parameters(self, template: str) -> int:
        """
        Count the number of parameters in a template.

        Args:
            template: Command template

        Returns:
            Number of parameters in the template
        """
        if not template:
            return 0
        return len(re.findall(r'\{([^}]+)\}', template))

    def _validate_template_format(self, template: str) -> bool:
        """
        Validate template format.

        Args:
            template: Command template to validate

        Returns:
            True if template format is valid, False otherwise
        """
        if not template or not template.strip():
            return False

        # Check for balanced braces
        open_braces = template.count('{')
        close_braces = template.count('}')

        if open_braces != close_braces:
            return False

        # Check for valid parameter placeholders
        param_names = re.findall(r'\{([^}]+)\}', template)
        for param_name in param_names:
            if not param_name.strip():
                return False

        return True

    def extract_parameter_names(self, template: str) -> List[str]:
        """
        Extract parameter names from template.

        Args:
            template: Command template

        Returns:
            List of parameter names found in template
        """
        if not template:
            return []
        return re.findall(r'\{([^}]+)\}', template)

    async def is_command_in_use(
        self,
        db: AsyncSession,
        *,
        command_id: str
    ) -> bool:
        """
        Check if a command is in use by any test steps.

        Args:
            db: Database session
            command_id: Command ID to check

        Returns:
            True if command is in use, False otherwise
        """
        try:
            from app.models.test_spec import TestStep

            # Check if command is used in any test step actions or expected results
            result = await db.execute(
                select(func.count(TestStep.id))
                .where(
                    and_(
                        TestStep.is_active == True,
                        or_(
                            TestStep.action.contains({"command_id": command_id}),
                            TestStep.expected_result.contains({"command_id": command_id})
                        )
                    )
                )
            )
            return result.scalar() > 0
        except Exception as e:
            logger.error(f"Error checking if command {command_id} is in use: {str(e)}")
            raise

    async def get_command_usage_count(
        self,
        db: AsyncSession,
        *,
        command_id: str
    ) -> int:
        """
        Get the number of test steps using this command.

        Args:
            db: Database session
            command_id: Command ID to check

        Returns:
            Number of test steps using this command
        """
        try:
            from app.models.test_spec import TestStep

            result = await db.execute(
                select(func.count(TestStep.id))
                .where(
                    and_(
                        TestStep.is_active == True,
                        or_(
                            TestStep.action.contains({"command_id": command_id}),
                            TestStep.expected_result.contains({"command_id": command_id})
                        )
                    )
                )
            )
            return result.scalar()
        except Exception as e:
            logger.error(f"Error getting usage count for command {command_id}: {str(e)}")
            raise

    async def remove_with_validation(
        self,
        db: AsyncSession,
        *,
        id: str
    ) -> GenericCommand:
        """
        Remove a command with validation to prevent deletion of commands in use.

        Args:
            db: Database session
            id: Command ID to remove

        Returns:
            Removed command

        Raises:
            NotFoundError: If command not found
            ConflictError: If command is in use
        """
        try:
            # Check if command exists
            command = await self.get(db, id=id)
            if not command:
                raise NotFoundError(f"Command with ID {id} not found")

            # Check if command is in use
            if await self.is_command_in_use(db, command_id=id):
                usage_count = await self.get_command_usage_count(db, command_id=id)
                raise ConflictError(
                    f"Cannot delete command. It is currently used by {usage_count} test step(s). "
                    f"Please remove or update the test steps first."
                )

            # Remove the command
            return await self.remove(db, id=id)

        except (NotFoundError, ConflictError):
            raise
        except Exception as e:
            logger.error(f"Error removing command {id}: {str(e)}")
            raise


# Create instance
generic_command = CRUDGenericCommand(GenericCommand)
