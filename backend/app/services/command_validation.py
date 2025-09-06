"""
Command template validation service.

This module provides validation logic for command templates and parameter references,
ensuring that command templates are syntactically correct and reference valid parameters.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.command import GenericCommand
from app.models.parameter import Parameter
from app.utils.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class CommandTemplateValidator:
    """
    Validator for command templates and parameter references.
    """

    def __init__(self):
        """Initialize the validator."""
        self.parameter_pattern = re.compile(r'\{([^}]+)\}')
        self.template_patterns = {
            'valid_chars': re.compile(r'^[a-zA-Z0-9\s\{\}\[\]\(\)\-\_\.\,\:\;\!\?\=\+\*\/\\\|\<\>\"\'`~@#$%^&]+$'),
            'balanced_braces': re.compile(r'^[^{}]*(\{[^{}]*\}[^{}]*)*$'),
            'no_nested_braces': re.compile(r'^[^{}]*(\{[^}]*\}[^{}]*)*$')
        }

    async def validate_template_syntax(
        self,
        template: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate the syntax of a command template.

        Args:
            template: Command template to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not template or not template.strip():
            errors.append("Template cannot be empty")
            return False, errors

        template = template.strip()

        # Check for valid characters
        if not self.template_patterns['valid_chars'].match(template):
            errors.append("Template contains invalid characters")

        # Check for balanced braces
        if not self.template_patterns['balanced_braces'].match(template):
            errors.append("Template has unbalanced braces")

        # Check for nested braces (not allowed)
        if not self.template_patterns['no_nested_braces'].match(template):
            errors.append("Template contains nested braces which are not allowed")

        # Check for empty parameter names
        empty_params = re.findall(r'\{\s*\}', template)
        if empty_params:
            errors.append(f"Template contains {len(empty_params)} empty parameter reference(s)")

        # Check for spaces in parameter names
        spaced_params = re.findall(r'\{\s+[^}]*\s+\}', template)
        if spaced_params:
            errors.append("Parameter names cannot contain leading or trailing spaces")

        return len(errors) == 0, errors

    async def extract_parameter_names(
        self,
        template: str
    ) -> List[str]:
        """
        Extract parameter names from a template.

        Args:
            template: Command template

        Returns:
            List of parameter names found in template
        """
        if not template:
            return []

        matches = self.parameter_pattern.findall(template)
        # Clean up parameter names (remove spaces)
        return [match.strip() for match in matches if match.strip()]

    async def validate_parameter_references(
        self,
        db: AsyncSession,
        *,
        template: str,
        required_parameters: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all parameter references in template exist in required_parameters.

        Args:
            db: Database session
            template: Command template to validate
            required_parameters: List of required parameter names

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Extract parameter names from template
        template_params = await self.extract_parameter_names(template)

        # Check for duplicate parameter references
        if len(template_params) != len(set(template_params)):
            duplicates = [param for param in set(template_params) if template_params.count(param) > 1]
            errors.append(f"Template contains duplicate parameter references: {', '.join(duplicates)}")

        # Check that all template parameters are in required_parameters
        missing_params = set(template_params) - set(required_parameters)
        if missing_params:
            errors.append(f"Template references parameters not in required_parameters: {', '.join(missing_params)}")

        # Check that all required_parameters are used in template
        unused_params = set(required_parameters) - set(template_params)
        if unused_params:
            errors.append(f"Required parameters not used in template: {', '.join(unused_params)}")

        return len(errors) == 0, errors

    async def validate_parameter_existence(
        self,
        db: AsyncSession,
        *,
        parameter_names: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all parameter names exist in the database.

        Args:
            db: Database session
            parameter_names: List of parameter names to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        if not parameter_names:
            return True, errors

        try:
            # Get all active parameters
            result = await db.execute(
                select(Parameter.name)
                .where(Parameter.is_active == True)
            )
            existing_params = {row[0] for row in result.fetchall()}

            # Check which parameters don't exist
            missing_params = set(parameter_names) - existing_params
            if missing_params:
                errors.append(f"Parameters do not exist in database: {', '.join(missing_params)}")

        except Exception as e:
            logger.error(f"Error validating parameter existence: {str(e)}")
            errors.append("Error validating parameter existence")

        return len(errors) == 0, errors

    async def validate_command_template(
        self,
        db: AsyncSession,
        *,
        template: str,
        required_parameters: List[str],
        command_id: Optional[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        Comprehensive validation of a command template.

        Args:
            db: Database session
            template: Command template to validate
            required_parameters: List of required parameter names
            command_id: Optional command ID for update operations

        Returns:
            Tuple of (is_valid, error_messages)
        """
        all_errors = []

        # Validate template syntax
        is_syntax_valid, syntax_errors = await self.validate_template_syntax(template)
        if not is_syntax_valid:
            all_errors.extend(syntax_errors)

        # Extract parameter names from template
        template_params = await self.extract_parameter_names(template)

        # Validate parameter references
        is_refs_valid, ref_errors = await self.validate_parameter_references(
            db, template=template, required_parameters=required_parameters
        )
        if not is_refs_valid:
            all_errors.extend(ref_errors)

        # Validate parameter existence in database
        if template_params:
            is_params_valid, param_errors = await self.validate_parameter_existence(
                db, parameter_names=template_params
            )
            if not is_params_valid:
                all_errors.extend(param_errors)

        return len(all_errors) == 0, all_errors

    async def validate_command_data(
        self,
        db: AsyncSession,
        *,
        template: str,
        required_parameters: List[str],
        category_id: str,
        command_id: Optional[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate complete command data including template and parameters.

        Args:
            db: Database session
            template: Command template
            required_parameters: List of required parameter names
            category_id: Command category ID
            command_id: Optional command ID for update operations

        Returns:
            Tuple of (is_valid, error_messages)
        """
        all_errors = []

        # Validate template
        is_template_valid, template_errors = await self.validate_command_template(
            db, template=template, required_parameters=required_parameters, command_id=command_id
        )
        if not is_template_valid:
            all_errors.extend(template_errors)

        # Validate required_parameters format
        if not isinstance(required_parameters, list):
            all_errors.append("Required parameters must be a list")

        # Validate parameter names format
        if isinstance(required_parameters, list):
            for param in required_parameters:
                if not isinstance(param, str) or not param.strip():
                    all_errors.append("All required parameters must be non-empty strings")
                    break

        return len(all_errors) == 0, all_errors

    def get_validation_summary(
        self,
        is_valid: bool,
        errors: List[str]
    ) -> Dict[str, Any]:
        """
        Get a summary of validation results.

        Args:
            is_valid: Whether validation passed
            errors: List of error messages

        Returns:
            Validation summary dictionary
        """
        return {
            "is_valid": is_valid,
            "error_count": len(errors),
            "errors": errors,
            "has_errors": len(errors) > 0
        }


# Global instance
command_template_validator = CommandTemplateValidator()
