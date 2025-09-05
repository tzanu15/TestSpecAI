"""
Custom validators and complex validation rules for TestSpecAI schemas.

This module provides custom validation functions and complex business rules
that can be used across different schema classes.
"""

import re
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID
from pydantic import ValidationError, field_validator, model_validator


class ValidationRules:
    """
    Collection of validation rules and helper methods for schema validation.
    """

    # Common validation patterns
    NAME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_\s-]*$')
    MANUFACTURER_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_\s-]*$')
    PARAMETER_PLACEHOLDER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    # Business rule constants
    MAX_REQUIREMENT_TITLE_LENGTH = 255
    MAX_DESCRIPTION_LENGTH = 10000
    MAX_TEMPLATE_LENGTH = 2000
    MAX_PARAMETER_VALUE_LENGTH = 500
    MAX_MANUFACTURER_NAME_LENGTH = 100

    @staticmethod
    def validate_name_format(name: str, field_name: str = "name") -> str:
        """
        Validate name format for categories, parameters, etc.

        Args:
            name: The name to validate
            field_name: Name of the field for error messages

        Returns:
            The validated and cleaned name

        Raises:
            ValueError: If name format is invalid
        """
        if not name or not name.strip():
            raise ValueError(f'{field_name} cannot be empty or only whitespace')

        cleaned_name = name.strip()

        if not ValidationRules.NAME_PATTERN.match(cleaned_name):
            raise ValueError(
                f'{field_name} must start with a letter and contain only '
                'letters, numbers, underscores, spaces, and hyphens'
            )

        if len(cleaned_name) > ValidationRules.MAX_REQUIREMENT_TITLE_LENGTH:
            raise ValueError(
                f'{field_name} cannot exceed {ValidationRules.MAX_REQUIREMENT_TITLE_LENGTH} characters'
            )

        return cleaned_name

    @staticmethod
    def validate_manufacturer_name(manufacturer: str) -> str:
        """
        Validate manufacturer name format.

        Args:
            manufacturer: The manufacturer name to validate

        Returns:
            The validated and cleaned manufacturer name

        Raises:
            ValueError: If manufacturer name format is invalid
        """
        if not manufacturer or not manufacturer.strip():
            raise ValueError('Manufacturer name cannot be empty or only whitespace')

        cleaned_manufacturer = manufacturer.strip()

        if not ValidationRules.MANUFACTURER_PATTERN.match(cleaned_manufacturer):
            raise ValueError(
                'Manufacturer name must start with a letter and contain only '
                'letters, numbers, underscores, spaces, and hyphens'
            )

        if len(cleaned_manufacturer) > ValidationRules.MAX_MANUFACTURER_NAME_LENGTH:
            raise ValueError(
                f'Manufacturer name cannot exceed {ValidationRules.MAX_MANUFACTURER_NAME_LENGTH} characters'
            )

        return cleaned_manufacturer

    @staticmethod
    def validate_parameter_placeholder(placeholder: str) -> str:
        """
        Validate parameter placeholder format in command templates.

        Args:
            placeholder: The parameter placeholder to validate

        Returns:
            The validated placeholder

        Raises:
            ValueError: If placeholder format is invalid
        """
        if not placeholder or not placeholder.strip():
            raise ValueError('Parameter placeholder cannot be empty')

        cleaned_placeholder = placeholder.strip()

        if not ValidationRules.PARAMETER_PLACEHOLDER_PATTERN.match(cleaned_placeholder):
            raise ValueError(
                'Parameter placeholder must start with a letter or underscore '
                'and contain only alphanumeric characters and underscores'
            )

        return cleaned_placeholder

    @staticmethod
    def validate_template_parameters(template: str) -> List[str]:
        """
        Extract and validate parameter placeholders from a command template.

        Args:
            template: The command template to validate

        Returns:
            List of valid parameter names found in the template

        Raises:
            ValueError: If template contains invalid parameter placeholders
        """
        if not template or not template.strip():
            raise ValueError('Template cannot be empty')

        # Find all parameter placeholders
        placeholders = re.findall(r'\{([^}]+)\}', template)

        if not placeholders:
            return []  # No parameters in template

        validated_placeholders = []
        for placeholder in placeholders:
            try:
                validated_placeholder = ValidationRules.validate_parameter_placeholder(placeholder)
                validated_placeholders.append(validated_placeholder)
            except ValueError as e:
                raise ValueError(f'Invalid parameter placeholder "{placeholder}": {str(e)}')

        # Check for duplicate placeholders
        if len(validated_placeholders) != len(set(validated_placeholders)):
            raise ValueError('Template contains duplicate parameter placeholders')

        return validated_placeholders

    @staticmethod
    def validate_parameter_value(value: str, parameter_name: str = "parameter") -> str:
        """
        Validate parameter value format and length.

        Args:
            value: The parameter value to validate
            parameter_name: Name of the parameter for error messages

        Returns:
            The validated and cleaned value

        Raises:
            ValueError: If value format is invalid
        """
        if not value or not value.strip():
            raise ValueError(f'{parameter_name} value cannot be empty or only whitespace')

        cleaned_value = value.strip()

        if len(cleaned_value) > ValidationRules.MAX_PARAMETER_VALUE_LENGTH:
            raise ValueError(
                f'{parameter_name} value cannot exceed {ValidationRules.MAX_PARAMETER_VALUE_LENGTH} characters'
            )

        return cleaned_value

    @staticmethod
    def validate_description_length(description: str, field_name: str = "description") -> str:
        """
        Validate description length and format.

        Args:
            description: The description to validate
            field_name: Name of the field for error messages

        Returns:
            The validated and cleaned description

        Raises:
            ValueError: If description format is invalid
        """
        if description is None:
            return None

        if not description or not description.strip():
            return None  # Convert empty descriptions to None

        cleaned_description = description.strip()

        if len(cleaned_description) > ValidationRules.MAX_DESCRIPTION_LENGTH:
            raise ValueError(
                f'{field_name} cannot exceed {ValidationRules.MAX_DESCRIPTION_LENGTH} characters'
            )

        return cleaned_description

    @staticmethod
    def validate_template_length(template: str) -> str:
        """
        Validate command template length.

        Args:
            template: The template to validate

        Returns:
            The validated template

        Raises:
            ValueError: If template is too long
        """
        if not template or not template.strip():
            raise ValueError('Template cannot be empty')

        if len(template) > ValidationRules.MAX_TEMPLATE_LENGTH:
            raise ValueError(
                f'Template cannot exceed {ValidationRules.MAX_TEMPLATE_LENGTH} characters'
            )

        return template.strip()

    @staticmethod
    def validate_unique_uuids(uuid_list: List[UUID], field_name: str = "IDs") -> List[UUID]:
        """
        Validate that a list of UUIDs contains no duplicates.

        Args:
            uuid_list: List of UUIDs to validate
            field_name: Name of the field for error messages

        Returns:
            List of unique UUIDs in original order

        Raises:
            ValueError: If list contains duplicate UUIDs
        """
        if not isinstance(uuid_list, list):
            raise ValueError(f'{field_name} must be a list')

        seen = set()
        unique_uuids = []

        for uuid_val in uuid_list:
            if uuid_val in seen:
                raise ValueError(f'{field_name} contains duplicate values')
            seen.add(uuid_val)
            unique_uuids.append(uuid_val)

        return unique_uuids

    @staticmethod
    def validate_sequence_numbers(sequence_numbers: List[int], field_name: str = "sequence numbers") -> List[int]:
        """
        Validate that sequence numbers are positive and unique.

        Args:
            sequence_numbers: List of sequence numbers to validate
            field_name: Name of the field for error messages

        Returns:
            List of validated sequence numbers

        Raises:
            ValueError: If sequence numbers are invalid
        """
        if not sequence_numbers:
            return []

        if not isinstance(sequence_numbers, list):
            raise ValueError(f'{field_name} must be a list')

        validated_numbers = []
        seen = set()

        for num in sequence_numbers:
            if not isinstance(num, int) or num < 1:
                raise ValueError(f'{field_name} must be positive integers')

            if num in seen:
                raise ValueError(f'{field_name} contains duplicate values')

            seen.add(num)
            validated_numbers.append(num)

        return validated_numbers


