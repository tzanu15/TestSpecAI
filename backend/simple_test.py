#!/usr/bin/env python3
"""
Simple test script for database models.
"""

import asyncio
from app.database import get_db
from app.models import (
    RequirementCategory, ParameterCategory, CommandCategory,
    Requirement, Parameter, ParameterVariant, GenericCommand,
    TestSpecification, TestStep, FunctionalArea
)

async def simple_test():
    """Simple test of database models."""
    print("🚀 Starting simple model test...")

    async for session in get_db():
        try:
            # Create a simple category
            category = RequirementCategory(
                name="Test Category",
                description="Test category for simple test",
                created_by="test-user"
            )
            session.add(category)
            await session.commit()
            await session.refresh(category)

            print(f"✅ Category created: {category.name} (ID: {category.id})")

            # Create a simple requirement
            requirement = Requirement(
                title="Test Requirement",
                description="Simple test requirement",
                category_id=category.id,
                created_by="test-user"
            )
            session.add(requirement)
            await session.commit()
            await session.refresh(requirement)

            print(f"✅ Requirement created: {requirement.title} (ID: {requirement.id})")

            # Test basic properties
            print(f"✅ Requirement title length: {requirement.title_length}")
            print(f"✅ Requirement is manual source: {requirement.is_manual_source}")

            # Test serialization
            req_dict = requirement.to_dict()
            print(f"✅ Serialization works: {req_dict['title']}")

            # Test validation
            requirement.validate()
            print("✅ Validation works")

            print("🎉 Simple test completed successfully!")

        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
        finally:
            await session.close()
        break

if __name__ == "__main__":
    asyncio.run(simple_test())
