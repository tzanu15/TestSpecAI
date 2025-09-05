#!/usr/bin/env python3
"""
Test script for database models.

This script tests the database models by creating sample data and verifying relationships.
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
import uuid

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.database import AsyncSessionLocal
from app.models import (
    RequirementCategory, ParameterCategory, CommandCategory,
    Requirement, Parameter, ParameterVariant, GenericCommand,
    TestSpecification, TestStep, FunctionalArea
)

async def test_models():
    """Test database models by creating sample data."""
    print("🧪 Testing database models...")

    async with AsyncSessionLocal() as session:
        try:
            # Create categories
            print("📁 Creating categories...")

            req_category = RequirementCategory(
                name="UDS Requirements",
                description="Requirements for UDS testing",
                created_by="test-user"
            )
            session.add(req_category)

            param_category = ParameterCategory(
                name="Authentication Parameters",
                description="Parameters for authentication testing",
                created_by="test-user"
            )
            session.add(param_category)

            cmd_category = CommandCategory(
                name="UDS Commands",
                description="Generic UDS commands",
                created_by="test-user"
            )
            session.add(cmd_category)

            await session.commit()
            print("✅ Categories created successfully")

            # Create parameters
            print("🔧 Creating parameters...")

            auth_param = Parameter(
                name="Authentication Level",
                category_id=param_category.id,
                has_variants=True,
                description="Authentication level parameter",
                created_by="test-user"
            )
            session.add(auth_param)
            await session.flush()  # Flush to get the ID

            # Create parameter variant
            auth_variant = ParameterVariant(
                parameter_id=auth_param.id,
                manufacturer="BMW",
                value="Level 1",
                description="BMW authentication level 1",
                created_by="test-user"
            )
            session.add(auth_variant)

            await session.commit()
            print("✅ Parameters created successfully")

            # Create generic command
            print("⚡ Creating generic command...")

            uds_command = GenericCommand(
                template="Set authentication level to {Authentication Level}",
                category_id=cmd_category.id,
                description="Set authentication level command",
                created_by="test-user"
            )
            session.add(uds_command)

            await session.commit()
            print("✅ Generic command created successfully")

            # Create requirement
            print("📋 Creating requirement...")

            requirement = Requirement(
                title="UDS Authentication Test",
                description="Test UDS authentication functionality",
                category_id=req_category.id,
                source="manual",
                metadata_json={"priority": "high", "complexity": "medium"},
                created_by="test-user"
            )
            session.add(requirement)

            await session.commit()
            print("✅ Requirement created successfully")

            # Create test specification
            print("🧪 Creating test specification...")

            test_spec = TestSpecification(
                name="UDS Authentication Test Specification",
                description="Comprehensive test specification for UDS authentication",
                precondition="System is in diagnostic mode",
                postcondition="Authentication level is set correctly",
                test_data_description={"auth_level": "Level 1"},
                functional_area=FunctionalArea.UDS,
                created_by="test-user"
            )
            session.add(test_spec)

            await session.commit()
            print("✅ Test specification created successfully")

            # Create test step
            print("📝 Creating test step...")

            test_step = TestStep(
                test_specification_id=test_spec.id,
                action={
                    "command_id": str(uds_command.id),
                    "populated_parameters": {"Authentication Level": "Level 1"}
                },
                expected_result={
                    "command_id": str(uds_command.id),
                    "populated_parameters": {"Authentication Level": "Level 1"}
                },
                description="Set authentication level to Level 1",
                sequence_number=1,
                created_by="test-user"
            )
            session.add(test_step)

            # Access all relationships before session closes to avoid lazy loading issues
            print("🔗 Testing relationships...")

            # Test requirement -> category
            req_category = requirement.category
            assert req_category.name == "UDS Requirements"
            print("✅ Requirement -> Category relationship works")

            # Test parameter -> category
            param_category = auth_param.category
            assert param_category.name == "Authentication Parameters"
            print("✅ Parameter -> Category relationship works")

            # Test parameter -> variant (access before session closes)
            variants = auth_param.variants
            assert variants[0].manufacturer == "BMW"
            print("✅ Parameter -> Variant relationship works")

            # Test command -> category
            cmd_category = uds_command.category
            assert cmd_category.name == "UDS Commands"
            print("✅ Command -> Category relationship works")

            # Test test spec -> test step (access before session closes)
            test_steps = test_spec.test_steps
            assert test_steps[0].sequence_number == 1
            print("✅ Test Specification -> Test Step relationship works")

            # Test test spec -> requirements
            assert len(test_spec.requirements) == 1
            assert test_spec.requirements[0].title == "UDS Authentication Test"
            print("✅ Test Specification -> Requirements relationship works")

            print("✅ All relationships work correctly!")

            # Test hybrid properties
            print("🔧 Testing hybrid properties...")

            # Test requirement hybrid properties
            assert requirement.title_length == len("UDS Authentication Test")
            assert requirement.description_length == len("Test UDS authentication functionality")
            assert requirement.is_manual_source == True
            assert requirement.is_document_source == False
            assert requirement.has_metadata == True
            assert requirement.category_name == "UDS Requirements"
            print("✅ Requirement hybrid properties work")

            # Test parameter hybrid properties
            assert auth_param.name_length == len("Authentication Level")
            assert auth_param.description_length == len("Authentication level parameter")
            assert auth_param.has_default_value == False
            assert auth_param.is_variant_parameter == True
            print("✅ Parameter hybrid properties work")

            # Test test spec hybrid properties
            assert test_spec.name_length == len("UDS Authentication Test Specification")
            assert test_spec.description_length == len("Comprehensive test specification for UDS authentication")
            assert test_spec.has_precondition == True
            assert test_spec.has_postcondition == True
            assert test_spec.has_test_data == True
            assert test_spec.test_steps_count == 1
            print("✅ Test Specification hybrid properties work")

            # Test test step hybrid properties
            test_step = test_spec.test_steps[0]
            assert test_step.has_description == True
            assert test_step.description_length == len("Test authentication level setting")
            assert test_step.action_parameters_count == 1
            assert test_step.expected_result_parameters_count == 1
            print("✅ Test Step hybrid properties work")

            print("✅ All hybrid properties work correctly!")

            # Test serialization
            print("📄 Testing serialization...")

            # Test requirement serialization
            req_dict = requirement.to_dict()
            assert req_dict['title'] == "UDS Authentication Test"
            assert req_dict['category_id'] == str(requirement.category_id)
            print("✅ Requirement serialization works")

            # Test parameter serialization
            param_dict = auth_param.to_dict()
            assert param_dict['name'] == "Authentication Level"
            assert param_dict['has_variants'] == True
            print("✅ Parameter serialization works")

            # Test test spec serialization
            spec_dict = test_spec.to_dict()
            assert spec_dict['name'] == "UDS Authentication Test Specification"
            assert spec_dict['functional_area'] == "UDS"
            print("✅ Test Specification serialization works")

            print("✅ All serialization works correctly!")

            # Test validation methods
            print("✅ Testing validation methods...")

            # Test requirement validation
            requirement.validate()
            print("✅ Requirement validation works")

            # Test parameter validation
            auth_param.validate()
            print("✅ Parameter validation works")

            # Test test spec validation
            test_spec.validate()
            print("✅ Test Specification validation works")

            print("✅ All validation methods work correctly!")

            print("🎉 All tests passed successfully!")

            await session.commit()
            print("✅ Test step created successfully")

            # Test hybrid properties
            print("🔍 Testing hybrid properties...")

            assert requirement.title_length > 0
            assert requirement.is_manual_source
            assert requirement.has_metadata
            print("✅ Requirement hybrid properties work")

            assert auth_param.name_length > 0
            assert auth_param.is_variant_parameter
            print("✅ Parameter hybrid properties work")

            assert uds_command.template_length > 0
            assert uds_command.parameter_count == 1
            print("✅ Generic Command hybrid properties work")

            assert test_spec.name_length > 0
            assert test_spec.has_precondition
            assert test_spec.has_postcondition
            print("✅ Test Specification hybrid properties work")

            assert test_step.has_description
            assert test_step.action_parameters_count == 1
            print("✅ Test Step hybrid properties work")

            # Test serialization
            print("📄 Testing serialization...")

            req_dict = requirement.to_dict()
            assert "id" in req_dict
            assert "title" in req_dict
            print("✅ Model serialization works")

            req_json = requirement.to_json()
            assert isinstance(req_json, str)
            print("✅ Model JSON serialization works")

            print("🎉 All tests passed successfully!")

        except Exception as e:
            print(f"❌ Test failed: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def main():
    """Main function."""
    print("🚀 Starting model tests...")
    await test_models()
    print("✨ Model tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