class BusinessRuleValidators:
    """
    Business rule validators for complex validation scenarios.
    """

    @staticmethod
    def validate_parameter_variants_consistency(
        has_variants: bool,
        default_value: Optional[str],
        variants: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Validate consistency between parameter variants and default value.

        Args:
            has_variants: Whether parameter has variants
            default_value: Default value for parameter
            variants: List of parameter variants

        Raises:
            ValueError: If variants and default value are inconsistent
        """
        if has_variants and default_value:
            raise ValueError('Parameters with variants should not have default values')

        if not has_variants and not default_value:
            raise ValueError('Parameters without variants must have a default value')

        if has_variants and variants and len(variants) == 0:
            raise ValueError('Parameters with variants must have at least one variant')

    @staticmethod
    def validate_command_template_parameters(
        template: str,
        required_parameter_ids: List[UUID],
        parameter_names: Optional[List[str]] = None
    ) -> None:
        """
        Validate that command template parameters match required parameters.

        Args:
            template: Command template string
            required_parameter_ids: List of required parameter IDs
            parameter_names: List of parameter names (optional, for enhanced validation)

        Raises:
            ValueError: If template parameters don't match required parameters
        """
        if not template:
            return

        # Extract parameter names from template
        template_params = ValidationRules.validate_template_parameters(template)

        if template_params and not required_parameter_ids:
            raise ValueError('Template contains parameters but no required parameters are specified')

        # If parameter names are provided, validate that template parameters exist
        if parameter_names and template_params:
            missing_params = set(template_params) - set(parameter_names)
            if missing_params:
                raise ValueError(f'Template references unknown parameters: {", ".join(missing_params)}')

    @staticmethod
    def validate_test_step_sequence_consistency(
        test_steps: List[Dict[str, Any]],
        test_specification_id: Optional[UUID] = None
    ) -> None:
        """
        Validate that test steps have consistent sequence numbers.

        Args:
            test_steps: List of test step data
            test_specification_id: ID of the test specification (optional)

        Raises:
            ValueError: If sequence numbers are inconsistent
        """
        if not test_steps:
            return

        sequence_numbers = [step.get('sequence_number') for step in test_steps if 'sequence_number' in step]

        if not sequence_numbers:
            return

        # Validate sequence numbers
        ValidationRules.validate_sequence_numbers(sequence_numbers, "test step sequence numbers")

        # Check for gaps in sequence (optional business rule)
        min_seq = min(sequence_numbers)
        max_seq = max(sequence_numbers)
        expected_sequences = set(range(min_seq, max_seq + 1))
        actual_sequences = set(sequence_numbers)

        if expected_sequences != actual_sequences:
            missing = expected_sequences - actual_sequences
            raise ValueError(f'Test step sequence numbers have gaps: missing {sorted(missing)}')

    @staticmethod
    def validate_requirement_test_spec_relationship(
        requirement_ids: List[UUID],
        test_specification_id: Optional[UUID] = None
    ) -> None:
        """
        Validate relationship between requirements and test specifications.

        Args:
            requirement_ids: List of requirement IDs
            test_specification_id: ID of the test specification (optional)

        Raises:
            ValueError: If relationship is invalid
        """
        if not requirement_ids:
            raise ValueError('Test specification must address at least one requirement')

        # Validate unique requirement IDs
        ValidationRules.validate_unique_uuids(requirement_ids, "requirement IDs")

    @staticmethod
    def validate_manufacturer_variant_uniqueness(
        variants: List[Dict[str, Any]],
        parameter_id: Optional[UUID] = None
    ) -> None:
        """
        Validate that parameter variants have unique manufacturers.

        Args:
            variants: List of parameter variant data
            parameter_id: ID of the parameter (optional)

        Raises:
            ValueError: If manufacturers are not unique
        """
        if not variants:
            return

        manufacturers = [variant.get('manufacturer') for variant in variants if 'manufacturer' in variant]

        if len(manufacturers) != len(set(manufacturers)):
            raise ValueError('Parameter variants must have unique manufacturers')

    @staticmethod
    def validate_functional_area_consistency(
        functional_area: str,
        requirement_categories: Optional[List[str]] = None
    ) -> None:
        """
        Validate that functional area is consistent with requirement categories.

        Args:
            functional_area: Functional area of the test specification
            requirement_categories: List of requirement category names (optional)

        Raises:
            ValueError: If functional area is inconsistent
        """
        if not functional_area:
            raise ValueError('Functional area is required')

        valid_areas = ["UDS", "Communication", "ErrorHandler", "CyberSecurity"]
        if functional_area not in valid_areas:
            raise ValueError(f'Functional area must be one of: {", ".join(valid_areas)}')

        # Additional business rules can be added here based on requirement categories
        if requirement_categories:
            # Example: UDS test specs should primarily address UDS requirements
            if functional_area == "UDS":
                uds_categories = [cat for cat in requirement_categories if "UDS" in cat.upper()]
                if not uds_categories:
                    # This is a warning, not an error - could be logged instead
                    pass


class CrossEntityValidators:
    """
    Validators for cross-entity relationships and constraints.
    """

    @staticmethod
    def validate_parameter_command_compatibility(
        parameter_id: UUID,
        command_id: UUID,
        parameter_name: str,
        command_template: str
    ) -> None:
        """
        Validate that a parameter is compatible with a command.

        Args:
            parameter_id: ID of the parameter
            command_id: ID of the command
            parameter_name: Name of the parameter
            command_template: Template of the command

        Raises:
            ValueError: If parameter and command are incompatible
        """
        # Extract parameter names from command template
        template_params = ValidationRules.validate_template_parameters(command_template)

        if parameter_name not in template_params:
            raise ValueError(f'Parameter "{parameter_name}" is not used in command template')

    @staticmethod
    def validate_test_step_command_references(
        action_command_id: UUID,
        expected_result_command_id: UUID,
        action_template: str,
        expected_result_template: str
    ) -> None:
        """
        Validate that test step action and expected result use different commands.

        Args:
            action_command_id: ID of the action command
            expected_result_command_id: ID of the expected result command
            action_template: Template of the action command
            expected_result_template: Template of the expected result command

        Raises:
            ValueError: If action and expected result use the same command
        """
        if action_command_id == expected_result_command_id:
            raise ValueError('Action and expected result cannot use the same command')

        # Additional validation: ensure templates are different
        if action_template == expected_result_template:
            raise ValueError('Action and expected result templates cannot be identical')

    @staticmethod
    def validate_category_entity_consistency(
        category_type: str,
        entity_type: str,
        category_name: str,
        entity_name: str
    ) -> None:
        """
        Validate consistency between category and entity types.

        Args:
            category_type: Type of category (requirement, parameter, command)
            entity_type: Type of entity (requirement, parameter, command)
            category_name: Name of the category
            entity_name: Name of the entity

        Raises:
            ValueError: If category and entity types are inconsistent
        """
        if category_type != entity_type:
            raise ValueError(f'{entity_type} cannot belong to {category_type} category')

        # Additional business rules based on naming conventions
        if category_type == "parameter" and entity_type == "parameter":
            # Example: Authentication parameters should be in Authentication category
            if "authentication" in entity_name.lower() and "authentication" not in category_name.lower():
                # This could be a warning rather than an error
                pass
