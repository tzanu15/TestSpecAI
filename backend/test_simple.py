#!/usr/bin/env python3
"""
Simple test for API endpoints.
"""
import asyncio
from app.main import app
from app.database import get_db
from app.crud.requirement import requirement
from app.crud.category import requirement_category

async def test_endpoints():
    """Test endpoints directly."""
    try:
        # Test database connection
        async for db in get_db():
            # Test getting requirements
            requirements = await requirement.get_multi(db)
            print(f"Found {len(requirements)} requirements")

            # Test getting categories
            categories = await requirement_category.get_multi(db)
            print(f"Found {len(categories)} categories")

            if categories:
                print(f"First category: {categories[0].name}")

                # Test creating a requirement
                from app.schemas.requirement import RequirementCreate
                new_req = RequirementCreate(
                    title="Test Requirement",
                    description="This is a test requirement",
                    category_id=categories[0].id,
                    source="test",
                    created_by="test-user"
                )

                created_req = await requirement.create(db, obj_in=new_req)
                print(f"Created requirement: {created_req.title}")

                # Test getting the created requirement
                retrieved_req = await requirement.get(db, id=created_req.id)
                print(f"Retrieved requirement: {retrieved_req.title}")

                # Test updating the requirement
                from app.schemas.requirement import RequirementUpdate
                update_data = RequirementUpdate(
                    title="Updated Test Requirement",
                    description="This is an updated test requirement"
                )

                updated_req = await requirement.update(db, db_obj=retrieved_req, obj_in=update_data)
                print(f"Updated requirement: {updated_req.title}")

                # Test deleting the requirement
                await requirement.remove(db, id=created_req.id)
                print("Deleted requirement successfully")

            break

    except Exception as e:
        print(f"Error testing endpoints: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_endpoints())
