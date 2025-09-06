#!/usr/bin/env python3
"""
Test script for requirements endpoints.
"""
import asyncio
import sys
from app.database import get_db
from app.crud.category import requirement_category
from app.crud.requirement import requirement

async def test_database():
    """Test database connections and basic operations."""
    try:
        async for db in get_db():
            # Test categories
            categories = await requirement_category.get_multi(db)
            print(f"Found {len(categories)} requirement categories")

            # Test requirements
            requirements = await requirement.get_multi(db)
            print(f"Found {len(requirements)} requirements")

            break
    except Exception as e:
        print(f"Error testing database: {e}")
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_database())
    sys.exit(0 if success else 1)
