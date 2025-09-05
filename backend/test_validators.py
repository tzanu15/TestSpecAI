"""
Test script for custom validators and complex validation rules.

This script demonstrates the usage of custom validators and validates
that the validation rules work correctly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.schemas.validators import ValidationRules, BusinessRuleValidators, CrossEntityValidators
from uuid import uuid4


def test_validation_rules():
    """Test basic validation rules."""
    print("Testing ValidationRules...")

    # Test name format validation
    try:
        valid_name = ValidationRules.validate_name_format("Test Parameter", "parameter name")
        print(f"✓ Valid name: {valid_name}")
    except ValueError as e:
        print(f"✗ Name validation failed: {e}")

    try:
        invalid_name = ValidationRules.validate_name_format("123Invalid", "parameter name")
        print(f"✗ Invalid name should have failed: {invalid_name}")
    except ValueError as e:
        print(f"✓ Invalid name correctly rejected: {e}")

    # Test manufacturer name validation
    try:
        valid_manufacturer = ValidationRules.validate_manufacturer_name("BMW")
        print(f"✓ Valid manufacturer: {valid_manufacturer}")
    except ValueError as e:
        print(f"✗ Manufacturer validation failed: {e}")

    # Test parameter placeholder validation
    try:
        valid_placeholder = ValidationRules.validate_parameter_placeholder("Authentication")
        print(f"✓ Valid placeholder: {valid_placeholder}")
    except ValueError as e:
        print(f"✗ Placeholder validation failed: {e}")

    # Test template parameter extraction
    try:
        template = "Set level of authentication {Authentication} and read {DTC_Code}"
        params = ValidationRules.validate_template_parameters(template)
        print(f"✓ Template parameters extracted: {params}")
    except ValueError as e:
        print(f"✗ Template validation failed: {e}")

    # Test UUID uniqueness validation
    try:
        uuids = [uuid4(), uuid4(), uuid4()]
        unique_uuids = ValidationRules.validate_unique_uuids(uuids, "test IDs")
        print(f"✓ Unique UUIDs validated: {len(unique_uuids)} items")
    except ValueError as e:
        print(f"✗ UUID validation failed: {e}")

    # Test sequence number validation
    try:
        sequences = [1, 2, 3, 4, 5]
        valid_sequences = ValidationRules.validate_sequence_numbers(sequences, "test sequences")
        print(f"✓ Sequence numbers validated: {valid_sequences}")
    except ValueError as e:
        print(f"✗ Sequence validation failed: {e}")


def test_business_rule_validators():
    """Test business rule validators."""
    print("\nTesting BusinessRuleValidators...")

    # Test parameter variants consistency
    try:
        BusinessRuleValidators.validate_parameter_variants_consistency(
            has_variants=True,
            default_value=None,
            variants=[{"manufacturer": "BMW", "value": "Level 3"}]
        )
        print("✓ Parameter variants consistency validated")
    except ValueError as e:
        print(f"✗ Parameter variants validation failed: {e}")

    try:
        BusinessRuleValidators.validate_parameter_variants_consistency(
            has_variants=True,
            default_value="Level 1",  # This should fail
            variants=[]
        )
        print("✗ Inconsistent variants should have failed")
    except ValueError as e:
        print(f"✓ Inconsistent variants correctly rejected: {e}")

    # Test command template parameters
    try:
        BusinessRuleValidators.validate_command_template_parameters(
            template="Set level of authentication {Authentication}",
            required_parameter_ids=[uuid4()],
            parameter_names=["Authentication"]
        )
        print("✓ Command template parameters validated")
    except ValueError as e:
        print(f"✗ Command template validation failed: {e}")

    # Test test step sequence consistency
    try:
        test_steps = [
            {"sequence_number": 1, "description": "Step 1"},
            {"sequence_number": 2, "description": "Step 2"},
            {"sequence_number": 3, "description": "Step 3"}
        ]
        BusinessRuleValidators.validate_test_step_sequence_consistency(test_steps)
        print("✓ Test step sequence consistency validated")
    except ValueError as e:
        print(f"✗ Test step sequence validation failed: {e}")

    # Test requirement test spec relationship
    try:
        BusinessRuleValidators.validate_requirement_test_spec_relationship(
            requirement_ids=[uuid4(), uuid4()]
        )
        print("✓ Requirement test spec relationship validated")
    except ValueError as e:
        print(f"✗ Requirement test spec validation failed: {e}")

    # Test manufacturer variant uniqueness
    try:
        variants = [
            {"manufacturer": "BMW", "value": "Level 3"},
            {"manufacturer": "VW", "value": "Level 2"},
            {"manufacturer": "Audi", "value": "Level 4"}
        ]
        BusinessRuleValidators.validate_manufacturer_variant_uniqueness(variants)
        print("✓ Manufacturer variant uniqueness validated")
    except ValueError as e:
        print(f"✗ Manufacturer variant validation failed: {e}")

    # Test functional area consistency
    try:
        BusinessRuleValidators.validate_functional_area_consistency(
            functional_area="UDS",
            requirement_categories=["UDS Requirements", "Diagnostic Requirements"]
        )
        print("✓ Functional area consistency validated")
    except ValueError as e:
        print(f"✗ Functional area validation failed: {e}")


def test_cross_entity_validators():
    """Test cross-entity validators."""
    print("\nTesting CrossEntityValidators...")

    # Test parameter command compatibility
    try:
        CrossEntityValidators.validate_parameter_command_compatibility(
            parameter_id=uuid4(),
            command_id=uuid4(),
            parameter_name="Authentication",
            command_template="Set level of authentication {Authentication}"
        )
        print("✓ Parameter command compatibility validated")
    except ValueError as e:
        print(f"✗ Parameter command validation failed: {e}")

    try:
        CrossEntityValidators.validate_parameter_command_compatibility(
            parameter_id=uuid4(),
            command_id=uuid4(),
            parameter_name="DTC_Code",  # Not in template
            command_template="Set level of authentication {Authentication}"
        )
        print("✗ Incompatible parameter should have failed")
    except ValueError as e:
        print(f"✓ Incompatible parameter correctly rejected: {e}")

    # Test test step command references
    try:
        action_cmd_id = uuid4()
        result_cmd_id = uuid4()
        CrossEntityValidators.validate_test_step_command_references(
            action_command_id=action_cmd_id,
            expected_result_command_id=result_cmd_id,
            action_template="Set level of authentication {Authentication}",
            expected_result_template="Read authentication status {Status}"
        )
        print("✓ Test step command references validated")
    except ValueError as e:
        print(f"✗ Test step command validation failed: {e}")

    try:
        same_cmd_id = uuid4()
        CrossEntityValidators.validate_test_step_command_references(
            action_command_id=same_cmd_id,
            expected_result_command_id=same_cmd_id,  # Same command
            action_template="Set level of authentication {Authentication}",
            expected_result_template="Set level of authentication {Authentication}"
        )
        print("✗ Same command should have failed")
    except ValueError as e:
        print(f"✓ Same command correctly rejected: {e}")

    # Test category entity consistency
    try:
        CrossEntityValidators.validate_category_entity_consistency(
            category_type="parameter",
            entity_type="parameter",
            category_name="Authentication",
            entity_name="Authentication Level"
        )
        print("✓ Category entity consistency validated")
    except ValueError as e:
        print(f"✗ Category entity validation failed: {e}")


def main():
    """Run all validator tests."""
    print("=" * 60)
    print("TestSpecAI Custom Validators Test Suite")
    print("=" * 60)

    test_validation_rules()
    test_business_rule_validators()
    test_cross_entity_validators()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
